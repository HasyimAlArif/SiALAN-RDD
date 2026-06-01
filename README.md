# Sialan Robot - Pothole Detection System

Project Python terpisah untuk robot pendeteksi lubang jalan berbasis YOLO.
Terhubung ke API server [Sialan-web](https://github.com/HasyimAlArif/Sialan-web) secara otomatis.

---

## Struktur Folder

```
Sialan-robot/
├── main.py              # Entry point utama
├── detector.py          # Loop deteksi YOLO + kirim laporan (dengan GPS real-time)
├── api_client.py        # Kelas HTTP client ke API SIALAN
├── gps_reader.py        # Modul pembaca hardware GPS (NMEA) / Simulasi
├── config.py            # Semua konfigurasi (URL, token, kamera, GPS, dll)
├── requirements.txt     # Dependensi Python
├── models/
│   └── best.pt          # Model YOLO hasil training (letakkan di sini)
└── detected_frames/     # Folder auto-dibuat untuk menyimpan frame hasil deteksi
```

---

## Instalasi

```bash
pip install -r requirements.txt
```

---

## Konfigurasi

Edit file `config.py` sesuai kebutuhan:

| Variabel                  | Default                        | Keterangan                              |
|---------------------------|--------------------------------|-----------------------------------------|
| `API_BASE_URL`            | `https://semzzdev.qzz.io/api` | URL base API server                     |
| `ROBOT_TOKEN`             | `robot-secret-123`             | Token autentikasi robot                 |
| `ROBOT_NAME`              | `Robot-01`                     | Nama robot sebagai pelapor              |
| `CAMERA_SOURCE`           | `0`                            | Index kamera (0=webcam, atau path video)|
| `CONFIDENCE_THRESHOLD`    | `0.5`                          | Batas confidence deteksi YOLO           |
| `REPORT_COOLDOWN_SECONDS` | `3`                           | Jeda minimum antar laporan (detik)      |
| `USE_MOCK_GPS`            | `True`                         | Gunakan simulasi koordinat acak jika `True` |
| `GPS_SERIAL_PORT`         | `COM3`                         | Port Serial GPS (misal `COM3` atau `/dev/ttyUSB0`) |
| `GPS_BAUDRATE`            | `9600`                         | Baudrate modul GPS (biasanya 9600)      |
| `MODEL_PATH`              | `models/best.pt`               | Path ke model YOLO                      |

---

## Cara Pakai

### 1. Letakkan model YOLO
```
Salin best.pt ke folder: models/best.pt
```

### 2. Tes koneksi API (tanpa kamera)
```bash
python main.py --test
```

### 3. Jalankan deteksi real-time
```bash
python main.py
```

Tekan **Q** di jendela kamera untuk berhenti.

---

## Alur Kerja

```
Kamera --> YOLO Deteksi --> Lubang Terdeteksi?
                                  |
                                 Ya
                                  |
                          Simpan Frame (foto)
                                  |
                          Kirim ke API SIALAN
                                  |
                           Tunggu Cooldown (30 detik)
                                  |
                          Ulangi deteksi...
```

---

## 🍓 Panduan Khusus Raspberry Pi 5 & Modul GPS

Jika Anda ingin menjalankan sistem ini di Raspberry Pi 5 di lapangan, ikuti langkah-langkah berikut:

### 1. Persiapan Raspberry Pi 5
Buka terminal di Raspberry Pi Anda dan jalankan perintah berikut untuk meng-update sistem dan menginstal *library* dasar yang dibutuhkan OpenCV:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install libgl1-mesa-glx libglib2.0-0 -y
```

### 2. Konfigurasi Hardware Serial (Untuk Modul GPS)
Raspberry Pi perlu dikonfigurasi agar pin GPIO-nya bisa membaca data dari modul GPS (via UART).
1. Ketik `sudo raspi-config` di terminal.
2. Pilih **3 Interface Options**.
3. Pilih **I5 Serial Port**.
4. Akan muncul pertanyaan: *"Would you like a login shell to be accessible over serial?"* -> Pilih **No**.
5. Akan muncul pertanyaan: *"Would you like the serial port hardware to be enabled?"* -> Pilih **Yes**.
6. Keluar dan **Reboot (Restart)** Raspberry Pi Anda.

### 3. Skema Pemasangan Kabel Modul GPS (NEO-6M / sejenis)
Hubungkan 4 kabel dari Modul GPS ke pin GPIO Raspberry Pi 5:
- **VCC** (Merah) -> Pin 2 atau 4 (5V) atau Pin 1 (3.3V, *tergantung spesifikasi modul GPS Anda*)
- **GND** (Hitam) -> Pin 6 (Ground)
- **TX** (Kuning) -> Pin 10 (GPIO 15 / RXD)
- **RX** (Hijau)  -> Pin 8 (GPIO 14 / TXD)

*(Perhatian: Pin TX dari GPS harus masuk ke pin RX di Raspberry Pi, begitupun sebaliknya secara menyilang).*

### 4. Instalasi Project
Disarankan menggunakan *Virtual Environment* (venv) di Raspberry Pi:
```bash
# Buat virtual environment
python3 -m venv env
source env/bin/activate

# Install requirements
pip install -r requirements.txt

# (Khusus GUI Tkinter) pastikan tkinter terinstall di sistem Linux
sudo apt install python3-tk -y
```

### 5. Sesuaikan `config.py`
Buka file `config.py` dan ubah 2 baris berikut:
```python
USE_MOCK_GPS = False
GPS_SERIAL_PORT = "/dev/serial0"  # Port default UART hardware Raspberry Pi
```

### 6. Jalankan Aplikasi
Karena kita sudah menggunakan GUI Desktop:
```bash
# Pastikan Anda menjalankannya di desktop Raspberry Pi (bukan via SSH teks)
python3 main.py
```
