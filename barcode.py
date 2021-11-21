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
import qrcode
from PIL import Image as img
import os
import subprocess
import common


def get_frame(webcam):
    """Get a frame from the Webcam"""
    return cv2.cvtColor(np.array(webcam.read()[1]), cv2.COLOR_BGR2GRAY)


def get_barcode(frame):
    """Get barcodes in frame."""
    return zbar.decode(frame)


def generate_barcode(type, uid):
    """Generate a QR Code"""
    # Generate QR Code
    path = "/tmp/qr_codes"
    data = {"type": type, "uid": uid}
    qr = qrcode.QRCode()
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    if not os.path.isdir(path):
        print("MAKING DIR")
        os.mkdir(path)
    image.save(f"{path}/{type}_{uid}.png")
    print(f"Saved file to {path}/{type}_{uid}.png")
    return f"{path}/{type}_{uid}.png"


def print_barcode(paths):
    """Print QR codes"""
    images = []
    recursion_point = None
    for each in paths:
        images.append(img.open(each))
    canvas = img.new("RGB", (2550, 3300), color=(255, 255, 255))
    # we can user canvas.paste() to paste images into the canvas, then just save the canvas as a file
    attach_point = [0, 0]
    canvas.paste(images[0], tuple(attach_point))
    attach_point = [5, 0]
    for each in images[1:]:
        size = each.size
        attach_point[0] = size[0] + attach_point[0] + 5
        if ((size[0] + attach_point[0] + 5) >= 2550): # if the image goes over the right edge, wrap
            attach_point[0] = 0
            attach_point[1] = attach_point[1] + size[1] + 5
        print(attach_point)
        if attach_point[1] >= 3300: # if the image goes over the bottom edge, stop. Mark recursion point
            recursion_point = image.index(each)
            break
        canvas.paste(each, tuple(attach_point))
        attach_point[0] = attach_point[0] + 5
    output = f"{int(time.time())}.png"
    canvas.save(output)
    if recursion_point == None:
        return output
    add = print_barcode(paths[recursion_point:])
    if isinstance(add, list):
        return [output] + add
    return [output, add]


# this is just a basic barcode scanner that reads in JSON data
# it has little sanitization, and works in black and white in order to cut
# down on memory usage.
def barcode_scanner(pipe, webcam):
    """Barcode scanner process"""
    common.set_procname("PLM-barcode")
    job = False
    while True:
        while True:
            loop = False
            try:
                data = get_frame(webcam)
            except cv2.error:
                print("Camera disabled. Sleeping...")
                time.sleep(1)
                loop = True
            if pipe.poll():
                break
            if loop:
                continue
            detected_barcodes = get_barcode(data)
            if detected_barcodes != []:
                break
        if pipe.poll():
            job = pipe.recv()
            if job == "get_barcode":
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
            elif isinstance(job, dict):
                print("Abnormal job!")
                if job["cmd_type"] == "make_qr":
                    # generate QR Code
                    print("Making QR!")
                    output = generate_barcode(job["type"], job["uid"])
                elif job["cmd_type"] == "print_qr":
                    print("Generating images for printing!")
                    output = print_barcode(job["paths"])
            pipe.send(output)
            job = None
