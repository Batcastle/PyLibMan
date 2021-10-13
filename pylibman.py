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



if sys.version_info[0] == 2:
    common.eprint("Please run with Python 3 as Python 2 is End-of-Life.")
    exit(2)

# Set up vars
ARGC = len(sys.argv)

# Initialize Webcam
WEBCAM = cv2.VideoCapture(0)

parent_conn, bar_pipe = multiprocessing.Pipe()
parent_conn2, user_pipe = multiprocessing.Pipe()
parent_conn3, book_pipe = multiprocessing.Pipe()
procs = []
procs.append(multiprocessing.Process(target=barcode.barcode_scanner,
                                     args=(parent_conn, WEBCAM)))
procs.append(multiprocessing.Process(target=db.book_table, args=(parent_conn3,)))
procs.append(multiprocessing.Process(target=db.user_table, args=(parent_conn2,)))
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
add = common.add_template
add["data"] = common.db_struct_users
add["data"]["uid"] = 1000
add["data"]["name"] = "TestUser Test TestUserMan"
add["data"]["contact_info"] = common.contact_info_template
add["data"]["contact_info"]["phone_numbers"].append("000-000-0000")
add["data"]["contact_info"]["emails"].append("test@example.com")
add["data"]["checked_out_books"] = []

user_pipe.send(add)
print(user_pipe.recv())


get = common.get_template
get["filter"]["field"] = "uid"
get["filter"]["compare"] = 1000

user_pipe.send(get)
print(json.dumps(user_pipe.recv(), indent=1))

ch = common.change_template
ch["settings"]["search_term"] = "uid"
ch["settings"]["search_value"] = 1000
ch["settings"]["ch_field"] = "contact_info"
ch["settings"]["new"] = common.contact_info_template
ch["settings"]["new"]["phone_numbers"] = ["828-850-2474"]
ch["settings"]["new"]["emails"] = ["test@example.com"]

user_pipe.send(ch)
print(user_pipe.recv())

delete = common.delete_template
delete["filter"]["field"] = "uid"
delete["filter"]["compare"] = 1000

user_pipe.send(get)
print(json.dumps(user_pipe.recv(), indent=1))

user_pipe.send(delete)
print(user_pipe.recv())


# DEMO BOOKS DB INTERFACE
print("BOOKS DB INTERFACE DEMO")
add = common.add_template
add["data"] = common.db_struct_books
add["data"]["uid"] = 1000
add["data"]["name"] = "Citizenship in the Community"
add["data"]["check_out_history"] = {}
add["data"]["check_in_status"] = common.status_template
add["data"]["published"] = 2021

book_pipe.send(add)
print(book_pipe.recv())

book_pipe.send(get)
print(json.dumps(book_pipe.recv(), indent=1))

ch = common.change_template
ch["settings"]["search_term"] = "uid"
ch["settings"]["search_value"] = 1000
ch["settings"]["ch_field"] = "check_out_history"
ch["settings"]["new"] = {0: common.check_out_history_template}
ch["settings"]["new"][0]["uid"] = 1000
ch["settings"]["new"][0]["checked_out"] = time.time()
due_date = time.time() + 1814400
ch["settings"]["new"][0]["due_date"] = due_date

book_pipe.send(ch)
print(book_pipe.recv())

ch = common.change_template
ch["settings"]["search_term"] = "uid"
ch["settings"]["search_value"] = 1000
ch["settings"]["ch_field"] = "check_in_status"
ch["settings"]["new"] = common.status_template
ch["settings"]["new"]["status"] = "checked_out"
ch["settings"]["new"]["possession"] = 1000
ch["settings"]["new"]["due_date"] = due_date

book_pipe.send(ch)
print(book_pipe.recv())

book_pipe.send(get)
print(json.dumps(book_pipe.recv(), indent=1))

user_pipe.send(delete)
print(user_pipe.recv())

count = 0
while True:
    data = bar_pipe.recv()
    print(json.dumps(data, indent=1))
    count += 1
    print(count)
    time.sleep(1)
barcoder_proc.join()
WEBCAM.release()
