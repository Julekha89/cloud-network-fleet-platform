"""Read-only HTTP API for a fictional multi-region network fleet."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs, unquote
from pathlib import Path
import json
import os

from fleet.core import FleetStore, load_sample


class FleetHandler(BaseHTTPRequestHandler):
    store: FleetStore

    def send_json(self, code: int, data: dict | list) -> None:
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        url = urlsplit(self.path)
        path = url.path.rstrip('/') or '/'
        params = parse_qs(url.query)
        if path == '/healthz':
            return self.send_json(200, {'service': 'ok', 'mode': 'simulation'})
        if path == '/api/v1/devices':
            return self.send_json(200, {'devices': self.store.list_devices(params.get('region', [None])[0])})
        if path.startswith('/api/v1/devices/') and path.endswith('/health'):
            id_ = unquote(path[len('/api/v1/devices/'):-len('/health')].strip('/'))
            if not id_ or '/' in id_:
                return self.send_json(400, {'error': 'invalid device ID'})
            result = self.store.assess(id_)
            return self.send_json(200, result) if result else self.send_json(404, {'error': 'device not found'})
        if path == '/api/v1/fleet/summary':
            return self.send_json(200, self.store.summary())
        if path == '/api/v1/audit':
            return self.send_json(200, {'events': self.store.audit_log()})
        return self.send_json(404, {'error': 'not found'})

    def do_POST(self):
        return self.send_json(405, {'error': 'Read-only demo: writes are disabled'})

    def do_PUT(self):
        return self.send_json(405, {'error': 'Read-only demo: writes are disabled'})

    def do_DELETE(self):
        return self.send_json(405, {'error': 'Read-only demo: writes are disabled'})


def serve(host: str = '127.0.0.1', port: int = 8080, database: str = ':memory:') -> None:
    store = FleetStore(database)
    load_sample(store, Path(__file__).resolve().parent.parent / 'examples/devices.json')
    class Handler(FleetHandler):
        pass
    Handler.store = store
    server = ThreadingHTTPServer((host, port), Handler)
    print(f'Lab-only fleet API available at http://{host}:{port} (Ctrl+C to stop)', flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        store.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Lab-only network fleet API')
    parser.add_argument('--host', default='127.0.0.1', help='Bind address; loopback by default')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--database', default=':memory:')
    args = parser.parse_args()
    serve(args.host, args.port, args.database)
