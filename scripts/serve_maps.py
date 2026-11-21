"""Serve the league's map files to a lobby page on this machine, for scripts/lobby-run.js.

    python3 scripts/serve_maps.py   # serves maps/*/*.json at http://127.0.0.1:41499/<name>.json

The lobby page is https; Chrome lets it read from 127.0.0.1 with these CORS and
private-network headers. Only the map files are served.
"""

import http.server
import sys
from functools import partial


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves files with the headers a lobby page on lobby.elidan.org needs to read them."""

    def end_headers(self) -> None:
        """Add the CORS and private-network headers."""
        self.send_header("Access-Control-Allow-Origin", "https://lobby.elidan.org")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        super().end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        """Answer the preflight."""
        self.send_response(204)
        self.end_headers()


def main() -> None:
    """Copy every map into one directory, flat, and serve it."""
    import shutil
    import tempfile
    from pathlib import Path

    flat = Path(tempfile.mkdtemp(prefix="league-maps-"))
    for path in sorted((Path(__file__).resolve().parents[1] / "maps").glob("*/*.json")):
        shutil.copy(path, flat / path.name)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 41499
    http.server.ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(flat))).serve_forever()


if __name__ == "__main__":
    main()
