# -*- coding: utf-8 -*-
"""
config.py - Konfigurasi terpusat project Sialan Robot
"""

# URL base API server
API_BASE_URL = "https://semzzdev.qzz.io/api"

# Token autentikasi robot (harus sama dengan ROBOT_API_TOKEN di .env Laravel)
ROBOT_TOKEN = "robot-secret-123"

# Identitas robot
ROBOT_NAME  = "Robot-01"
ROBOT_NO_HP = "08000000000"

# Lokasi default robot (bisa diupdate dari GPS)
DEFAULT_LATITUDE      = -6.200000
DEFAULT_LONGITUDE     = 106.816666
DEFAULT_ALAMAT_LOKASI = "Lokasi tidak diketahui"

# Path model YOLO
MODEL_PATH = "models/best.pt"

# Kamera (0 = webcam default, bisa diganti path video/IP camera)
CAMERA_SOURCE = 0

# Confidence threshold deteksi (0.0 - 1.0)
CONFIDENCE_THRESHOLD = 0.5

# Jeda minimum antar laporan (detik) agar tidak spam ke server
REPORT_COOLDOWN_SECONDS = 5

# Simpan foto hasil deteksi sebelum dikirim
SAVE_DETECTED_FRAME = True
DETECTED_FRAMES_DIR = "detected_frames"

# =======================================================
#  KONFIGURASI GPS
# =======================================================
# Jika True, robot akan menggunakan simulasi pergerakan (cocok untuk testing di laptop/PC)
# Jika False, robot akan mencoba membaca modul GPS via Serial/USB (misal: Ublox NEO-6M)
USE_MOCK_GPS = True
GPS_SERIAL_PORT = "COM3"  # Sesuaikan dengan port USB GPS di sistem Anda (contoh Linux: /dev/ttyUSB0)
GPS_BAUDRATE = 9600
