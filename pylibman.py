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
import os
import copy


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

# DB structures for easy generation of SQLite commands
db_struct_books = {"uid": "INTEGER",
                   "name": "TEXT",
                   "check_out_history": "TEXT", # Store this data a a JSON-formatted string
                   "check_in_status": "TEXT",   # Also store this as JSON, basic template found in `status_template`
                   "published": "INTEGER"}
db_struct_users = {"uid": "INTEGER",
                   "name": "TEXT",
                   "contact_info": "TEXT", # Store as JSON-formatted string, template in `contact_info_template`
                   "checked_out_books": "TEXT", # Store as list of book UIDs
                   "privs": "user"} # either `user` or `admin`
# JSON templates
status_template = {"status" : "checked_in", # can be one of: "checked_in", "checked_out", "unavailable", or "missing"
                   "possession": None, # UID of user who has (or should have) book, None if checked in
                   "duration": 0, # Number of days book has been  in possession of UID in "possession" field
                   "due_date": 0} # UNIX time book is due to be returned
contact_info_template = {"phone_numbers": [], # list of phone numbers, stored as text
                         "emails": []}

check_out_history_template = {"uid": 0,
                              "checked_out": 0, # store as Unix time book was checked out. calculate the duration checked out from there on the fly
                              "due_date": 0, # store as Unix time due back. calculate time till due on the fly
                              "returned": False}


# Interface command templates
get_template = {"cmd_type": "get",
                "filter": {"field": None,
                           "compare": None}}
change_template = {"cmd_type": "ch",
                   "settings": {"ch_field": None,
                                "new": None,
                                "search_term": None,
                                "search_value": None}}
delete_template = {"cmd_type": "del",
                   "filter": {"field": None,
                              "compare": None}}
add_template = {"cmd_type": "add",
                "data": {}} # define this field following the db_struct template for the table in question

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


def __get_struct__(db, full=True):
    output = "("
    if db in ("user", "users"):
        for each in db_struct_users:
            output = f"{output} {each}"
            if full:
                output = output + f" {db_struct_users[each]}"
            output = output + ","
        output = output[:-1] + ")"
    elif db in ("book", "books"):
        for each in db_struct_books:
            output = f"{output} {each}"
            if full:
                output = output + f" {db_struct_books[each]}"
            output = output + ","
        output = output[:-1] + ")"
    return output


def format_db_output(data, table):
    """Format output from the given table into a reasonable format"""
    if table in ("user", "users"):
        output = db_struct_users
        output["uid"] = data[0]
        output["name"] = data[1]
        try:
            output["contact_info"] = json.loads(data[2])
        except json.decoder.JSONDecodeError:
            output["contact_info"] = data[2]
        try:
            output["checked_out_books"] = json.loads(data[3])
        except json.decoder.JSONDecodeError:
            output["checked_out_books"] = data[3]
        output["privs"] = data[4]
    elif table in ("book", "books"):
        output = db_struct_books
        output["uid"] = data[0]
        output["name"] = data[1]
        try:
            output["check_out_history"] = json.loads(data[2])
        except json.decoder.JSONDecodeError:
            output["check_out_history"] = data[2]
        try:
            output["check_in_status"] = json.loads(data[3])
        except json.decoder.JSONDecodeError:
            output["check_in_status"] = data[3]
        output["published"] = data[4]
    return output


def user_table(pipe):
    """Interface to interact with the 'user' table"""
    db = sql.connect("library.db")
    success = {"status": 1}
    struct = __get_struct__("user", full=False)
    while True:
        output = None
        input = pipe.recv() # Receive our commands from the pipe
        if input["cmd_type"].lower() == "get":
            command = "SELECT * FROM users"
            if "filter" in input.keys():
                if input["filter"] != None:
                    if None not in (input["filter"]["field"],
                                    input["filter"]["compare"]):
                        command = f"{command} WHERE {input['filter']['field']}"
                        if isinstance(input['filter']['compare'], str):
                            command = f"{command}=\"{input['filter']['compare']}\""
                        elif isinstance(input['filter']['compare'], (dict, list)):
                            command = f"{command}='{json.dumps(input['filter']['compare'])}'"
                        else:
                            command = f"{command}={input['filter']['compare']}"
            unformatted = list(db.execute(command).fetchall())
            output = []
            for each in unformatted:
                output.append(format_db_output(each, "user"))
        elif input["cmd_type"].lower() == "ch":
            command = f"UPDATE users SET {input['settings']['ch_field']}="
            if isinstance(input['settings']['new'], str):
                command = command + f"\"{input['settings']['new']}\" WHERE "
            elif isinstance(input['settings']['new'], (dict, list)):
                command = command + f"'{json.dumps(input['settings']['new'])}' WHERE "
            else:
                command = command + f"{input['settings']['new']} WHERE "
            command = command + f"{input['settings']['search_term']}="
            if isinstance(input['settings']['search_value'], str):
                command = command + f"\"{input['settings']['search_value']}\""
            elif isinstance(input['settings']['search_value'], (dict, list)):
                command = command + f"'{json.dumps(input['settings']['search_value'])}'"
            else:
                command = command + f"{input['settings']['search_value']}"
            try:
                db.execute(command)
                output = success
            except:
                output = {"status": 0}
        elif input["cmd_type"].lower() == "del":
            command = f"DELETE FROM users WHERE {input['filter']['field']}="
            command = command + f"{input['filter']['compare']}"
            try:
                db.execute(command)
                output = success
            except:
                output = {"status": 0}
        elif input["cmd_type"].lower() == "add":
            command = "INSERT INTO users VALUES"
            data = f"({input['data']['uid']}, '{input['data']['name']}',"
            data = data + f"'{json.dumps(input['data']['contact_info'])}',"
            data = data + f"'{json.dumps(input['data']['checked_out_books'])}',"
            data = data + f"'{input['data']['privs']}')"
            command = command + " " + data
            try:
                db.execute(command)
                output = success
            except:
                output = {"status": 0}
        db.commit()
        pipe.send(output)


def book_table(pipe):
    """Interface to interact with the 'book' table"""
    db = sql.connect("library.db")
    success = {"status": 1}
    struct = __get_struct__("book", full=False)
    while True:
        output = None
        input = pipe.recv() # Receive our commands from the pipe
        if input["cmd_type"].lower() == "get":
            command = "SELECT * FROM books"
            if "filter" in input.keys():
                if input["filter"] != None:
                    if None not in (input["filter"]["field"],
                                    input["filter"]["compare"]):
                        command = f"{command} WHERE {input['filter']['field']}"
                        if isinstance(input['filter']['compare'], str):
                            command = f"{command}=\"{input['filter']['compare']}\""
                        elif isinstance(input['filter']['compare'], (dict, list)):
                            command = f"{command}='{json.dumps(input['filter']['compare'])}'"
                        else:
                            command = f"{command}={input['filter']['compare']}"
            unformatted = list(db.execute(command).fetchall())
            output = []
            for each in unformatted:
                output.append(format_db_output(each, "books"))
        elif input["cmd_type"].lower() == "ch":
            command = f"UPDATE books SET {input['settings']['ch_field']}="
            if isinstance(input['settings']['new'], str):
                command = command + f"\"{input['settings']['new']}\" WHERE "
            elif isinstance(input['settings']['new'], (dict, list)):
                command = command + f"'{json.dumps(input['settings']['new'])}' WHERE "
            else:
                command = command + f"{input['settings']['new']} WHERE "
            command = command + f"{input['settings']['search_term']}="
            if isinstance(input['settings']['search_value'], str):
                command = command + f"\"{input['settings']['search_value']}\""
            elif isinstance(input['settings']['search_value'], (dict, list)):
                command = command + f"'{json.dumps(input['settings']['search_value'])}'"
            else:
                command = command + f"{input['settings']['search_value']}"
            try:
                db.execute(command)
                output = success
            except:
                output = {"status": 0}
        elif input["cmd_type"].lower() == "del":
            command = f"DELETE FROM books WHERE {input['filter']['field']}="
            command = command + f"{input['filter']['compare']}"
            try:
                db.execute(command)
                output = success
            except:
                output = {"status": 0}
        elif input["cmd_type"].lower() == "add":
            command = "INSERT INTO books VALUES"
            data = f"({input['data']['uid']}, '{input['data']['name']}',"
            data = data + f"'{json.dumps(input['data']['check_out_history'])}',"
            data = data + f"'{json.dumps(input['data']['check_in_status'])}',"
            data = data + f"'{input['data']['published']}')"
            command = command + " " + data
            try:
                db.execute(command)
                output = success
            except:
                output = {"status": 0}
        db.commit()
        pipe.send(output)


parent_conn, bar_pipe = multiprocessing.Pipe()
parent_conn2, user_pipe = multiprocessing.Pipe()
parent_conn3, book_pipe = multiprocessing.Pipe()
procs = []
# procs.append(multiprocessing.Process(target=barcode_scanner, args=(parent_conn,)))
procs.append(multiprocessing.Process(target=book_table, args=(parent_conn3,)))
procs.append(multiprocessing.Process(target=user_table, args=(parent_conn2,)))
DB = sql.connect("library.db")
tables = DB.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
if len(tables) < 1:
    print("Tables do not exist. Generating...")
    DB.execute(f"CREATE TABLE users {__get_struct__('user')}")
    DB.execute(f"CREATE TABLE books {__get_struct__('book')}")
    DB.commit()
else:
    print("Tables exist!")


for each in procs:
    each.start()

# DEMO USER DB INTERFACE
print("USER DB INTERFACE DEMO")
add = add_template
add["data"] = db_struct_users
add["data"]["uid"] = 1000
add["data"]["name"] = "TestUser Test TestUserMan"
add["data"]["contact_info"] = contact_info_template
add["data"]["contact_info"]["phone_numbers"].append("000-000-0000")
add["data"]["contact_info"]["emails"].append("test@example.com")
add["data"]["checked_out_books"] = []

user_pipe.send(add)
print(user_pipe.recv())


get = get_template
get["filter"]["field"] = "uid"
get["filter"]["compare"] = 1000

user_pipe.send(get)
print(json.dumps(user_pipe.recv(), indent=1))

ch = change_template
ch["settings"]["search_term"] = "uid"
ch["settings"]["search_value"] = 1000
ch["settings"]["ch_field"] = "contact_info"
ch["settings"]["new"] = contact_info_template
ch["settings"]["new"]["phone_numbers"] = ["828-850-2474"]
ch["settings"]["new"]["emails"] = ["test@example.com"]

user_pipe.send(ch)
print(user_pipe.recv())

delete = delete_template
delete["filter"]["field"] = "uid"
delete["filter"]["compare"] = 1000

user_pipe.send(get)
print(json.dumps(user_pipe.recv(), indent=1))

user_pipe.send(delete)
print(user_pipe.recv())


# DEMO BOOKS DB INTERFACE
print("BOOKS DB INTERFACE DEMO")
add = add_template
add["data"] = db_struct_books
add["data"]["uid"] = 1000
add["data"]["name"] = "Citizenship in the Community"
add["data"]["check_out_history"] = {}
add["data"]["check_in_status"] = status_template
add["data"]["published"] = 2021

book_pipe.send(add)
print(book_pipe.recv())

book_pipe.send(get)
print(json.dumps(book_pipe.recv(), indent=1))

ch = change_template
ch["settings"]["search_term"] = "uid"
ch["settings"]["search_value"] = 1000
ch["settings"]["ch_field"] = "check_out_history"
ch["settings"]["new"] = {0: check_out_history_template}
ch["settings"]["new"][0]["uid"] = 1000
ch["settings"]["new"][0]["checked_out"] = time.time()
due_date = time.time() + 1814400
ch["settings"]["new"][0]["due_date"] = due_date

book_pipe.send(ch)
print(book_pipe.recv())

ch = change_template
ch["settings"]["search_term"] = "uid"
ch["settings"]["search_value"] = 1000
ch["settings"]["ch_field"] = "check_in_status"
ch["settings"]["new"] = status_template
ch["settings"]["new"]["status"] = "checked_out"
ch["settings"]["new"]["possession"] = 1000
ch["settings"]["new"]["due_date"] = due_date

book_pipe.send(ch)
print(book_pipe.recv())

book_pipe.send(get)
print(json.dumps(book_pipe.recv(), indent=1))

user_pipe.send(delete)
print(user_pipe.recv())

# barcoder_proc.start()
# count = 0
# while True:
#     data = child_conn.recv()
#     print(json.dumps(data, indent=1))
#     count += 1
#     print(count)
#     time.sleep(1)
# barcoder_proc.join()
# WEBCAM.release()
