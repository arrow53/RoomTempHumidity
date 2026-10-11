#include "boot_id.h"
#include <errno.h>
#include <stdint.h>

int room_boot_id_generate(char out[ROOM_BOOT_ID_LEN + 1], room_random_fill_fn fill)
{
	uint8_t bytes[16];
	static const char hex[] = "0123456789abcdef";
	if (out == NULL || fill == NULL) {
		return -EINVAL;
	}
	out[0] = '\0';
	int rc = fill(bytes, sizeof(bytes));
	if (rc != 0) {
		return rc;
	}
	for (size_t i = 0; i < sizeof(bytes); ++i) {
		out[2 * i] = hex[bytes[i] >> 4];
		out[2 * i + 1] = hex[bytes[i] & 15];
	}
	out[ROOM_BOOT_ID_LEN] = '\0';
	return 0;
}
