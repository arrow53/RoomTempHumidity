#ifndef ROOM_BOOT_ID_H
#define ROOM_BOOT_ID_H
#include "reading.h"
#include <stddef.h>

/* fill must return zero only after filling all bytes from a secure random source.
 * The hardware application passes Zephyr sys_csrand_get; deterministic providers
 * are used only in isolated unit tests. The boot ID is public, not a credential.
 */
typedef int (*room_random_fill_fn)(void *buffer, size_t length);
int room_boot_id_generate(char out[ROOM_BOOT_ID_LEN + 1], room_random_fill_fn fill);
#endif
