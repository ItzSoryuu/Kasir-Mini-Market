"""
Modul Logika Bisnis Transaksi.
Mengatur validasi login, kalkulasi diskon, dan pembuatan struk belanja.
"""
import json

daftar_barang = [
    [1, "Beras", 15000],
    [2, "Minyak", 20000],
    [3, "Gula", 14000]
]

# Melacak sisa percobaan login admin selama server aktif
sisa_kesempatan = 3

def login(username, password):
    """
    Validasi kredensial admin.
    Return nilai Boolean (True jika cocok, False jika salah).
    """
    ADMIN_USER = "admin"
    ADMIN_PASS = "1234"
    return username == ADMIN_USER and password == ADMIN_PASS

def tampil_barang():
    """Menampilkan tabel daftar barang ke terminal server."""
    print("\n========== DAFTAR BARANG ==========")
    print(f"{'No':<5}{'Nama Barang':<15}{'Harga':<10}")
    print("-" * 30)
    for barang in daftar_barang:
        print(f"{barang[0]:<5}{barang[1]:<15}Rp {barang[2]}")
    print("-" * 30)

def hitung_total(keranjang):
    """
    Kalkulasi total harga belanjaan tanpa diskon.
    :param keranjang: List barang yang dibeli.
    """
    total = 0
    for item in keranjang:
        total += item['harga'] * item['jumlah']
    return total

def hitung_diskon(total_belanja, status_member):
    """
    Logika perhitungan diskon berdasarkan status member dan total belanja.
    Return nilai diskon dalam integer.
    """
    diskon = 0
    if status_member == "ya":
        if total_belanja >= 100000:
            diskon = total_belanja * 0.15
        elif total_belanja >= 50000:
            diskon = total_belanja * 0.10
        else:
            diskon = total_belanja * 0.05
    else:
        if total_belanja >= 100000:
            diskon = total_belanja * 0.05
        else:
            diskon = 0
    return int(diskon)

def cetak_struk(status_member, total_belanja, nilai_diskon, total_bayar, keranjang):
    """
    Mencetak struk transaksi ke konsol server untuk keperluan audit/log.
    """
    print("\n" + "="*35)
    print("======== STRUK PEMBAYARAN =========")
    print(f"Member       : {status_member}")
    print("-" * 35)
    for item in keranjang:
        print(f"{item['nama']} (x{item['jumlah']}) : Rp {item['harga'] * item['jumlah']}")
    print("-" * 35)
    print(f"Total Belanja: Rp {total_belanja}")
    print(f"Diskon       : Rp {nilai_diskon} ({(nilai_diskon/total_belanja*100) if total_belanja > 0 else 0:.2f}%)")
    print(f"Total Bayar  : Rp {total_bayar}")
    print("="*35 + "\n")

def handleApiLogin(handler_context):
    """
    Endpoint API untuk proses login.
    Mengatur pembatasan percobaan login dan mengirim respon status ke frontend.
    """
    global sisa_kesempatan
    try:
        content_length = int(handler_context.headers['Content-Length'])
        post_data = handler_context.rfile.read(content_length)
        data_login = json.loads(post_data.decode('utf-8'))
        
        if sisa_kesempatan <= 0:
            handler_context.send_response(403)
            handler_context.send_header('Content-Type', 'application/json')
            handler_context.end_headers()
            handler_context.wfile.write(b'{"status":"gagal","pesan":"Akses diblokir! Kesempatan habis."}')
            return

        terverifikasi = login(data_login.get('username'), data_login.get('password'))
        
        handler_context.send_response(200)
        handler_context.send_header('Content-Type', 'application/json')
        handler_context.end_headers()

        if terverifikasi:
            sisa_kesempatan = 3
            handler_context.wfile.write(b'{"status":"sukses"}')
        else:
            sisa_kesempatan -= 1
            pesan_gagal = f"Kredensial salah! Sisa kesempatan: {sisa_kesempatan}"
            if sisa_kesempatan <= 0:
                pesan_gagal = "Kesempatan login habis! Akses ditutup."
            handler_context.wfile.write(json.dumps({"status": "gagal", "pesan": pesan_gagal}).encode('utf-8'))
            
    except Exception as e:
        handler_context.send_response(500)
        handler_context.end_headers()

def handleApiTransaksi(handler_context):
    """
    Endpoint API untuk pemrosesan transaksi belanja.
    Menghitung total, diskon, dan mengembalikan data struk final ke browser.
    """
    try:
        content_length = int(handler_context.headers['Content-Length'])
        post_data = handler_context.rfile.read(content_length)
        data_request = json.loads(post_data.decode('utf-8'))
        
        keranjang = data_request['keranjang']
        status_member = data_request['member']
        
        tampil_barang()
        total_belanja = hitung_total(keranjang)
        nilai_diskon = hitung_diskon(total_belanja, status_member)
        total_bayar = total_belanja - nilai_diskon
        
        cetak_struk(status_member, total_belanja, nilai_diskon, total_bayar, keranjang)
        
        data_final = {
            "id_transaksi": "TRX-LIVE",
            "member": status_member,
            "total_belanja": total_belanja,
            "diskon": nilai_diskon,
            "total_bayar": total_bayar,
            "detail_barang": keranjang
        }
        
        handler_context.send_response(200)
        handler_context.send_header('Content-Type', 'application/json')
        handler_context.end_headers()
        handler_context.wfile.write(json.dumps({"status": "sukses", "struk": data_final}).encode('utf-8'))

    except Exception as e:
        handler_context.send_response(500)
        handler_context.end_headers()