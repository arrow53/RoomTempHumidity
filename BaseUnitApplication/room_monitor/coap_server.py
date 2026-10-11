"""CoAP adapter. aiocoap owns packet parsing, retransmission and response delivery."""
import json
import sys

from .protocol import ReadingError


async def create_context(store, host="::1", port=5683):
    import aiocoap
    import aiocoap.resource

    class Readings(aiocoap.resource.Resource):
        async def render_post(self, request):
            if request.opt.content_format != 50:
                return aiocoap.Message(code=aiocoap.UNSUPPORTED_CONTENT_FORMAT,
                                       payload=b'{"error":"Content-Format must be application/json (50)"}', content_format=50)
            try:
                result = store.ingest(request.payload)
                return aiocoap.Message(code=aiocoap.CHANGED, payload=json.dumps(result).encode(), content_format=50)
            except ReadingError as exc:
                code = {"too_large": aiocoap.REQUEST_ENTITY_TOO_LARGE, "unknown_node": aiocoap.FORBIDDEN,
                        "replay": aiocoap.CONFLICT, "boot_limit": aiocoap.SERVICE_UNAVAILABLE,
                        "clock": aiocoap.SERVICE_UNAVAILABLE}.get(exc.kind, aiocoap.BAD_REQUEST)
                return aiocoap.Message(code=code, payload=json.dumps({"error": str(exc)}).encode(), content_format=50)

    site = aiocoap.resource.Site()
    site.add_resource(("readings",), Readings())
    transports = ["simplesocketserver"] if sys.platform == "win32" else ["udp6"]
    return await aiocoap.Context.create_server_context(site, bind=(host, port), transports=transports)
