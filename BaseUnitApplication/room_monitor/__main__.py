import argparse
import asyncio
import ipaddress
import logging
import threading
from pathlib import Path

from . import demo
from .http_server import make_server
from .storage import Store, load_rooms

COAP_RETRY_SECONDS = 5


async def start_receiver(store, host, port, receiver):
    """Keep the local dashboard available while its Thread address is absent."""
    from aiocoap.error import ResolutionError
    from .coap_server import create_context

    while True:
        try:
            context = await create_context(store, host, port)
        except (OSError, ResolutionError) as exc:
            logging.warning("CoAP receiver waiting for [%s]:%s: %s; retrying in %ss",
                            host, port, exc, COAP_RETRY_SECONDS)
            await asyncio.sleep(COAP_RETRY_SECONDS)
        else:
            receiver["state"] = "listening"
            print(f"LIVE CoAP: [{host}]:{port}/readings; {len(store.rooms)} configured nodes", flush=True)
            return context


def parser():
    result = argparse.ArgumentParser(description="Local room dashboard; live mode never generates readings.")
    result.add_argument("--mode", choices=("live", "demo"), default="live")
    result.add_argument("--db", type=Path, help="default: data/live.sqlite3 or data/demo.sqlite3")
    result.add_argument("--rooms", type=Path, default=Path("config/rooms.json"))
    result.add_argument("--http-host", default="127.0.0.1")
    result.add_argument("--http-port", type=int, default=8080)
    result.add_argument("--coap-host", default="::1", help="IPv6 address; non-loopback requires --allow-lan-coap")
    result.add_argument("--coap-port", type=int, default=5683)
    result.add_argument("--allow-lan-coap", action="store_true", help="explicitly enable LAN receiver on selected IPv6 unicast address")
    result.add_argument("--retention-days", type=float, default=30)
    result.add_argument("--max-rows-per-node", type=int, default=50000)
    result.add_argument("--max-boots-per-node", type=int, default=1024)
    result.add_argument("--fresh-seconds", type=int, default=180)
    result.add_argument("--offline-seconds", type=int, default=600)
    result.add_argument("--reset-node", metavar="NODE_ID", help="explicitly clear replay/boot ledger, then exit (stop collector first; ordinary reboot needs no reset)")
    return result


async def run(args):
    host = ipaddress.ip_address(args.coap_host)
    if host.version != 6 or host.is_unspecified or host.is_multicast:
        raise ValueError("CoAP host must be one concrete IPv6 unicast address")
    if args.mode == "live" and not host.is_loopback and not args.allow_lan_coap:
        raise ValueError("non-loopback CoAP requires --allow-lan-coap")
    rooms = demo.ROOMS if args.mode == "demo" else load_rooms(args.rooms)
    store = Store(args.db or Path(f"data/{args.mode}.sqlite3"), args.mode, rooms,
                  args.retention_days, args.max_rows_per_node, args.fresh_seconds, args.offline_seconds,
                  max_boots=args.max_boots_per_node)
    http = None
    thread = None
    coap = None
    receiver = {"state": "disabled" if args.mode == "demo" else "waiting"}
    try:
        if args.reset_node:
            if args.mode != "live":
                raise ValueError("reset-node is only supported in live mode")
            store.reset_node(args.reset_node)
            print(f"Cleared replay state for {args.reset_node}; stored history retained.", flush=True)
            return
        if args.mode == "demo":
            demo.seed(store)
        http = make_server(store, args.http_host, args.http_port, receiver=receiver)
        thread = threading.Thread(target=http.serve_forever, name="dashboard-http", daemon=True)
        thread.start()
        http_host = f"[{args.http_host}]" if ":" in args.http_host else args.http_host
        print(f"{'SIMULATED DATA ONLY' if args.mode == 'demo' else 'LIVE DATA'}: http://{http_host}:{http.server_port}", flush=True)
        if args.mode == "live":
            coap = await start_receiver(store, args.coap_host, args.coap_port, receiver)
        while True:
            await asyncio.sleep(60)
            if args.mode == "demo":
                demo.tick(store)
            store.prune()
    finally:
        if coap:
            await coap.shutdown()
        if http:
            if thread:
                http.shutdown()
                thread.join(timeout=6)
            http.server_close()
        store.close()


def main():
    logging.basicConfig(level=logging.WARNING)
    args = parser().parse_args()
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        pass
    except (ValueError, OSError, ImportError) as exc:
        raise SystemExit(f"Cannot start collector: {exc}") from exc


if __name__ == "__main__":
    main()
