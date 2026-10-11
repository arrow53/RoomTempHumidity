#ifndef ROOM_TRANSPORT_H
#define ROOM_TRANSPORT_H
#include <stdbool.h>
#include <stddef.h>
int room_network_init(void);
bool room_transport_ready(void);
int room_transport_send(const char *json, size_t length);
#endif
