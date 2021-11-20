#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  barcode.py
#
#  Copyright 2021 Thomas Castleman <contact@draugeros.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
"""Barcode Reader for PyLibMan"""
import cv2
import json
import time
import pyzbar.pyzbar as zbar
import numpy as np
import common


def get_frame(webcam):
    """Get a frame from the Webcam"""
    return cv2.cvtColor(np.array(webcam.read()[1]), cv2.COLOR_BGR2GRAY)


def get_barcode(frame):
    """Get barcodes in frame."""
    return zbar.decode(frame)


# this is just a basic barcode scanner that reads in JSON data
# it has little sanitization, and works in black and white in order to cut
# down on memory usage.
def barcode_scanner(pipe, webcam):
    """Barcode scanner process"""
    common.set_procname("PLM-barcode")
    job = False
    while True:
        while True:
            try:
                data = get_frame(webcam)
            except cv2.error:
                print("Camera disabled. Sleeping...")
                time.sleep(20)
                continue
            detected_barcodes = get_barcode(data)
            if detected_barcodes != []:
                break
        if pipe.poll():
            job = pipe.recv()
            for barcode in detected_barcodes:
                data = barcode.data.decode()
                try:
                    data = json.loads(data)
                except json.decoder.JSONDecodeError:
                    continue
                    # basic sanitation
                if isinstance(data, dict):
                    keys = data.keys()
                    if (("type" in keys) and ("uid" in keys)):
                        output = {"type": data["type"], "uid": data["uid"]}
                        if job:
                            pipe.send(output)
                            job = False
