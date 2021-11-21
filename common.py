#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  common.py
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
"""Common Library for PyLibMan"""
import sys
import json
import copy
from ctypes import cdll, byref, create_string_buffer


def eprint(*args, **kwargs):
    """Make it easier for us to print to stderr"""
    print(*args, file=sys.stderr, **kwargs)


VERSION = "0.0.1-alpha0"
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
                   "duration": 0, # Number of days book has been in possession of UID in "possession" field
                   "due_date": 0} # UNIX time book is due to be returned
contact_info_template = {"phone_numbers": [], # list of phone numbers, stored as text
                         "emails": []}

check_out_history_template = {"uid": 0,
                              "checked_out": 0, # store as Unix time book was checked out. calculate the duration checked out from there on the fly
                              "due_date": 0, # store as Unix time due back. calculate time till due on the fly
                              "returned": False}


# Interface command templates
get_info_template = {"cmd_type": "get",
                "filter": {"field": None,
                           "compare": None},
                "column": "*"} # Get all entries by default
checkout_template = {"cmd_type": "checkout",
                     "data": {"book_uid": None,
                              "user_uid": None}}
checkin_template = {"cmd_type": "checkin",
                     "data": {"book_uid": None,
                              "user_uid": None}}
renew_template = {"cmd_type": "renew",
                     "data": {"book_uid": None,
                              "user_uid": None}}
change_template = {"cmd_type": "ch",
                   "settings": {"ch_field": None,
                                "new": None,
                                "search_term": None,
                                "search_value": None}}
delete_template = {"cmd_type": "del",
                   "filter": {"field": None,
                              "compare": None}}
add_template = {"cmd_type": "add",
                "data": None} # define this field following the db_struct template for the table in question
make_qr_template = {"cmd_type": "make_qr",
                    "type": None,
                    "uid": None}
print_qr_template = {"cmd_type": "print_qr",
                     "paths": []} # list of file paths to PNGs to print


def get_template(template_name):
    """Return a seperate instance of whatever template needed"""
    if template_name == "status":
        return copy.deepcopy(status_template)
    if template_name == "change":
        return copy.deepcopy(change_template)
    if template_name == "renew":
        return copy.deepcopy(renew_template)
    if template_name == "delete":
        return copy.deepcopy(delete_template)
    if template_name == "add":
        return copy.deepcopy(add_template)
    if template_name in ("checkin", "check_in"):
        return copy.deepcopy(checkin_template)
    if template_name in ("check_out", "checkout"):
        return copy.deepcopy(checkout_template)
    if template_name == "get":
        return copy.deepcopy(get_info_template)
    if template_name == "check_out_history":
        return copy.deepcopy(check_out_history_template)
    if template_name in ("contact_info_template", "contact_info"):
        return copy.deepcopy(contact_info_template)
    if template_name in ("db_books", "db_book", "book", "books"):
        return copy.deepcopy(db_struct_books)
    if template_name in ("db_users", "db_user", "user", "users"):
        return copy.deepcopy(db_struct_users)
    if template_name in ("make_qr", "make"):
        return copy.deepcopy(make_qr_template)
    if template_name in ("print_qr", "print"):
        return copy.deepcopy(print_qr_template)
    raise NameError(f"Template for '{template_name}' not found")


def unique(starting_list):
    """Function to get a list down to only unique elements"""
    # intilize a null list
    unique_list = []
    # traverse for all elements
    for each in starting_list:
        # check if exists in unique_list or not
        if each not in unique_list:
            unique_list.append(each)
    return unique_list


def set_procname(newname):
	libc = cdll.LoadLibrary('libc.so.6')    #Loading a 3rd party library C
	buff = create_string_buffer(len(newname) + 1) #Note: One larger than the name (man prctl says that)
	buff.value = bytes(newname, "utf-8")                 #Null terminated string as it should be
	libc.prctl(15, byref(buff), 0, 0, 0) #Refer to "#define" of "/usr/include/linux/prctl.h" for the misterious value 16 & arg[3..5] are zero as the man page says.
