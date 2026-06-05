/*
    Logika Frontend Aplikasi Kasir.
    Mengelola interaksi UI, keranjang belanja, dan komunikasi dengan API backend.
*/

const daftarBarang = [
    { id: 1, nama: "Beras", harga: 15000 },
    { id: 2, nama: "Minyak", harga: 20000 },
    { id: 3, nama: "Gula", harga: 14000 }
];

let keranjang = [];

// DOM Elements
const loginScreen = document.getElementById('login-screen');
const mainScreen = document.getElementById('main-screen');
const inputUser = document.getElementById('input-username');
const inputPass = document.getElementById('input-password');
const loginError = document.getElementById('login-error');
const btnLogin = document.getElementById('btn-login');
const btnLogout = document.getElementById('btn-logout');

const productListEl = document.getElementById('product-list');
const cartListEl = document.getElementById('cart-list');
const textTotalEl = document.getElementById('text-total');
const textDiskonEl = document.getElementById('text-diskon');
const textBayarEl = document.getElementById('text-bayar');
const memberStatusEl = document.getElementById('member-status');
const btnCheckout = document.getElementById('btn-checkout');

/**
 * Mengirim data login ke server untuk verifikasi.
 * Jika sukses, menyimpan status session dan memperbarui UI.
 */
async function handleLogin() {
    const payload = {
        username: inputUser.value,
        password: inputPass.value
    };

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (response.ok && data.status === "sukses") {
            loginError.style.display = 'none';
            sessionStorage.setItem('isLoggedIn', 'true');
            checkSession();
        } else {
            loginError.style.display = 'block';
            loginError.innerText = data.pesan || "Login Gagal!";
        }
    } catch (err) {
        console.error(err);
        alert('Gagal terhubung ke server.');
    }
}

/**
 * Mengecek status login di sessionStorage dan menampilkan layar yang sesuai.
 */
function checkSession() {
    if (sessionStorage.getItem('isLoggedIn') === 'true') {
        loginScreen.style.display = 'none';
        mainScreen.style.display = 'block';
        renderProducts();
    } else {
        loginScreen.style.display = 'flex';
        mainScreen.style.display = 'none';
    }
}

// Event Listeners untuk Login/Logout
btnLogin.addEventListener('click', handleLogin);
btnLogout.addEventListener('click', () => {
    sessionStorage.removeItem('isLoggedIn');
    inputUser.value = "";
    inputPass.value = "";
    checkSession();
});

// Inisialisasi pengecekan session saat aplikasi dimuat
checkSession();

/**
 * Menampilkan daftar produk yang tersedia ke dalam DOM.
 */
function renderProducts() {
    productListEl.innerHTML = daftarBarang.map(barang => `
        <div class="item-row">
            <div class="item-info">
                <div class="item-name">${barang.nama}</div>
                <div class="item-price">Rp ${barang.harga.toLocaleString('id-ID')}</div>
            </div>
            <button class="oui-btn-action" onclick="tambahKeKeranjang(${barang.id})">Tambah</button>
        </div>
    `).join('');
}

/**
 * Menambahkan barang ke dalam array keranjang atau menambah jumlahnya.
 * @param {number} id - ID barang yang akan ditambah.
 */
window.tambahKeKeranjang = function(id) {
    const barang = daftarBarang.find(b => b.id === id);
    const itemDiKeranjang = keranjang.find(item => item.id === id);

    if (itemDiKeranjang) {
        itemDiKeranjang.jumlah += 1;
    } else {
        keranjang.push({ ...barang, jumlah: 1 });
    }
    updateKalkulasi();
};

/**
 * Menghitung ulang total, diskon, dan total bayar berdasarkan isi keranjang 
 * dan status member, kemudian memperbarui tampilan struk belanja.
 */
function updateKalkulasi() {
    if (keranjang.length === 0) {
        cartListEl.innerHTML = 'Belum ada barang di keranjang.';
        cartListEl.classList.add('empty');
        textTotalEl.innerText = 'Rp0';
        textDiskonEl.innerText = 'Rp0';
        textBayarEl.innerText = 'Rp0';
        btnCheckout.disabled = true;
        return;
    }

    cartListEl.classList.remove('empty');
    cartListEl.innerHTML = keranjang.map(item => `
        <div class="item-row">
            <div class="item-info">
                <div class="item-name">${item.nama} (x${item.jumlah})</div>
                <div class="item-price">Subtotal: Rp ${(item.harga * item.jumlah).toLocaleString('id-ID')}</div>
            </div>
            <button class="oui-btn-action" style="color:red;" onclick="hapusDariKeranjang(${item.id})">Hapus</button>
        </div>
    `).join('');

    const totalBelanja = keranjang.reduce((sum, item) => sum + (item.harga * item.jumlah), 0);
    const statusMember = memberStatusEl.value;
    let diskon = 0;

    if (statusMember === 'ya') {
        if (totalBelanja >= 100000) diskon = totalBelanja * 0.15;
        else if (totalBelanja >= 50000) diskon = totalBelanja * 0.10;
        else diskon = totalBelanja * 0.05;
    } else {
        if (totalBelanja >= 100000) diskon = totalBelanja * 0.05;
    }

    const totalBayar = totalBelanja - diskon;
    textTotalEl.innerText = `Rp ${totalBelanja.toLocaleString('id-ID')}`;
    textDiskonEl.innerText = `Rp ${diskon.toLocaleString('id-ID')}`;
    textBayarEl.innerText = `Rp ${totalBayar.toLocaleString('id-ID')}`;
    btnCheckout.disabled = false;
}
window.hapusDariKeranjang = function(id) {
    keranjang = keranjang.filter(item => item.id !== id);
    updateKalkulasi();
};

// Update kalkulasi secara real-time saat status member berubah
memberStatusEl.addEventListener('change', updateKalkulasi);

/**
 * Mengirim data transaksi ke backend untuk diproses dan menampilkan struk di Terminal.
 */
btnCheckout.addEventListener('click', async () => {
    const totalBelanja = keranjang.reduce((sum, item) => sum + (item.harga * item.jumlah), 0);
    const payload = {
        member: memberStatusEl.value,
        total_belanja: totalBelanja,
        keranjang: keranjang
    };

    try {
        const response = await fetch('/api/transaksi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok && data.status === "sukses") {
            alert("Struk Telah Dicetak Dalam Terminal");
            
            keranjang = [];
            updateKalkulasi();
        } else {
            alert('Gagal memproses transaksi.');
        }
    } catch (err) {
        console.error(err);
        alert('Terjadi kesalahan koneksi server.');
    }
});