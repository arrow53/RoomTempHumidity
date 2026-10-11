#ifndef ROOM_SEQUENCE_H
#define ROOM_SEQUENCE_H
#include <stdint.h>
struct room_sequence {
	uint64_t next;
};
void room_sequence_init(struct room_sequence *state);
int room_sequence_take(struct room_sequence *state, uint64_t *value);
#endif
