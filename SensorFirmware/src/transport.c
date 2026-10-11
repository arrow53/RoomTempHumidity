#include "transport.h"
#include <errno.h>
#include <openthread.h>
#include <openthread/coap.h>
#include <openthread/dataset.h>
#include <openthread/ip6.h>
#include <openthread/thread.h>
#include <openthread/thread_ftd.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(room_transport);
static otInstance *instance;
static otIp6Address collector;
/* All accesses are under the OpenThread mutex; response callback already owns it. */
static bool pending;
static bool configured;
static const otCoapTxParameters tx_parameters = {
	.mAckTimeout = 2000,
	.mAckRandomFactorNumerator = 3,
	.mAckRandomFactorDenominator = 2,
	.mMaxRetransmit = 3,
};

static bool attached(void)
{
	otDeviceRole role = otThreadGetDeviceRole(instance);
	return role == OT_DEVICE_ROLE_CHILD || role == OT_DEVICE_ROLE_ROUTER ||
	       role == OT_DEVICE_ROLE_LEADER;
}

static void response(void *context, otMessage *message,
		     const otMessageInfo *info, otError error)
{
	ARG_UNUSED(context);
	ARG_UNUSED(info);
	pending = false;
	if (error != OT_ERROR_NONE || message == NULL) {
		LOG_WRN("Reading delivery failed (OT error %d)", error);
		return;
	}
	otCoapCode code = otCoapMessageGetCode(message);
	if (code == OT_COAP_CODE_CHANGED || code == OT_COAP_CODE_CREATED) {
		LOG_INF("Collector acknowledged reading");
	} else {
		LOG_WRN("Collector rejected/unexpected response: %u.%02u",
			(unsigned)code >> 5, (unsigned)code & 31U);
	}
}

int room_network_init(void)
{
	instance = openthread_get_default_instance();
	if (instance == NULL) {
		return -ENODEV;
	}
	openthread_mutex_lock();
	otLinkModeConfig mode = {
		.mRxOnWhenIdle = true,
		.mDeviceType = true,
		.mNetworkData = true,
	};
	otError error = otThreadSetLinkMode(instance, mode);
	if (error == OT_ERROR_NONE) {
		error = otThreadSetRouterEligible(instance, true);
	}
	if (error == OT_ERROR_NONE && otDatasetIsCommissioned(instance)) {
		error = otIp6SetEnabled(instance, true);
		if (error == OT_ERROR_NONE) {
			error = otThreadSetEnabled(instance, true);
		}
	} else if (error == OT_ERROR_NONE) {
		LOG_INF("No active dataset; waiting for physical commissioning");
	}
	if (error == OT_ERROR_NONE && CONFIG_ROOM_COLLECTOR_IPV6[0] != '\0') {
		error = otIp6AddressFromString(CONFIG_ROOM_COLLECTOR_IPV6, &collector);
		/* Only ULA (fc00::/7) or global unicast (2000::/3). No scope guessing. */
		uint8_t first = collector.mFields.m8[0];
		if (error == OT_ERROR_NONE && (first & 0xfe) != 0xfc && (first & 0xe0) != 0x20) {
			error = OT_ERROR_INVALID_ARGS;
		}
		if (error == OT_ERROR_NONE) {
			error = otCoapStart(instance, OT_DEFAULT_COAP_PORT);
			configured = error == OT_ERROR_NONE;
		}
	}
	openthread_mutex_unlock();
	if (error != OT_ERROR_NONE) {
		LOG_ERR("Thread/collector configuration error %d", error);
		return -EIO;
	}
	if (!configured) {
		LOG_WRN("Collector address empty; reporting is disabled");
	}
	return 0;
}

bool room_transport_ready(void)
{
	if (instance == NULL) {
		return false;
	}
	openthread_mutex_lock();
	bool ready = configured && !pending && attached();
	openthread_mutex_unlock();
	return ready;
}

int room_transport_send(const char *json, size_t length)
{
	if (instance == NULL || json == NULL || length == 0 || length > UINT16_MAX) {
		return -EINVAL;
	}
	openthread_mutex_lock();
	if (!configured || pending || !attached()) {
		openthread_mutex_unlock();
		return -EAGAIN;
	}
	otMessage *message = otCoapNewMessage(instance, NULL);
	if (message == NULL) {
		openthread_mutex_unlock();
		return -ENOMEM;
	}
	otCoapMessageInit(message, OT_COAP_TYPE_CONFIRMABLE, OT_COAP_CODE_POST);
	otCoapMessageGenerateToken(message, 8);
	otError error = otCoapMessageAppendUriPathOptions(message, "readings");
	if (error == OT_ERROR_NONE) {
		error = otCoapMessageAppendContentFormatOption(message, OT_COAP_OPTION_CONTENT_FORMAT_JSON);
	}
	if (error == OT_ERROR_NONE) {
		error = otCoapMessageSetPayloadMarker(message);
	}
	if (error == OT_ERROR_NONE) {
		error = otMessageAppend(message, json, (uint16_t)length);
	}
	if (error == OT_ERROR_NONE) {
		otMessageInfo info = {0};
		info.mPeerAddr = collector;
		info.mPeerPort = CONFIG_ROOM_COLLECTOR_PORT;
		pending = true;
		error = otCoapSendRequestWithParameters(instance, message, &info,
						      response, NULL, &tx_parameters);
	}
	if (error != OT_ERROR_NONE) {
		pending = false;
		otMessageFree(message);
	}
	/* On success OpenThread owns and later frees message. */
	openthread_mutex_unlock();
	return error == OT_ERROR_NONE ? 0 : -EIO;
}
