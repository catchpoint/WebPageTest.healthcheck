#!/usr/bin/env python
# Copyright 2017 Google Inc. All rights reserved.
# Use of this source code is governed by the Apache 2.0 license that can be
# found in the LICENSE file.
"""HTTP Healthcheck responder"""
import os
import time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

ALIVE_FILE = None

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP server that responds to health checks"""
    def do_GET(self):
        """Handle GET requests"""
        response_code = 409
        message = 'Error'

        if os.path.isfile('/proc/uptime'):
            with open('/proc/uptime', 'r') as f_in:
                uptime_seconds = int(float(f_in.readline().split()[0]))
                if uptime_seconds < 3600:
                    response_code = 200
                    message = 'OK: Freshly booted ({0:d} seconds)'.format(uptime_seconds)

        if response_code != 200 and ALIVE_FILE is not None and os.path.isfile(ALIVE_FILE):
            elapsed = int(time.time() - os.path.getmtime(ALIVE_FILE))
            if elapsed < 3600:
                response_code = 200
                message = 'OK: last updated {0:d} seconds ago'.format(elapsed)
            else:
                message = 'ERROR: last updated {0:d} seconds ago'.format(elapsed)

        self.send_response(response_code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message)
        with open('/tmp/healthcheck', 'wb') as f_out:
            f_out.write(message + "\n")


def main():
    """Startup and initialization"""
    global ALIVE_FILE
    import argparse
    parser = argparse.ArgumentParser(description='WebPageTest Agent.', prog='wpt-agent')
    parser.add_argument('--file', help="File to check for modifications within the last hour.")
    parser.add_argument('--port', type=int, default=8877, help="HTTP server port (default 8877).")
    options, _ = parser.parse_known_args()

    if options.file is not None:
        ALIVE_FILE = options.file

    print 'Starting http server on port {0:d}...'.format(options.port)
    httpd = HTTPServer(('', options.port), HealthCheckHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
