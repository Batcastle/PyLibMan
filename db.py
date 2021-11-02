#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  db.py
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
"""Explain what this program does here!!!"""
import sqlite3 as sql
import json
import common
import time


def format_db_output(data, table):
    """Format output from the given table into a reasonable format"""
    if table in ("user", "users"):
        output = common.db_struct_users
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
        output = common.db_struct_books
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


def get_struct(db, full=True):
    output = "("
    if db in ("user", "users"):
        for each in common.db_struct_users:
            output = f"{output} {each}"
            if full:
                output = output + f" {common.db_struct_users[each]}"
            output = output + ","
        output = output[:-1] + ")"
    elif db in ("book", "books"):
        for each in common.db_struct_books:
            output = f"{output} {each}"
            if full:
                output = output + f" {common.db_struct_books[each]}"
            output = output + ","
        output = output[:-1] + ")"
    return output


def __get_command__(input, db_name, db):
    if db_name.lower() in ("user", "users"):
        name = "users"
    elif db_name.lower() in ("book", "books"):
        name = "books"
    command = f"SELECT * FROM {name}"
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
        output.append(format_db_output(each, name))
    return output


def __change_command__(input, db_name, db):
    if db_name.lower() in ("user", "users"):
        name = "users"
    elif db_name.lower() in ("book", "books"):
        name = "books"
    command = f"UPDATE {name} SET {input['settings']['ch_field']}="
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
    return output


def __del_command__(input, db_name, db):
    if db_name.lower() in ("user", "users"):
        name = "users"
    elif db_name.lower() in ("book", "books"):
        name = "books"
    command = f"DELETE FROM {name} WHERE {input['filter']['field']}="
    command = command + f"{input['filter']['compare']}"
    try:
        db.execute(command)
        output = success
    except:
        output = {"status": 0}
    return output


def user_table(pipe):
    """Interface to interact with the 'user' table"""
    db = sql.connect("library.db")
    success = {"status": 1}
    struct = get_struct("user", full=False)
    while True:
        output = None
        input = pipe.recv() # Receive our commands from the pipe
        if input["cmd_type"].lower() == "get":
            output = __get_command__(input, "users", db)
        elif input["cmd_type"].lower() == "ch":
            output = __change_command__(input, "users", db)
        elif input["cmd_type"].lower() == "del":
            output = __del_command__(input, "users", db)
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
    struct = get_struct("book", full=False)
    while True:
        output = None
        input = pipe.recv() # Receive our commands from the pipe
        if input["cmd_type"].lower() == "get":
            output = __get_command__(input, "books", db)
        elif input["cmd_type"].lower() == "ch":
            output = __change_command__(input, "books", db)
        elif input["cmd_type"].lower() == "del":
            output = __del_command__(input, "books", db)
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


def check_out(book_uid, user_uid, db):
    """Perform checkout of book"""
    # Update checkout status
    check_out_time = time.time()
    days = common.SETTINGS["default_checkout_days"]
    due_date = int(check_out_time + (days * 24 * 60 * 60))
    new_status = common.status_template
    new_status["status"] = "checked_out"
    new_status["possession"] = int(user_uid)
    # Round it to the nearest second. May
    new_status["due_date"] = due_date
    cmd = common.change_template
    cmd["settings"]["ch_field"] = "check_in_status"
    cmd["settings"]["new"] = new_status
    cmd["settings"]["search_term"] = "uid"
    cmd["settings"]["search_value"] = book_uid
    __change_command__(cmd, "books", db)

    # Check out status is now updated.
    # Update checkout history

    cmd = common.get_template
    cmd["filter"]["field"] = "uid"
    cmd["filter"]["compare"] = book_uid
    history = __get_command__(cmd, "books", db)
    history = data["check_out_history"]
    new_history = common.check_out_history_template
    new_history["uid"] = user_uid
    new_history["checked_out"] = check_out_time
    new_history["due_date"] = due_date
    history.insert(0, new_history)
    cmd["settings"]["ch_field"] = "check_out_history"
    cmd["settings"]["new"] = history
    __change_command__(cmd, "books", db)
