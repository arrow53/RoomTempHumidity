#ifndef ROOM_READING_H
#define ROOM_READING_H
#include <stddef.h>
#include <stdint.h>

#define ROOM_NODE_ID_LEN 16
#define ROOM_BOOT_ID_LEN 32
#define ROOM_JSON_CAPACITY 256
#define ROOM_MAX_SEQUENCE UINT64_C(9007199254740991)

struct room_reading {
	char node_id[ROOM_NODE_ID_LEN + 1];
	char boot_id[ROOM_BOOT_ID_LEN + 1];
	uint64_t sequence;
	uint64_t uptime_s;
	int32_t temperature_milli_c;
	int32_t humidity_milli_pct;
};

/* Normalize real driver results, including the SHT4x raw RH conversion range.
 * Invalid temperatures or impossible raw humidity return -ERANGE.
 */
int room_measurement_from_micro(int64_t temperature, int64_t humidity,
			       struct room_reading *out);
int room_reading_encode(const struct room_reading *r, char *out, size_t capacity);
#endif
