# -*- coding: utf-8 -*-
"""
gps_reader.py - Modul pembaca sensor GPS
Menggunakan modul serial (USB/UART) untuk membaca data NMEA (seperti modul Ublox NEO-6M).
"""

import serial
import pynmea2
import threading
import time
import random

import config

class GPSReader:
    def __init__(self):
        self.latitude = config.DEFAULT_LATITUDE
        self.longitude = config.DEFAULT_LONGITUDE
        self.is_running = False
        self.thread = None
        self.serial_conn = None

    def start(self):
        self.is_running = True
        if config.USE_MOCK_GPS:
            print("[INFO] GPS berjalan dalam Mode Simulasi (Mock GPS)")
            self.thread = threading.Thread(target=self._mock_update_loop, daemon=True)
        else:
            print(f"[INFO] Mencoba koneksi ke GPS di port {config.GPS_SERIAL_PORT} (Baudrate: {config.GPS_BAUDRATE})")
            try:
                self.serial_conn = serial.Serial(config.GPS_SERIAL_PORT, config.GPS_BAUDRATE, timeout=1)
                self.thread = threading.Thread(target=self._read_serial_loop, daemon=True)
            except Exception as e:
                print(f"[ERROR] Gagal membuka port GPS: {e}")
                print("[INFO] Fallback ke nilai default/simulasi")
                self.thread = threading.Thread(target=self._mock_update_loop, daemon=True)
        
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            
    def get_location(self):
        """Mengembalikan latitude dan longitude saat ini."""
        return self.latitude, self.longitude

    def _read_serial_loop(self):
        """Loop membaca data asli dari hardware GPS (NMEA)."""
        while self.is_running:
            try:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode('ascii', errors='replace')
                    if line.startswith('$GPRMC') or line.startswith('$GPGGA'):
                        msg = pynmea2.parse(line)
                        if msg.latitude != 0.0 and msg.longitude != 0.0:
                            self.latitude = msg.latitude
                            self.longitude = msg.longitude
            except Exception as e:
                # Hindari crash jika ada masalah parsing sementara
                pass
            time.sleep(0.1)

    def _mock_update_loop(self):
        """Loop simulasi pergerakan robot (update koordinat sedikit demi sedikit)."""
        while self.is_running:
            # Simulasi pergerakan robot secara acak
            self.latitude += random.uniform(-0.0001, 0.0001)
            self.longitude += random.uniform(-0.0001, 0.0001)
            time.sleep(2)
