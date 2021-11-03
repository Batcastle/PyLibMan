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
import sqlite3 as sql
import json
import time
import multiprocessing
import os
import common
import barcode
import db
import ui



if sys.version_info[0] == 2:
    common.eprint("Please run with Python 3 as Python 2 is End-of-Life.")
    exit(2)

# Set up vars
ARGC = len(sys.argv)


def qr_query(request, pipe_handle):
    """Make a request from QR Code data"""
    get = common.get_template("get")
    get["filter"]["field"] = "uid"
    get["filter"]["compare"] = request["uid"]
    pipe_handle.send(get)
    return pipe_handle.recv()


# Initialize Webcam
WEBCAM = cv2.VideoCapture(0)

parent_conn, bar_pipe = multiprocessing.Pipe()
parent_conn2, user_pipe = multiprocessing.Pipe()
parent_conn3, book_pipe = multiprocessing.Pipe()
parent_conn4, ui_pipe = multiprocessing.Pipe()
procs = []
procs.append(multiprocessing.Process(target=barcode.barcode_scanner,
                                     args=(parent_conn, WEBCAM)))
procs.append(multiprocessing.Process(target=db.book_table, args=(parent_conn3,)))
procs.append(multiprocessing.Process(target=db.user_table, args=(parent_conn2,)))
procs.append(multiprocessing.Process(target=ui.show, args=(parent_conn4,)))
DB = sql.connect("library.db")
tables = DB.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
if len(tables) < 1:
    print("Tables do not exist. Generating...")
    DB.execute(f"CREATE TABLE users {db.get_struct('user')}")
    DB.execute(f"CREATE TABLE books {db.get_struct('book')}")
    DB.commit()
else:
    print("Tables exist!")
DB.close()

for each in procs:
    each.start()

# DEMO USER DB INTERFACE
print("USER DB INTERFACE DEMO")
add = common.get_template("add")
add["data"] = common.get_template("db_users")
add["data"]["uid"] = 1000
add["data"]["name"] = "TestUser Test TestUserMan"
add["data"]["contact_info"] = common.get_template("contact_info_template")
add["data"]["contact_info"]["phone_numbers"].append("000-000-0000")
add["data"]["contact_info"]["emails"].append("test@example.com")
add["data"]["checked_out_books"] = []
add["data"]["privs"] = "admin"

print(add)

user_pipe.send(add)
print(user_pipe.recv())


get = common.get_template("get")
get["filter"]["field"] = "uid"
get["filter"]["compare"] = 1000

user_pipe.send(get)
print(json.dumps(user_pipe.recv(), indent=1))

ch = common.get_template("change")
ch["settings"]["search_term"] = "uid"
ch["settings"]["search_value"] = 1000
ch["settings"]["ch_field"] = "contact_info"
ch["settings"]["new"] = common.get_template("contact_info_template")
ch["settings"]["new"]["phone_numbers"] = ["828-850-2474"]
ch["settings"]["new"]["emails"] = ["test@example.com"]

user_pipe.send(ch)
print(user_pipe.recv())

delete = common.get_template("delete")
delete["filter"]["field"] = "uid"
delete["filter"]["compare"] = 1000

user_pipe.send(get)
print(json.dumps(user_pipe.recv(), indent=1))

# user_pipe.send(delete)
# print(user_pipe.recv())


# DEMO BOOKS DB INTERFACE
print("BOOKS DB INTERFACE DEMO")
add = common.get_template('add')
add["data"] = common.get_template("db_books")
add["data"]["uid"] = 1000
add["data"]["name"] = "Citizenship in the Community"
add["data"]["check_out_history"] = []
add["data"]["check_in_status"] = common.get_template("status")
add["data"]["published"] = 2021

book_pipe.send(add)
print(book_pipe.recv())

book_pipe.send(get)
print(json.dumps(book_pipe.recv(), indent=1))

# user_pipe.send(delete)
# print(user_pipe.recv())

while True:
    try:
        if ui_pipe.poll():
            ui_request = ui_pipe.recv()
            if ui_request == "shut_down":
                break
            elif ui_request == "get_barcode":
                while True:
                    bar_pipe.send(True)
                    data = bar_pipe.recv()
                    if data["type"] in ("user", "users"):
                        data = qr_query(data, user_pipe)
                        break
                    elif data["type"] in ("book", "books"):
                        data = qr_query(data, book_pipe)
                        break
                    print(data)
                ui_pipe.send(data)
            elif isinstance(ui_request, dict):
                if ui_request["table"] in ("user", "users"):
                    user_pipe.send(ui_request["command"])
                    ui_pipe.send(user_pipe.recv())
                elif ui_request["table"] in ("book", "books"):
                    book_pipe.send(ui_request["command"])
                    ui_pipe.send(book_pipe.recv())
                elif ui_request["table"] == "both":
                    user_pipe.send(ui_request["command"])
                    book_pipe.send(ui_request["command"])
                    ui_pipe.send((user_pipe.recv(), book_pipe.recv()))

        else:
            time.sleep(1)
            continue
    except KeyboardInterrupt:
        print("Shutting down...")
        break
# Shutdown and clean up
WEBCAM.release()
for each in procs:
    each.kill()
    each.terminate()
    each.join()
time.sleep(3)
os.remove("library.db")
