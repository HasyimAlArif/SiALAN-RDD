# -*- coding: utf-8 -*-
"""
main.py - Entry point project Sialan Robot
Jalankan file ini untuk memulai sistem deteksi otomatis.

Cara pakai:
    python main.py            # deteksi real-time via kamera
    python main.py --test     # tes koneksi API tanpa kamera
"""

import sys
import io

# Paksa UTF-8 di terminal Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import argparse
import requests

import config
from api_client import RobotAPIClient


def tes_koneksi():
    """Tes koneksi ke server dengan mengirim laporan dummy."""
    print("\n[INFO] Mode tes koneksi API...")
    print(f"       URL   : {config.API_BASE_URL}")
    print(f"       Token : {config.ROBOT_TOKEN}")
    print("-" * 50)

    client = RobotAPIClient(
        base_url = config.API_BASE_URL,
        token    = config.ROBOT_TOKEN,
    )

    try:
        result = client.kirim_laporan(
            nama_pelapor  = config.ROBOT_NAME,
            no_hp         = config.ROBOT_NO_HP,
            judul         = "[TES] Koneksi Robot",
            deskripsi     = "Ini adalah laporan tes koneksi dari robot.",
            latitude      = config.DEFAULT_LATITUDE,
            longitude     = config.DEFAULT_LONGITUDE,
            alamat_lokasi = config.DEFAULT_ALAMAT_LOKASI,
        )

        if result.get("success"):
            print("[OK] Koneksi berhasil! Server merespons dengan benar.")
            print(f"     ID Laporan : {result['data']['id']}")
            print(f"     Status     : {result['data']['status']}")
        else:
            print(f"[GAGAL] Server merespons tapi laporan ditolak: {result.get('message')}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] Tidak bisa terhubung ke server. Cek jaringan atau URL.")
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP {e.response.status_code}: {e.response.text}")
    except Exception as e:
        print(f"[ERROR] {e}")

    print("-" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="SIALAN-Road Demage Detection"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Tes koneksi API tanpa membuka kamera",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("  SIALAN-Road Demage Detection")
    print("=" * 50)

    if args.test:
        tes_koneksi()
    else:
        from gui import start_gui
        start_gui()


if __name__ == "__main__":
    main()
