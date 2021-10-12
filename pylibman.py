#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  pylibman.py
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
"""Python Library Manager - Manage inventory, check in/out out books, track who has what book, and more!"""
from __future__ import print_function
import sys
import cv2
import pyzbar.pyzbar as zbar
import sqlite3 as sql
import json
import numpy as np
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import time
import multiprocessing


def __eprint__(*args, **kwargs):
    """Make it easier for us to print to stderr"""
    print(*args, file=sys.stderr, **kwargs)


if sys.version_info[0] == 2:
    __eprint__("Please run with Python 3 as Python 2 is End-of-Life.")
    exit(2)

# Set up vars
ARGC = len(sys.argv)
VERSION = "0.0.0-alpha0"
HELP = f"""PyLibMan, Version {VERSION}

The rest of this will be assigned later."""

# read settings
with open("settings.json", "r") as file:
    SETTINGS = json.load(file)

# Initialize Webcam
WEBCAM = cv2.VideoCapture(0)


def get_frame():
    """Get a frame from the Webcam"""
    gray = cv2.cvtColor(np.array(WEBCAM.read()[1]), cv2.COLOR_BGR2GRAY)
    return gray


def get_barcode(frame):
    """Get barcodes in frame."""
    return zbar.decode(frame)


# this is just a basic barcode scanner that reads in JSON data
# it has little sanitization, and works in black and white in order to cut
# down on memory usage.
def barcode_scanner(pipe):
    """Barcode scanner process"""
    while True:
        last_sent = None
        try:
            data = get_frame()
        except cv2.error:
            print("Camera disabled. Sleeping...")
            time.sleep(20)
        detected_barcodes = get_barcode(data)
        for barcode in detected_barcodes:
            data = barcode.data.decode()
            try:
                data = json.loads(data)
            except json.decoder.JSONDecodeError:
                continue
            if data != last_sent:
                pipe.send(data)
                last_sent = data
        time.sleep(1)


parent_conn, child_conn = multiprocessing.Pipe()
barcoder_proc = multiprocessing.Process(target=barcode_scanner, args=(parent_conn,))
barcoder_proc.start()
count = 0
while True:
    data = child_conn.recv()
    print(json.dumps(data, indent=1))
    count += 1
    print(count)
    time.sleep(1)
barcoder_proc.join()
WEBCAM.release()
