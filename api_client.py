# -*- coding: utf-8 -*-
"""
api_client.py - Kelas untuk berkomunikasi dengan API SIALAN
"""

import os
import requests


class RobotAPIClient:
    """Client HTTP untuk mengirim laporan ke server SIALAN."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.session  = requests.Session()
        self.session.headers.update({
            "X-Robot-Token": token,
            "Accept": "application/json",
        })

    def kirim_laporan(
        self,
        nama_pelapor: str,
        no_hp: str,
        judul: str,
        deskripsi: str,
        latitude: float,
        longitude: float,
        alamat_lokasi: str,
        foto_bytes: bytes = None,
    ) -> dict:
        """
        Kirim laporan ke API SIALAN. Foto bersifat opsional.

        Args:
            foto_bytes: Data gambar dalam bentuk bytes (langsung dari memori).

        Returns:
            dict: Response JSON dari server.
        """
        payload = {
            "nama_pelapor":  nama_pelapor,
            "no_hp":         no_hp,
            "judul":         judul,
            "deskripsi":     deskripsi,
            "latitude":      str(latitude),
            "longitude":     str(longitude),
            "alamat_lokasi": alamat_lokasi,
        }

        url = f"{self.base_url}/robot/laporans"

        if foto_bytes:
            files = {"foto": ("detected.jpg", foto_bytes, "image/jpeg")}
            response = self.session.post(url, data=payload, files=files, timeout=30)
        else:
            response = self.session.post(url, data=payload, timeout=15)

        response.raise_for_status()
        return response.json()
