# -*- coding: utf-8 -*-
"""
gui.py - Antarmuka Grafis (GUI) untuk Robot Sialan menggunakan Tkinter
"""

import tkinter as tk
from tkinter import font as tkfont
import cv2
from PIL import Image, ImageTk
import time
import os
from datetime import datetime
from ultralytics import YOLO

import config
from api_client import RobotAPIClient
from gps_reader import GPSReader
from detector import _bisa_kirim_laporan, _encode_frame, _kirim_laporan

# Path logo relatif ke file ini
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.png")

class SialanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SIALAN-Road Demage Detection")
        self.root.geometry("800x600")
        self.root.configure(bg="#454142")
        self.root.minsize(800, 600)

        # Set window icon (logo di title bar)
        if os.path.exists(LOGO_PATH):
            try:
                logo_icon = Image.open(LOGO_PATH)
                self._icon_img = ImageTk.PhotoImage(logo_icon)
                self.root.iconphoto(True, self._icon_img)
            except Exception as e:
                print(f"[WARN] Gagal memuat ikon logo: {e}")

        # STATE VARIABLES
        self.is_kamera_on = False
        self.is_deteksi_on = False
        self.cap = None
        self.model = None
        self.gps = GPSReader()
        self.api_client = RobotAPIClient(
            base_url=config.API_BASE_URL,
            token=config.ROBOT_TOKEN
        )
        self.fps = 0
        self.last_frame_time = time.time()
        
        self.setup_ui()
        self.gps.start()
        self.update_gps_status()

    def setup_ui(self):
        # 1. Area Kamera (Atas)
        self.video_frame = tk.Frame(self.root, bg="#454142")
        self.video_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.video_frame, bg="#454142", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Elemen teks di kanvas (saat kamera mati)
        self.text_center = self.canvas.create_text(
            400, 250, text="Kamera", fill="white", font=("Helvetica", 24)
        )
        self.text_fps = self.canvas.create_text(
            10, 10, text="FPS : 0", fill="red", font=("Helvetica", 16, "bold"), anchor="nw"
        )
        self.text_gps = self.canvas.create_text(
            10, 480, text="longitude,latitude", fill="red", font=("Helvetica", 16, "bold"), anchor="sw"
        )

        # Bind event resize agar teks center tetap di tengah
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # 2. Panel Kontrol (Bawah)
        self.control_panel = tk.Frame(self.root, bg="#cccccc", height=100)
        self.control_panel.pack(fill=tk.X, side=tk.BOTTOM)
        self.control_panel.pack_propagate(False) # Pertahankan tinggi 100px

        # Grid config untuk control panel (kolom 0 = logo, 1 = Kamera, 2 = Deteksi, 3 = GPS)
        self.control_panel.columnconfigure(0, weight=1)
        self.control_panel.columnconfigure(1, weight=1)
        self.control_panel.columnconfigure(2, weight=1)
        self.control_panel.columnconfigure(3, weight=1)

        # Kolom 0: Logo SiALAN
        frame_logo = tk.Frame(self.control_panel, bg="#cccccc")
        frame_logo.grid(row=0, column=0, pady=10, padx=10)
        if os.path.exists(LOGO_PATH):
            try:
                logo_img = Image.open(LOGO_PATH).resize((56, 56), Image.Resampling.LANCZOS)
                self._logo_panel_img = ImageTk.PhotoImage(logo_img)
                tk.Label(frame_logo, image=self._logo_panel_img, bg="#cccccc").pack()
            except Exception as e:
                print(f"[WARN] Gagal memuat logo panel: {e}")
                tk.Label(frame_logo, text="SiALAN", bg="#cccccc", font=("Helvetica", 12, "bold"), fg="#1a5fa8").pack()
        else:
            tk.Label(frame_logo, text="SiALAN", bg="#cccccc", font=("Helvetica", 12, "bold"), fg="#1a5fa8").pack()

        # Kolom 1: Kamera
        frame_cam = tk.Frame(self.control_panel, bg="#cccccc")
        frame_cam.grid(row=0, column=1, pady=15)
        tk.Label(frame_cam, text="Kamera", bg="#cccccc", font=("Helvetica", 11)).pack(pady=(0, 5))
        self.btn_kamera = tk.Button(
            frame_cam, text="ON", width=15, font=("Helvetica", 10),
            command=self.toggle_kamera, relief=tk.RAISED, bg="#e0e0e0"
        )
        self.btn_kamera.pack()

        # Kolom 2: Deteksi
        frame_det = tk.Frame(self.control_panel, bg="#cccccc")
        frame_det.grid(row=0, column=2, pady=15)
        tk.Label(frame_det, text="Deteksi", bg="#cccccc", font=("Helvetica", 11)).pack(pady=(0, 5))
        self.btn_deteksi = tk.Button(
            frame_det, text="Mulai", width=15, font=("Helvetica", 10),
            command=self.toggle_deteksi, relief=tk.RAISED, bg="#e0e0e0"
        )
        self.btn_deteksi.pack()

        # Kolom 3: Status GPS
        frame_gps = tk.Frame(self.control_panel, bg="#cccccc")
        frame_gps.grid(row=0, column=3, pady=15)
        tk.Label(frame_gps, text="Status GPS", bg="#cccccc", font=("Helvetica", 11)).pack(pady=(0, 5))
        self.lbl_gps_status = tk.Label(
            frame_gps, text="Mendapatkan Siynal", width=20, font=("Helvetica", 10),
            relief=tk.SUNKEN, bg="#e0e0e0", pady=3
        )
        self.lbl_gps_status.pack()

    def on_canvas_resize(self, event):
        w, h = event.width, event.height
        self.canvas.coords(self.text_center, w/2, h/2)
        self.canvas.coords(self.text_gps, 10, h-10)

    def toggle_kamera(self):
        if not self.is_kamera_on:
            # Nyalakan Kamera
            self.cap = cv2.VideoCapture(config.CAMERA_SOURCE)
            if self.cap.isOpened():
                self.is_kamera_on = True
                self.btn_kamera.config(text="OFF", bg="#ff9999")
                self.canvas.itemconfig(self.text_center, state="hidden")
                self.update_frame()
            else:
                print("[ERROR] Gagal membuka kamera!")
        else:
            # Matikan Kamera
            self.is_kamera_on = False
            self.btn_kamera.config(text="ON", bg="#e0e0e0")
            if self.cap:
                self.cap.release()
                self.cap = None
            
            # Matikan juga deteksi jika jalan
            if self.is_deteksi_on:
                self.toggle_deteksi()

            # Bersihkan layar
            self.canvas.delete("video_image")
            self.canvas.itemconfig(self.text_center, state="normal")
            self.canvas.itemconfig(self.text_fps, text="FPS : 0")

    def toggle_deteksi(self):
        if not self.is_deteksi_on:
            if not self.is_kamera_on:
                print("[INFO] Nyalakan kamera terlebih dahulu!")
                return
            
            # Load model jika belum ada
            if self.model is None:
                print("[INFO] Memuat model YOLO...")
                self.model = YOLO(config.MODEL_PATH)
            
            self.is_deteksi_on = True
            self.btn_deteksi.config(text="Berhenti", bg="#ff9999")
            print("[INFO] Deteksi dimulai.")
        else:
            self.is_deteksi_on = False
            self.btn_deteksi.config(text="Mulai", bg="#e0e0e0")
            print("[INFO] Deteksi dihentikan.")

    def update_frame(self):
        if not self.is_kamera_on or self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            # Hitung FPS
            current_time = time.time()
            self.fps = 1 / (current_time - self.last_frame_time) if (current_time - self.last_frame_time) > 0 else 0
            self.last_frame_time = current_time

            # Update teks FPS dan GPS di kanvas
            self.canvas.itemconfig(self.text_fps, text=f"FPS : {int(self.fps)}")
            lat, lon = self.gps.get_location()
            self.canvas.itemconfig(self.text_gps, text=f"{lon:.6f},{lat:.6f}")

            # Proses Deteksi
            if self.is_deteksi_on and self.model is not None:
                results = self.model(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
                annotated = results[0].plot()
                detections = results[0].boxes

                if len(detections) > 0 and _bisa_kirim_laporan():
                    print(f"\n[DETEKSI] {len(detections)} lubang ditemukan!")
                    foto_bytes = None
                    if config.SAVE_DETECTED_FRAME:
                        foto_bytes = _encode_frame(annotated)
                        print("[INFO] Gambar siap dikirim (langsung dari memori)")
                    
                    # Kirim laporan secara asynchronous/synchronous
                    _kirim_laporan(self.api_client, frame_bytes=foto_bytes, lat=lat, lon=lon)
                
                frame_to_show = annotated
            else:
                frame_to_show = frame

            # Konversi BGR OpenCV ke RGB PIL untuk Tkinter
            frame_rgb = cv2.cvtColor(frame_to_show, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb)

            # Resize image to fit canvas without maintaining aspect ratio exactly like mockup or fit it?
            # Sebaiknya fit to canvas size
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            if canvas_w > 10 and canvas_h > 10:
                img_pil = img_pil.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(image=img_pil)

            # Hapus gambar sebelumnya lalu timpa dengan baru (ditaruh di belakang teks)
            self.canvas.delete("video_image")
            self.canvas.create_image(0, 0, image=self.photo, anchor="nw", tags="video_image")
            self.canvas.tag_lower("video_image")

        # Looping update
        self.root.after(30, self.update_frame)

    def update_gps_status(self):
        lat, lon = self.gps.get_location()
        if lat != config.DEFAULT_LATITUDE or config.USE_MOCK_GPS:
            self.lbl_gps_status.config(text="Sinyal Didapatkan")
        else:
            self.lbl_gps_status.config(text="Mencari Sinyal...")
        
        self.root.after(2000, self.update_gps_status)

    def on_close(self):
        print("[INFO] Menutup aplikasi...")
        self.gps.stop()
        if self.cap:
            self.cap.release()
        self.root.destroy()

def start_gui():
    root = tk.Tk()
    app = SialanApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    start_gui()
