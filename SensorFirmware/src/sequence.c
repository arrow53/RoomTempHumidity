#include "sequence.h"
#include "reading.h"
#include <errno.h>
#include <stddef.h>

void room_sequence_init(struct room_sequence *state)
{
	state->next = 0;
}

int room_sequence_take(struct room_sequence *state, uint64_t *value)
{
	if (state == NULL || value == NULL) {
		return -EINVAL;
	}
	if (state->next > ROOM_MAX_SEQUENCE) {
		return -ERANGE;
	}
	*value = state->next++;
	return 0;
}
