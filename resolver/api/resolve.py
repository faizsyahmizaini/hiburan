from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import yt_dlp

CHANNELS = {
    "astroawani": "https://www.dailymotion.com/video/x8dbnq6",
}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        channel = query.get("channel", [None])[0]

        if not channel or channel not in CHANNELS:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(
                f"Unknown channel. Available: {', '.join(CHANNELS)}".encode()
            )
            return

        last_error = None
        for attempt in range(3):
            try:
                with yt_dlp.YoutubeDL({"quiet": True, "format": "best"}) as ydl:
                    info = ydl.extract_info(CHANNELS[channel], download=False)
                    hls_url = info.get("url")

                if not hls_url:
                    last_error = "No live stream URL found for this channel"
                    continue

                self.send_response(302)
                self.send_header("Location", hls_url)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return
            except Exception as e:
                last_error = str(e)

        self.send_response(500)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(f"Failed to resolve stream: {last_error}".encode())
