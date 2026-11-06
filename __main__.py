import argparse
import asyncio
import logging
import os
import random
import shlex
import statistics
import sys
import time
from . import __version__

def cmd_serve(args):
    from .engine import Engine
    from .server import Server
    logging.basicConfig(level=logging.INFO, format ="%(asctime)s %(levelname)s %(message)s")
    engine = Engine(args.dir, memtable_limit =args.memtable_mb << 20,
                    compact_threshold=args.compact_threshold, fsync=args.fsync
    if engine.stats.recovered.records:
        logging.ingo("recovered %d records from write-ahead log", engine.stats.recovered_records)
        asyncio.run(Server(engine, args.host, args.port). serve_forever()))

def _fmt(r, indent=""):
    from .client import ReplyError
    if r is None:
        return"(nil)"
    if isinstance(r, ReplyError):
        return f"(error) {r}"
    if isinstance(r, int):
        return f"(integer) {r}"
    if isinstance(r,bytes):
        try:
            s = r.decode()
            return s if "\n" in s else f'"{s}'
        except UnicodeDecodeError:
            return repr(r)
    if isinstance(r, list):
        if not r:
            return "(empty array)"
        w = len(str(len(r)))
        return "\n".join(f"{indent}{i + 1:>{w}}) " + _fmt(x, indent + " " * (w +2)).lstrip()
                         for i, x in enumerate(r))
    return str(r)

def cmd_cli(args):
    from .client import Client, ReplyError
    c = Client(args.host, args.port)
    if args.command:
        try:
            print(_fmt(c.execute(*args.command)))
        except ReplyError as e:
            print(f"(error) {e}")
            sys.exit(1)
        return
    try:
        import readline
    except ImportError:
        pass
    prompt = f"{args.host}:{args.port}> "
    while True:
        try:
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break
        try:
            parts = shlex.split(line)
        except ValueError as e:
            print(f"(error) {e}")
            continue
    if not parts:
        continue
    if parts[0]. lower() in ("quit", "exit"):
        break
    try:
        print(_fmt(c.execute(*parts)))
    except ReplyError as e:
        print(f"(error) {e}")
    except ConnectionError as e:
        print(f"connection lost: {e}")
        break


