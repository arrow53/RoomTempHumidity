#include "reading.h"
#include <errno.h>
#include <inttypes.h>
#include <stdio.h>

static int32_t round_milli(int64_t value)
{
	return (int32_t)((value + (value >= 0 ? 500 : -500)) / 1000);
}

int room_measurement_from_micro(int64_t temperature, int64_t humidity,
			       struct room_reading *out)
{
	if (out == NULL) {
		return -EINVAL;
	}
	if (temperature < -INT64_C(40000000) || temperature > INT64_C(125000000) ||
	    humidity < -INT64_C(6000000) || humidity > INT64_C(119000000)) {
		return -ERANGE;
	}
	if (humidity < 0) {
		humidity = 0;
	} else if (humidity > INT64_C(100000000)) {
		humidity = INT64_C(100000000);
	}
	out->temperature_milli_c = round_milli(temperature);
	out->humidity_milli_pct = round_milli(humidity);
	return 0;
}

int room_reading_encode(const struct room_reading *r, char *out, size_t capacity)
{
	if (r == NULL || out == NULL || capacity == 0) {
		return -EINVAL;
	}
	for (size_t i = 0; i < ROOM_NODE_ID_LEN; ++i) {
		char c = r->node_id[i];
		if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) {
			return -EINVAL;
		}
	}
	for (size_t i = 0; i < ROOM_BOOT_ID_LEN; ++i) {
		char c = r->boot_id[i];
		if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) {
			return -EINVAL;
		}
	}
	if (r->node_id[ROOM_NODE_ID_LEN] != '\0' || r->boot_id[ROOM_BOOT_ID_LEN] != '\0' ||
	    r->sequence > ROOM_MAX_SEQUENCE ||
	    r->uptime_s > ROOM_MAX_SEQUENCE || r->temperature_milli_c < -40000 ||
	    r->temperature_milli_c > 125000 || r->humidity_milli_pct < 0 ||
	    r->humidity_milli_pct > 100000) {
		return -ERANGE;
	}
	int32_t t = r->temperature_milli_c;
	uint32_t abs_t = (uint32_t)(t < 0 ? -t : t);
	uint32_t h = (uint32_t)r->humidity_milli_pct;
	int n = snprintf(out, capacity,
		"{\"schema_version\":1,\"node_id\":\"%s\",\"boot_id\":\"%s\",\"sequence\":%" PRIu64
		",\"uptime_s\":%" PRIu64 ",\"temperature_c\":%s%u.%03u,"
		"\"humidity_pct\":%u.%03u}",
		r->node_id, r->boot_id, r->sequence, r->uptime_s, t < 0 ? "-" : "",
		(unsigned)(abs_t / 1000), (unsigned)(abs_t % 1000),
		(unsigned)(h / 1000), (unsigned)(h % 1000));
	if (n < 0 || (size_t)n >= capacity) {
		out[0] = '\0';
		return -ENOSPC;
	}
	return n;
}
