"""
Nama  : Hanif Baihaqi Abdurrahman
Kelas : 11-3
Absen : 13
"""

"""
Server Utama (Entry Point).
Mengelola konfigurasi HTTP server, penyajian file statis frontend,
dan pemetaan rute API ke modul backend.
"""

import http.server
import socketserver
import os
from backend.transaksi import handleApiTransaksi, handleApiLogin

PORT = 8080
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')

class CustomFullStackHandler(http.server.SimpleHTTPRequestHandler):
    """Handler kustom untuk mengatur alur request GET dan POST."""

    def do_GET(self):
        """Melayani permintaan file statis (HTML, CSS, JS) ke browser."""
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
            return self.serve_static('text/html')
        elif self.path == '/style.css':
            return self.serve_static('text/css')
        elif self.path == '/app.js':
            return self.serve_static('application/javascript')
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        """Meneruskan permintaan POST ke fungsi handler API yang sesuai."""
        if self.path == '/api/login':
            handleApiLogin(self)
        elif self.path == '/api/transaksi':
            handleApiTransaksi(self)
        else:
            self.send_error(404)

    def serve_static(self, content_type):
        """
        Membaca dan mengirimkan file statis dari folder frontend.
        :param content_type: Tipe MIME (format file) yang dikirim.
        """
        file_path = os.path.join(FRONTEND_DIR, self.path.lstrip('/'))
        if os.path.exists(file_path):
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

if __name__ == "__main__":
    print(f"Server berjalan pada: http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), CustomFullStackHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt: # Interupsi Ctrl+C untuk menghentikan server
            print("\nServer dimatikan oleh pengguna.")