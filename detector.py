# -*- coding: utf-8 -*-
"""
detector.py - Deteksi lubang jalan menggunakan YOLO + kirim laporan ke API
"""

import cv2
import os
import sys
import time
import io
from datetime import datetime
from ultralytics import YOLO

import config
from api_client import RobotAPIClient
from gps_reader import GPSReader

# Paksa UTF-8 di terminal Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# =======================================================
#  STATE
# =======================================================
_last_report_time = 0   # Timestamp laporan terakhir dikirim


def _bisa_kirim_laporan() -> bool:
    """Cek apakah sudah melewati cooldown sebelum kirim laporan lagi."""
    return (time.time() - _last_report_time) >= config.REPORT_COOLDOWN_SECONDS


def _encode_frame(frame) -> bytes:
    """Mengubah frame OpenCV menjadi byte stream JPEG di memori."""
    success, encoded_image = cv2.imencode('.jpg', frame)
    if success:
        return encoded_image.tobytes()
    return None

def _kirim_laporan(client: RobotAPIClient, frame_bytes: bytes = None, lat: float = config.DEFAULT_LATITUDE, lon: float = config.DEFAULT_LONGITUDE):
    """Kirim laporan deteksi ke server SIALAN dengan lokasi real-time."""
    global _last_report_time

    waktu     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    deskripsi = "-"

    try:
        result = client.kirim_laporan(
            nama_pelapor  = config.ROBOT_NAME,
            no_hp         = config.ROBOT_NO_HP,
            judul         = "Lubang Jalan Terdeteksi (Otomatis)",
            deskripsi     = deskripsi,
            latitude      = lat,
            longitude     = lon,
            alamat_lokasi = config.DEFAULT_ALAMAT_LOKASI,
            foto_bytes    = frame_bytes,
        )
        _last_report_time = time.time()

        if result.get("success"):
            print(f"[OK] Laporan terkirim | ID: {result['data']['id']} | {waktu} | Lokasi: {lat:.6f}, {lon:.6f}")
        else:
            print(f"[GAGAL] Server menolak laporan: {result.get('message')}")

    except Exception as e:
        print(f"[ERROR] Gagal kirim laporan: {e}")


# =======================================================
#  MAIN DETECTION LOOP
# =======================================================

def jalankan_deteksi():
    """Loop utama: buka kamera, deteksi lubang, dan kirim laporan."""

    print("[INFO] Memulai modul GPS...")
    gps = GPSReader()
    gps.start()

    print("[INFO] Memuat model YOLO dari:", config.MODEL_PATH)
    model = YOLO(config.MODEL_PATH)

    print("[INFO] Membuka kamera:", config.CAMERA_SOURCE)
    cap = cv2.VideoCapture(config.CAMERA_SOURCE)

    if not cap.isOpened():
        print("[ERROR] Gagal membuka kamera.")
        return

    client = RobotAPIClient(
        base_url = config.API_BASE_URL,
        token    = config.ROBOT_TOKEN,
    )

    print("[INFO] Deteksi dimulai. Tekan 'Q' untuk keluar.")
    print(f"[INFO] Cooldown laporan: {config.REPORT_COOLDOWN_SECONDS} detik")
    print("-" * 50)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Gagal membaca frame dari kamera.")
            break

        # Jalankan deteksi YOLO
        results    = model(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
        annotated  = results[0].plot()
        detections = results[0].boxes

        # Jika ada objek terdeteksi dan sudah melewati cooldown
        if len(detections) > 0 and _bisa_kirim_laporan():
            print(f"\n[DETEKSI] {len(detections)} lubang ditemukan!")

            foto_bytes = None
            if config.SAVE_DETECTED_FRAME:
                foto_bytes = _encode_frame(annotated)
                print("[INFO] Gambar siap dikirim (langsung dari memori)")

            lat, lon = gps.get_location()
            _kirim_laporan(client, frame_bytes=foto_bytes, lat=lat, lon=lon)

        # Tampilkan jendela live
        cv2.imshow("Sialan - Pothole Detection", annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("\n[INFO] Deteksi dihentikan oleh pengguna.")
            break

    cap.release()
    cv2.destroyAllWindows()
    gps.stop()


if __name__ == "__main__":
    jalankan_deteksi()
