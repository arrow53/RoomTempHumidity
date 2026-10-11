#include "reading.h"
#include "boot_id.h"
#include "sequence.h"
#include "transport.h"
#include <errno.h>
#include <zephyr/device.h>
#include <zephyr/drivers/hwinfo.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/random/random.h>

LOG_MODULE_REGISTER(room_sensor);
static const struct device *const sensor = DEVICE_DT_GET(DT_NODELABEL(room_sht40));

static int make_node_id(char out[ROOM_NODE_ID_LEN + 1])
{
	uint8_t id[8];
	static const char hex[] = "0123456789abcdef";
	ssize_t count = hwinfo_get_device_id(id, sizeof(id));
	if (count != sizeof(id)) {
		return -EIO;
	}
	for (size_t i = 0; i < sizeof(id); ++i) {
		out[2 * i] = hex[id[i] >> 4];
		out[2 * i + 1] = hex[id[i] & 15];
	}
	out[ROOM_NODE_ID_LEN] = '\0';
	return 0;
}

int main(void)
{
	struct room_reading reading = {0};
	struct room_sequence sequence;
	char json[ROOM_JSON_CAPACITY];
	int rc = make_node_id(reading.node_id);
	if (rc == 0) {
		rc = room_boot_id_generate(reading.boot_id, sys_csrand_get);
	}
	if (rc != 0) {
		LOG_ERR("Hardware/boot identity generation failed (%d); measurements disabled", rc);
		return rc;
	}
	room_sequence_init(&sequence);
	LOG_INF("Room sensor node %s; period %d s", reading.node_id, CONFIG_ROOM_SAMPLE_INTERVAL_S);
	rc = room_network_init();
	if (rc != 0) {
		return rc;
	}
	/* Deadline cadence prevents the measurement and send duration accumulating drift.
	 * There is no sensor simulation or stale-sample resend path here.
	 */
	int64_t next = k_uptime_get();
	while (true) {
		struct sensor_value temperature, humidity;
		next += (int64_t)CONFIG_ROOM_SAMPLE_INTERVAL_S * 1000;
		if (!device_is_ready(sensor)) {
			LOG_ERR("SHT40 not ready; check power/wiring then reboot");
			goto sleep_until_next;
		}
		rc = sensor_sample_fetch(sensor);
		if (rc == 0) {
			rc = sensor_channel_get(sensor, SENSOR_CHAN_AMBIENT_TEMP, &temperature);
		}
		if (rc == 0) {
			rc = sensor_channel_get(sensor, SENSOR_CHAN_HUMIDITY, &humidity);
		}
		if (rc != 0) {
			LOG_WRN("SHT40 read/CRC error %d; sample dropped", rc);
			goto sleep_until_next;
		}
		rc = room_measurement_from_micro((int64_t)temperature.val1 * 1000000 + temperature.val2,
			(int64_t)humidity.val1 * 1000000 + humidity.val2, &reading);
		if (rc != 0) {
			LOG_WRN("SHT40 measurement outside valid range; sample dropped");
			goto sleep_until_next;
		}
		reading.uptime_s = (uint64_t)k_uptime_get() / 1000;
		LOG_INF("Measured temperature=%d mdegC humidity=%d milli-percent",
			reading.temperature_milli_c, reading.humidity_milli_pct);
		if (!room_transport_ready()) {
			LOG_INF("Fresh sample dropped: not attached, no collector, or request pending");
			goto sleep_until_next;
		}
		rc = room_sequence_take(&sequence, &reading.sequence);
		if (rc != 0) {
			LOG_ERR("Boot sequence exhausted (%d); sample dropped", rc);
			goto sleep_until_next;
		}
		rc = room_reading_encode(&reading, json, sizeof(json));
		if (rc < 0) {
			LOG_ERR("Reading encode failed %d", rc);
		} else {
			rc = room_transport_send(json, (size_t)rc);
			if (rc != 0) {
				LOG_WRN("Reading not queued (%d)", rc);
			}
		}
sleep_until_next:
		if (next <= k_uptime_get()) {
			next = k_uptime_get() + (int64_t)CONFIG_ROOM_SAMPLE_INTERVAL_S * 1000;
		}
		k_sleep(K_TIMEOUT_ABS_MS(next));
	}
	return 0;
}
