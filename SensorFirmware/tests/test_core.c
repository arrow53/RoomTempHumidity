#include "reading.h"
#include "boot_id.h"
#include "sequence.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>
#ifdef __ZEPHYR__
#include <zephyr/ztest.h>
#define CHECK(c) zassert_true((c), "%s", #c)
#else
#include <assert.h>
#define CHECK(c) assert(c)
#endif

/* Deterministic bytes are test fixtures only, never linked into firmware. */
static uint8_t fixture_offset;
static int fixture_random(void *buffer, size_t length)
{
	uint8_t *bytes = buffer;
	CHECK(length == 16);
	for (size_t i = 0; i < length; ++i) { bytes[i] = (uint8_t)i + fixture_offset; }
	return 0;
}
static int failed_random(void *buffer, size_t length)
{
	(void)buffer;
	(void)length;
	return -EIO;
}

static void test_measurements(void)
{
	struct room_reading r = {.node_id = "0123456789abcdef",
		.boot_id = "000102030405060708090a0b0c0d0e0f", .uptime_s = 60};
	char out[ROOM_JSON_CAPACITY];
	CHECK(room_measurement_from_micro(-500000, 46500000, &r) == 0);
	CHECK(r.temperature_milli_c == -500);
	CHECK(room_reading_encode(&r, out, sizeof(out)) > 0);
	CHECK(strstr(out, "\"temperature_c\":-0.500") != NULL);
	CHECK(strstr(out, "\"humidity_pct\":46.500") != NULL);
	CHECK(room_measurement_from_micro(-39999999, -6000000, &r) == 0);
	CHECK(r.temperature_milli_c == -40000 && r.humidity_milli_pct == 0);
	CHECK(room_measurement_from_micro(125000000, 119000000, &r) == 0);
	CHECK(r.temperature_milli_c == 125000 && r.humidity_milli_pct == 100000);
	CHECK(room_measurement_from_micro(125000001, 50000000, &r) == -ERANGE);
	CHECK(room_measurement_from_micro(-40000001, 50000000, &r) == -ERANGE);
	CHECK(room_measurement_from_micro(0, -6000001, &r) == -ERANGE);
	CHECK(room_measurement_from_micro(0, 119000001, &r) == -ERANGE);
	CHECK(room_measurement_from_micro(1499, 1000000, &r) == 0);
	CHECK(r.temperature_milli_c == 1);
	CHECK(room_measurement_from_micro(-1500, 1000000, &r) == 0);
	CHECK(r.temperature_milli_c == -2);
	CHECK(room_reading_encode(&r, out, 8) == -ENOSPC && out[0] == '\0');
	r.node_id[3] = '"';
	CHECK(room_reading_encode(&r, out, sizeof(out)) < 0);
	r.node_id[3] = '3';
	r.boot_id[0] = 'A';
	CHECK(room_reading_encode(&r, out, sizeof(out)) < 0);
	r.boot_id[0] = '0';
	r.boot_id[31] = '\0';
	CHECK(room_reading_encode(&r, out, sizeof(out)) < 0);
	r.boot_id[31] = 'f';
	r.sequence = ROOM_MAX_SEQUENCE;
	r.uptime_s = ROOM_MAX_SEQUENCE;
	CHECK(room_reading_encode(&r, out, sizeof(out)) > 0);
	r.sequence++;
	CHECK(room_reading_encode(&r, out, sizeof(out)) == -ERANGE);
}

static void test_boot_reboot_retry_and_failure(void)
{
	struct room_sequence seq;
	struct room_reading before = {.node_id = "0123456789abcdef", .uptime_s = 3600};
	struct room_reading after = {.node_id = "0123456789abcdef", .uptime_s = 1};
	char initial[ROOM_JSON_CAPACITY], retry[ROOM_JSON_CAPACITY], rebooted[ROOM_JSON_CAPACITY];
	fixture_offset = 0;
	CHECK(room_boot_id_generate(before.boot_id, fixture_random) == 0);
	CHECK(strcmp(before.boot_id, "000102030405060708090a0b0c0d0e0f") == 0);
	room_sequence_init(&seq);
	for (uint64_t i = 0; i < 1024; ++i) {
		CHECK(room_sequence_take(&seq, &before.sequence) == 0 && before.sequence == i);
	}
	CHECK(room_reading_encode(&before, initial, sizeof(initial)) > 0);
	CHECK(room_reading_encode(&before, retry, sizeof(retry)) > 0);
	CHECK(strcmp(initial, retry) == 0); /* Retry identity/body does not mutate. */
	fixture_offset = 16;
	CHECK(room_boot_id_generate(after.boot_id, fixture_random) == 0);
	CHECK(strcmp(before.boot_id, after.boot_id) != 0);
	room_sequence_init(&seq); /* New boot may reset sequence/uptime. */
	CHECK(room_sequence_take(&seq, &after.sequence) == 0 && after.sequence == 0);
	CHECK(room_reading_encode(&after, rebooted, sizeof(rebooted)) > 0);
	CHECK(strcmp(initial, rebooted) != 0);
	CHECK(strcmp(before.node_id, after.node_id) == 0);
	CHECK(room_boot_id_generate(after.boot_id, failed_random) == -EIO);
	CHECK(after.boot_id[0] == '\0'); /* Never substitute a fixed/fake ID. */
	CHECK(room_reading_encode(&after, rebooted, sizeof(rebooted)) < 0);
	seq.next = ROOM_MAX_SEQUENCE;
	uint64_t value;
	CHECK(room_sequence_take(&seq, &value) == 0 && value == ROOM_MAX_SEQUENCE);
	CHECK(room_sequence_take(&seq, &value) == -ERANGE);
}

#ifdef __ZEPHYR__
ZTEST(room_core, test_measurements) { test_measurements(); }
ZTEST(room_core, test_boot_reboot_retry_and_failure) { test_boot_reboot_retry_and_failure(); }
ZTEST_SUITE(room_core, NULL, NULL, NULL, NULL, NULL);
#else
int main(void)
{
	test_measurements();
	test_boot_reboot_retry_and_failure();
	struct room_reading r = {.node_id = "0123456789abcdef",
		.boot_id = "000102030405060708090a0b0c0d0e0f", .uptime_s = 60};
	char out[ROOM_JSON_CAPACITY];
	CHECK(room_measurement_from_micro(21375000, 46500000, &r) == 0);
	CHECK(room_reading_encode(&r, out, sizeof(out)) > 0);
	puts(out); /* Machine-readable actual firmware serializer output. */
	return 0;
}
#endif
