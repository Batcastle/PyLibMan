#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  ui.py
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
"""UI for PyLibMan"""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import common
import time
import random


class PyLibMan_UI(Gtk.Window):
    """Main UI Window"""
    def __init__(self, pipe):
        """Initialize the Window"""
        Gtk.Window.__init__(self, title="Python Library Manager")
        self.grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.grid)
        self.set_icon_name("dictionary")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        # Make sure the whole class can access the pipe to the main thread
        self.pipe = pipe
        # Make user data available class-wide
        self.user = None
        # Make our tabs
        self.page0 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.page1 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.page2 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.page3 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        self.page4 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        # Book UID so we can get the data we need
        self.book_uid = None

        # enable window to receive key press events
        self.connect("key-press-event", self.on_key_press_event)

        self.reset("")

    def on_key_press_event(self, widget, event):
        """Handles keyy press events for window"""
        if event.keyval == 65307: #Esc key code
            self.keys["esc"]("clicked")
        elif event.keyval in (65421, 65293): # key codes for enter on both numpad and normal keyboard
            self.keys["enter"]("clicked")


    def reset(self, widget):
        """make/remake tabs"""
        children = self.page0.get_children()
        for each0 in children:
            self.page0.remove(each0)

        children = self.page1.get_children()
        for each0 in children:
            self.page1.remove(each0)

        children = self.page2.get_children()
        for each0 in children:
            self.page2.remove(each0)

        children = self.page3.get_children()
        for each0 in children:
            self.page3.remove(each0)

        children = self.page4.get_children()
        for each0 in children:
            self.page4.remove(each0)

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>Check Out</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.page0.attach(label, 1, 1, 5, 1)

        label1 = Gtk.Label()
        label1.set_markup("""<b>Waiting for Book...</b>""")
        label1.set_justify(Gtk.Justification.CENTER)
        label1 = self._set_default_margins(label1)
        self.page0.attach(label1, 1, 2, 5, 1)

        label2 = Gtk.Label()
        label2.set_markup("""----""")
        label2.set_justify(Gtk.Justification.CENTER)
        label2 = self._set_default_margins(label2)
        self.page0.attach(label2, 1, 3, 5, 1)

        button = Gtk.Button.new_with_label("Start Scanning")
        button.connect("clicked", self.check_out_scanner)
        button = self._set_default_margins(button)
        self.page0.attach(button, 1, 4, 1, 1)

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>Check In</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.page1.attach(label, 1, 1, 5, 1)

        label1 = Gtk.Label()
        label1.set_markup("""<b>Waiting for Book...</b>""")
        label1.set_justify(Gtk.Justification.CENTER)
        label1 = self._set_default_margins(label1)
        self.page1.attach(label1, 1, 2, 5, 1)

        label2 = Gtk.Label()
        label2.set_markup("""----""")
        label2.set_justify(Gtk.Justification.CENTER)
        label2 = self._set_default_margins(label2)
        self.page1.attach(label2, 1, 3, 5, 1)

        button = Gtk.Button.new_with_label("Start Scanning")
        button.connect("clicked", self.check_in_scanner)
        button = self._set_default_margins(button)
        self.page1.attach(button, 1, 4, 1, 1)

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>Renew</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.page2.attach(label, 1, 1, 5, 1)

        label1 = Gtk.Label()
        label1.set_markup("""<b>Waiting for Book...</b>""")
        label1.set_justify(Gtk.Justification.CENTER)
        label1 = self._set_default_margins(label1)
        self.page2.attach(label1, 1, 2, 5, 1)

        label2 = Gtk.Label()
        label2.set_markup("""----""")
        label2.set_justify(Gtk.Justification.CENTER)
        label2 = self._set_default_margins(label2)
        self.page2.attach(label2, 1, 3, 5, 1)

        button = Gtk.Button.new_with_label("Start Scanning")
        button.connect("clicked", self.renew_scanner)
        button = self._set_default_margins(button)
        self.page2.attach(button, 1, 4, 1, 1)

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>User Administration</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.page3.attach(label, 1, 1, 5, 1)

        button = Gtk.Button.new_with_label("Add User")
        button.connect("clicked", self.add_user_ui)
        button = self._set_default_margins(button)
        self.page3.attach(button, 1, 2, 1, 1)

        button = Gtk.Button.new_with_label("Remove User")
        button.connect("clicked", self.remove_user_ui)
        button = self._set_default_margins(button)
        self.page3.attach(button, 2, 2, 1, 1)

        # Also need Edit User and Relinquish Admin Privs

        # button = Gtk.Button.new_with_label("Edit Book Info")
        # button.connect("clicked", self.edit_book_ui)
        # button = self._set_default_margins(button)
        # self.page4.attach(button, 1, 3, 1, 1)

        button = Gtk.Button.new_with_label("Relinquish Admin Rights")
        button.connect("clicked", self.remove_admin_rights)
        button = self._set_default_margins(button)
        self.page3.attach(button, 2, 3, 1, 1)

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>Book Administration</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.page4.attach(label, 1, 1, 5, 1)

        button = Gtk.Button.new_with_label("Add Book")
        button.connect("clicked", self.add_book_ui)
        button = self._set_default_margins(button)
        self.page4.attach(button, 1, 2, 1, 1)

        button = Gtk.Button.new_with_label("Remove Book")
        button.connect("clicked", self.remove_book_ui)
        button = self._set_default_margins(button)
        self.page4.attach(button, 2, 2, 1, 1)

        button = Gtk.Button.new_with_label("View Books")
        button.connect("clicked", self.view_titles_ui)
        button = self._set_default_margins(button)
        self.page4.attach(button, 2, 3, 1, 1)

        # button = Gtk.Button.new_with_label("Edit Book Info")
        # button.connect("clicked", self.edit_book_ui)
        # button = self._set_default_margins(button)
        # self.page4.attach(button, 1, 3, 1, 1)

        if self.user is None:
            self.main_menu("clicked")
        else:
            if self.user["privs"] == "admin":
                self.admin_menu("clicked")
            else:
                self.user_menu("clicked")

    def view_titles_ui(self, widget):
        """View Book Titles, or order to quickly find a specific book"""
        self.clear_window()

        self.keys = {"enter": self.view_books_ui,
                     "esc": self.reset}

        cmd = common.get_template("get")
        cmd["column"] = "name"
        del cmd["filter"]
        cmd = {"table": "book", "command": cmd}
        self.pipe.send(cmd)

        # While those threads are working, we can get our UI made
        label = Gtk.Label()
        label.set_markup("<span size='x-large'><b>View Books</b></span>")
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 1, 2, 1)

        label = Gtk.Label()
        label.set_markup("""
        <b>Pick a title to view info on</b>
        """)
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 2, 2, 1)

        titles = Gtk.ComboBoxText.new()
        titles = self._set_default_margins(titles)
        # hold off on finishing setting up this widget till the end to give the DB time to work

        button = Gtk.Button.new_with_label("<-- Back")
        button.connect("clicked", self.reset)
        button = self._set_default_margins(button)
        self.grid.attach(button, 1, 4, 1, 1)

        button = Gtk.Button.new_with_label("View Book")
        button.connect("clicked", self.view_books_ui)
        button = self._set_default_margins(button)
        self.grid.attach(button, 2, 4, 1, 1)

        # NOW get our data out of the pipe
        data = self.pipe.recv()
        # make sure the data is a sorted list of unique entries
        if isinstance(data, tuple):
            data = list(data)
        data = common.unique(data)
        data.sort()

        # add them to the drop down box
        for each in data:
            titles.append(each, each)
        titles.connect("changed", self.select_title)
        self.grid.attach(titles, 1, 3, 2, 1)

        self.show_all()

    def select_title(self, widget):
        """Grab book title to view"""
        self.book_uid = widget.get_active_id()

    def view_books_ui(self, widget):
        """View all books with a specific title"""
        self.clear_window()

        self.keys = {"enter": self.view_titles_ui,
                     "esc": self.view_titles_ui}

        cmd = common.get_template("get")
        cmd["filter"]["field"] = "name"
        cmd["filter"]["compare"] = self.book_uid
        cmd = {"table": "book", "command": cmd}
        self.pipe.send(cmd)

        label = Gtk.Label()
        label.set_markup(f"<span size='x-large'><b>{self.book_uid}</b></span>")
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 1, 2, 1)


        data = self.pipe.recv()
        for each in enumerate(data):
            label = Gtk.Label()
            label = self._set_default_margins(label)
            label.set_markup(f"<b>UID</b>: {data[each[0]]['uid']} - <b>Published</b>: {data[each[0]]['published']} - <b>Status</b>: {data[each[0]]['check_in_status']['status'].replace('_', ' ')}")
            self.grid.attach(label, 1, 2 + each[0], 2, 1)

        button = Gtk.Button.new_with_label("<-- Back")
        button.connect("clicked", self.view_titles_ui)
        button = self._set_default_margins(button)
        self.grid.attach(button, 1, 3 + len(data), 1, 1)

        self.book_uid = None
        self.show_all()

    def remove_admin_rights(self, widget):
        """Remove admin rights"""
        # have a UI confirming the user wants to do this
        self.clear_window()

        label = Gtk.Label()
        label.set_markup("<span size='x-large'><b>Relinquish Admin Rights</b></span>")
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 1, 2, 1)

        label = Gtk.Label()
        label.set_markup("""
        <b>Are you sure you want to relinquish your administrator privileges?</b>

        This action requires help from another administrator to undo.
        """)
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 2, 2, 1)

        button = Gtk.Button.new_with_label("Cancel")
        button.connect("clicked", self.reset)
        button = self._set_default_margins(button)
        self.grid.attach(button, 1, 3, 1, 1)

        button = Gtk.Button.new_with_label("Confirm")
        button.connect("clicked", self._remove_admin_rights)
        button = self._set_default_margins(button)
        self.grid.attach(button, 2, 3, 1, 1)

        self.show_all()

    def _remove_admin_rights(self, widget):
        """Remove admin rights"""
        # the change needs to be made to the DB too, to be persistant
        # this will just make the change apply to this session
        # logging out and back in would reset this value
        self.user["privs"] = "user"
        self.reset("clicked")


    def check_out_scanner(self, widget):
        """Check out scanner"""
        self.pipe.send("get_barcode")
        children = self.page0.get_children()
        element = []
        for each in children:
            # This is a bit of a hack but works
            if "<class 'gi.overrides.Gtk.Label'>" == str(type(each)):
                element.append(each)
        for each in element:
            if ((each.get_text() == "----") or ("uid" in each.get_text()) or (each.get_text() in ("Book Not Found", "Not a Book", "An Error has occured")) or ("due back by" in each.get_text())):
                details = each
            elif (("Waiting for Book..." in each.get_text()) or ("Book Found" in each.get_text()) or ("Checked Out" in each.get_text())):
                status = each
        input = self.pipe.recv()
        if input == []:
            details.set_markup("Book Not Found")
            # see if button exists. Delete if so
            for each in children:
                if each.get_label() == "Check Out Book":
                    self.page0.remove(each)
                    break
        elif "status" in input[0]:
            if input[0]["status"] == 0:
                details.set_markup("An Error has occured")
        elif "check_in_status" not in input[0]:
            details.set_markup("Not a Book")
            # see if button exists. Delete if so
            for each in children:
                if each.get_label() == "Check Out Book":
                    self.page0.remove(each)
                    break
        else:
            self.book_uid = input[0]["uid"]
            text = f"""
            <b>uid</b>: {input[0]["uid"]}
           <b>Name</b>: {input[0]["name"]}
         <b>Status</b>: {input[0]["check_in_status"]["status"]}"""
            details.set_markup(text)
            status.set_markup("<b>Book Found</b>")
            # See if button exists. If not, add button to send checkout command
            exists = False
            for each in children:
                if each.get_label() == "Check Out Book":
                    exists = True
            if not exists:
                button = Gtk.Button.new_with_label("Check Out Book")
                button.connect("clicked", self.check_out)
                button = self._set_default_margins(button)
                self.page0.attach(button, 2, 4, 1, 1)

        self.page0.show_all()

    def check_out(self, widget):
        """Perform checkout function"""
        command = {"table": "both", "command": common.get_template("check_out")}
        command["command"]["data"]["book_uid"] = self.book_uid
        command["command"]["data"]["user_uid"] = self.user["uid"]
        self.pipe.send(command)
        children = self.page0.get_children()
        for each in children:
            if each.get_label() == "Check Out Book":
                button = each
            try:
                if (("Waiting for Book..." in each.get_text()) or ("Book Found" in each.get_text()) or ("Checked Out" in each.get_text())):
                    status = each
                elif ((each.get_text() == "----") or ("uid" in each.get_text()) or (each.get_text() in ("Book Not Found", "Not a Book", "An Error has occured")) or ("due back by" in each.get_text()) or ("Already Checked Out" in each.get_text())):
                    details = each
            except AttributeError:
                pass
        response = self.pipe.recv()[1]
        if isinstance(response, (int, float)):
            due_date = time.ctime(response)
            details.set_markup(f"Your book is due back by: {due_date}")
            status.set_markup("Book Successfully Checked Out")
        elif isinstance(response, dict):
            if response["status"] == 0:
                details.set_markup("An Error has occured")
                status.set_markup("Waiting for Book...")
            if response["status"] == 2:
                status.set_markup("Book Found")
                message = "Already Checked Out to "
                if response["user"] == self.user["uid"]:
                    message = message + "You"
                else:
                    message = message + "Someone Else"
                details.set_markup(message)
        self.page0.remove(button)
        self.show_all()


    def renew_scanner(self, widget):
        """Renewal book scanner"""
        self.pipe.send("get_barcode")
        children = self.page2.get_children()
        element = []
        for each in children:
            # This is a bit of a hack but works
            if "<class 'gi.overrides.Gtk.Label'>" == str(type(each)):
                element.append(each)
        for each in element:
            if ((each.get_text() == "----") or ("uid" in each.get_text()) or (each.get_text() in ("Book Not Found", "Not a Book", "An Error has occured")) or ("due back by" in each.get_text())):
                details = each
            elif (("Waiting for Book..." in each.get_text()) or ("Book Found" in each.get_text()) or ("Renewed" in each.get_text())):
                status = each
        input = self.pipe.recv()
        if "status" in input[0]:
            if input[0]["status"] == 0:
                details.set_markup("An Error has occured")
        elif input == []:
            details.set_markup("Book Not Found")
            # see if button exists. Delete if so
            for each in children:
                if each.get_label() == "Renew Book":
                    self.page2.remove(each)
                    break
        elif "check_in_status" not in input[0]:
            details.set_markup("Not a Book")
            # see if button exists. Delete if so
            for each in children:
                if each.get_label() == "Renew Book":
                    self.page2.remove(each)
                    break
        else:
            self.book_uid = input[0]["uid"]
            text = f"""
            <b>uid</b>: {input[0]["uid"]}
           <b>Name</b>: {input[0]["name"]}
         <b>Status</b>: {input[0]["check_in_status"]["status"]}"""
            details.set_markup(text)
            status.set_markup("<b>Book Found</b>")
            # See if button exists. If not, add button to send checkout command
            exists = False
            for each in children:
                if each.get_label() == "Renew Book":
                    exists = True
            if not exists:
                button = Gtk.Button.new_with_label("Renew Book")
                button.connect("clicked", self.renew)
                button = self._set_default_margins(button)
                self.page2.attach(button, 2, 4, 1, 1)

        self.page2.show_all()

    def renew(self, widget):
        """Perform renew function"""
        command = {"table": "both", "command": common.get_template("renew")}
        command["command"]["data"]["book_uid"] = self.book_uid
        command["command"]["data"]["user_uid"] = self.user["uid"]
        self.pipe.send(command)
        children = self.page2.get_children()
        for each in children:
            if each.get_label() == "Renew Book":
                button = each
            try:
                if (("Waiting for Book..." in each.get_text()) or ("Book Found" in each.get_text()) or ("Renewed" in each.get_text())):
                    status = each
                elif ((each.get_text() == "----") or ("uid" in each.get_text()) or (each.get_text() in ("Book Not Found", "Not a Book", "An Error has occured")) or ("due back by" in each.get_text()) or ("Already Checked In" in each.get_text())):
                    details = each
            except AttributeError:
                pass
        response = self.pipe.recv()[1]
        if isinstance(response, (int, float)):
            due_date = time.ctime(response)
            details.set_markup(f"Your book is due back by: {due_date}")
            status.set_markup("Book Successfully Renewed")
        elif isinstance(response, dict):
            if response["status"] == 0:
                details.set_markup("An Error has occured")
                status.set_markup("Waiting for Book...")
            if response["status"] == 2:
                status.set_markup("Book Found")
                details.set_markup("Already Checked In")
        self.page2.remove(button)
        self.show_all()

    def check_in_scanner(self, widget):
        """Check in scanner"""
        self.pipe.send("get_barcode")
        children = self.page1.get_children()
        element = []
        for each in children:
            # This is a bit of a hack but works
            if "<class 'gi.overrides.Gtk.Label'>" == str(type(each)):
                element.append(each)
        for each in element:
            if ((each.get_text() == "----") or ("uid" in each.get_text()) or (each.get_text() in ("Book Not Found", "Not a Book", "An Error has occured"))):
                details = each
            elif (("Waiting for Book..." in each.get_text()) or ("Book Found" in each.get_text()) or ("Checked Back In" in each.get_text())):
                status = each
        input = self.pipe.recv()
        if "status" in input[0]:
            if input[0]["status"] == 0:
                details.set_markup("An Error has occured")
        elif input == []:
            details.set_markup("Book Not Found")
            # see if button exists. Delete if so
            for each in children:
                if each.get_label() == "Check In Book":
                    self.page1.remove(each)
                    break
        elif "check_in_status" not in input[0]:
            details.set_markup("Not a Book")
            # see if button exists. Delete if so
            for each in children:
                if each.get_label() == "Check In Book":
                    self.page1.remove(each)
                    break
        else:
            self.book_uid = input[0]["uid"]
            text = f"""
            <b>uid</b>: {input[0]["uid"]}
           <b>Name</b>: {input[0]["name"]}
         <b>Status</b>: {input[0]["check_in_status"]["status"]}"""
            details.set_markup(text)
            status.set_markup("<b>Book Found</b>")
            # See if button exists. If not, add button to send checkout command
            exists = False
            for each in children:
                if each.get_label() == "Check In Book":
                    exists = True
            if not exists:
                button = Gtk.Button.new_with_label("Check In Book")
                button.connect("clicked", self.check_in)
                button = self._set_default_margins(button)
                self.page1.attach(button, 2, 4, 1, 1)

        self.page1.show_all()

    def check_in(self, widget):
        """Perform check in function"""
        command = {"table": "both", "command": common.get_template("check_in")}
        command["command"]["data"]["book_uid"] = self.book_uid
        command["command"]["data"]["user_uid"] = self.user["uid"]
        self.pipe.send(command)
        children = self.page1.get_children()
        for each in children:
            if each.get_label() == "Check In Book":
                button = each
            try:
                if (("Waiting for Book..." in each.get_text()) or ("Book Found" in each.get_text()) or ("Checked In" in each.get_text())):
                    status = each
                elif ((each.get_text() == "----") or ("uid" in each.get_text()) or (each.get_text() in ("Book Not Found", "Not a Book", "An Error has occured")) or ("Already Checked In" in each.get_text())):
                    details = each
            except AttributeError:
                pass
        response = self.pipe.recv()[1]
        if response["status"] == 1:
            details.set_markup("----")
            status.set_markup("Book Successfully Checked Back In")
        elif response["status"] == 0:
            details.set_markup("An Error has occured")
            status.set_markup("Waiting for Book...")
        elif response["status"] == 2:
            status.set_markup("Book Found")
            details.set_markup("Already Checked In")
        self.page1.remove(button)
        self.show_all()

    def _set_default_margins(self, widget):
        """Set default margin size"""
        widget.set_margin_start(10)
        widget.set_margin_end(10)
        widget.set_margin_top(10)
        widget.set_margin_bottom(10)
        return widget

    def clear_window(self):
        """Clear Window"""
        children = self.grid.get_children()
        for each0 in children:
            self.grid.remove(each0)

    def exit(self, button):
        """Exit dialog"""
        self.clear_window()

        self.keys = {"enter": self._exit,
                     "esc": self._exit}

        label = Gtk.Label()
        label.set_markup("""\n<b>Are you sure you want to exit?</b>

Exiting now will cause any unsaved data to be lost.""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 1, 2, 1)

        yes = Gtk.Button.new_with_label("Exit")
        yes.connect("clicked", self._exit)
        yes = self._set_default_margins(yes)
        self.grid.attach(yes, 1, 2, 1, 1)

        no = Gtk.Button.new_with_label("Return")
        no.connect("clicked", self.main_menu)
        no = self._set_default_margins(no)
        self.grid.attach(no, 2, 2, 1, 1)

        self.show_all()

    def _exit(self, button):
        """Exit"""
        Gtk.main_quit("delete-event")
        self.destroy()
        self.pipe.send("shut_down")

    def main_menu(self, widget):
        """Main window"""
        self.user = common.get_template("db_users")
        self.clear_window()

        self.keys = {"enter": self.on_login,
                     "esc": self.exit}

        # This is our sign in window. You can't do anything without letting the app know who you are

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>Awaiting User Login</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 1, 3, 1)


        text = """<b>Please enter your UID</b>"""
        if widget == "invalid":
            text = f"{text}\nInvalid UID. Try again."
        label1 = Gtk.Label()
        label1.set_markup(text)
        label1.set_justify(Gtk.Justification.CENTER)
        label1 = self._set_default_margins(label1)
        self.grid.attach(label1, 2, 2, 1, 1)

        uid = Gtk.Entry()
        uid = self._set_default_margins(uid)
        self.grid.attach(uid, 2, 3, 1, 1)

        button1 = Gtk.Button.new_with_label("Login -->")
        button1.connect("clicked", self.on_login)
        button1 = self._set_default_margins(button1)
        self.grid.attach(button1, 3, 4, 1, 1)

        button2 = Gtk.Button.new_with_label("Exit")
        button2.connect("clicked", self.exit)
        button2 = self._set_default_margins(button2)
        self.grid.attach(button2, 1, 4, 1, 1)

        self.show_all()

    def on_login(self, widget):
        """Login handler"""
        children = self.grid.get_children()
        uid = children[2].get_text()
        del children
        command = {"table": "users", "command": common.get_template("get")}
        try:
            uid = int(uid)
        except ValueError:
            pass
        command["command"]["filter"]["compare"] = uid
        command["command"]["filter"]["field"] = "uid"
        self.pipe.send(command)
        response = self.pipe.recv()
        if response == []:
            self.main_menu("invalid")
        self.user = response[0]
        self.reset("")

    def on_logout(self, widget):
        """Logout handler"""
        self.user = None
        self.reset("")

    def user_menu(self, widget):
        """Menu for Users"""
        self.clear_window()

        self.keys = {"enter": None,
                     "esc": self.on_logout}

        stack = Gtk.Stack()
        stack.add_titled(self.page0, "Check Out", "Check Out")
        stack.add_titled(self.page1, "Check In", "Check In")
        stack.add_titled(self.page2, "Renew", "Renew")
        stack = self._set_default_margins(stack)
        self.grid.attach(stack, 1, 2, 4, 1)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        stack_switcher = self._set_default_margins(stack_switcher)
        stack_switcher.connect("event", self.keyboard_changer)
        self.grid.attach(stack_switcher, 2, 1, 2, 1)

        button1 = Gtk.Button.new_with_label("Log Out")
        button1.connect("clicked", self.on_logout)
        button1 = self._set_default_margins(button1)
        self.grid.attach(button1, 3, 4, 1, 1)

        self.show_all()

    def admin_menu(self, widget):
        """Menu for Admin"""
        self.clear_window()

        self.keys = {"enter": None,
                     "esc": self.on_logout}

        stack = Gtk.Stack()
        stack.add_titled(self.page0, "Check Out", "Check Out")
        stack.add_titled(self.page1, "Check In", "Check In")
        stack.add_titled(self.page2, "Renew", "Renew")
        stack.add_titled(self.page3, "User Admin", "User Admin")
        stack.add_titled(self.page4, "Book Admin", "Book Admin")
        stack = self._set_default_margins(stack)
        self.grid.attach(stack, 1, 2, 4, 1)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        stack_switcher = self._set_default_margins(stack_switcher)
        stack_switcher.connect("event", self.keyboard_changer)
        self.grid.attach(stack_switcher, 2, 1, 2, 1)

        button1 = Gtk.Button.new_with_label("Log Out")
        button1.connect("clicked", self.on_logout)
        button1 = self._set_default_margins(button1)
        self.grid.attach(button1, 3, 4, 1, 1)

        self.show_all()

    def keyboard_changer(self, widget, other_widget):
        """Change keyboard keys depending on what is on screen"""
        children = self.grid.get_children()
        for each in children:
            if str(type(each)) == "<class 'gi.repository.Gtk.Stack'>":
                visible = each.get_visible_child_name()
                break
        if visible == "Check Out":
            self.keys = {"enter": self.check_in_scanner,
                         "esc": self.on_logout}
        elif visible == "Check Out":
            self.keys = {"enter": self.check_out_scanner,
                         "esc": self.on_logout}
        elif visible == "Renew":
            self.keys = {"enter": self.renew_scanner,
                         "esc": self.on_logout}
        elif visible == "User Admin":
            self.keys = {"enter": None,
                         "esc": self.on_logout}
        elif visible == "Book Admin":
            self.keys = {"enter": None,
                         "esc": self.on_logout}

    def add_book_ui(self, widget):
        """UI to add a book"""
        self.clear_window()

        # Set up to collect all necessary info to add a book to the database

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>Add A Book</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 1, 5, 1)

        name = Gtk.Entry()
        name.set_placeholder_text("Book Name")
        name = self._set_default_margins(name)
        self.grid.attach(name, 1, 2, 1, 1)

        uid = Gtk.Entry()
        uid.set_placeholder_text("UID (Unique ID)")
        uid = self._set_default_margins(uid)
        self.grid.attach(uid, 1, 3, 1, 1)

        button = Gtk.Button.new_with_label("Generate Random UID")
        button.connect("clicked", self.gen_uid)
        button = self._set_default_margins(button)
        self.grid.attach(button, 2, 3, 1, 1)

        date = Gtk.Entry()
        date.set_placeholder_text("Publish Year")
        date = self._set_default_margins(date)
        self.grid.attach(date, 2, 2, 1, 1)

        button1 = Gtk.Button.new_with_label("<--Back")
        button1.connect("clicked", self.reset)
        button1 = self._set_default_margins(button1)
        self.grid.attach(button1, 1, 4, 1, 1)

        button2 = Gtk.Button.new_with_label("Add Book")
        button2.connect("clicked", self.add_book)
        button2 = self._set_default_margins(button2)
        self.grid.attach(button2, 2, 4, 1, 1)

        self.show_all()

    def add_book(self, widget):
        """Add book to DB"""
        db_struct = common.get_template("db_books")
        command = common.get_template("add")
        children = self.grid.get_children()
        for each in children:
            if "<class 'gi.repository.Gtk.Entry'>" == str(type(each)):
                if each.get_placeholder_text() == "UID (Unique ID)":
                    db_struct["uid"] = int(each.get_text())
                elif each.get_placeholder_text() == "Book Name":
                    db_struct["name"] = each.get_text()
                elif each.get_placeholder_text() ==  "Publish Year":
                    db_struct["published"] = int(each.get_text())

        # we have retreived data from the UI. Generate remaining data
        db_struct["check_in_status"] = {"status": "checked_in",
                                        "possession": None,
                                        "duration": 0,
                                        "due_date": 0}
        db_struct["check_out_history"] = []

        # Generate command
        command["data"] = db_struct
        command = {"table": "book", "command": command}
        self.pipe.send(command)
        output = self.pipe.recv()
        if output["status"] == 1:
            self.reset("")
        else:
            self.error()

    def error(self):
        """Error Dialog"""
        self.clear_window()

    def gen_uid(self, widget):
        """Generate random UID"""
        children = self.grid.get_children()
        for each in children:
            if "<class 'gi.repository.Gtk.Entry'>" == str(type(each)):
                if each.get_placeholder_text() == "UID (Unique ID)":
                    placement = each
                    break
        cmd = common.get_template("get")
        cmd["column"] = "uid"
        del cmd["filter"]
        cmd = {"table": "book", "command": cmd}
        self.pipe.send(cmd)
        data = self.pipe.recv()
        print("Generating UID...")
        while True:
            uid = random.randint(1000, 999999)
            print("Selecting UID: ", uid)
            if uid not in data:
                break
            print("UID already taken. Retrying")
        placement.set_text(str(uid))
        self.show_all()

    def remove_book_ui(self, widget):
        """UI to remove a book"""
        self.clear_window()

        # Make a scanner window basicly

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>Remove Book</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 1, 5, 1)

        label1 = Gtk.Label()
        label1.set_markup("""<b>Waiting for Book...</b>""")
        label1.set_justify(Gtk.Justification.CENTER)
        label1 = self._set_default_margins(label1)
        self.grid.attach(label1, 1, 2, 5, 1)

        label2 = Gtk.Label()
        label2.set_markup("""----""")
        label2.set_justify(Gtk.Justification.CENTER)
        label2 = self._set_default_margins(label2)
        self.grid.attach(label2, 1, 3, 5, 1)

        button1 = Gtk.Button.new_with_label("<-- Back")
        button1.connect("clicked", self.reset)
        button1 = self._set_default_margins(button1)
        self.grid.attach(button1, 1, 4, 1, 1)

        button = Gtk.Button.new_with_label("Start Scanning")
        button.connect("clicked", self.remove_book_scanner)
        button = self._set_default_margins(button)
        self.grid.attach(button, 2, 4, 1, 1)

        self.show_all()

    def remove_book_scanner(self, widget):
        """Check out scanner"""
        self.pipe.send("get_barcode")
        children = self.grid.get_children()
        element = []
        for each in children:
            # This is a bit of a hack but works
            if "<class 'gi.overrides.Gtk.Label'>" == str(type(each)):
                element.append(each)
        for each in element:
            if ((each.get_text() == "----") or ("uid" in each.get_text()) or (each.get_text() in ("Book Not Found", "Not a Book", "An Error has occured")) or ("Removed" in each.get_text())):
                details = each
            elif (("Waiting for Book..." in each.get_text()) or ("Book Found" in each.get_text()) or ("Removed" in each.get_text())):
                status = each
        input = self.pipe.recv()
        if "status" in input[0]:
            if input[0]["status"] == 0:
                details.set_markup("An Error has occured")
        elif input == []:
            details.set_markup("Book Not Found")
            # see if button exists. Delete if so
            for each in children:
                if each.get_label() == "Remove Book":
                    self.page0.remove(each)
                    break
        elif "check_in_status" not in input[0]:
            details.set_markup("Not a Book")
            # see if button exists. Delete if so
            for each in children:
                if each.get_label() == "Remove Book":
                    self.page0.remove(each)
                    break
        else:
            self.book_uid = input[0]["uid"]
            text = f"""
            <b>uid</b>: {input[0]["uid"]}
           <b>Name</b>: {input[0]["name"]}
      <b>Published</b>: {input[0]["published"]}"""
            details.set_markup(text)
            status.set_markup("<b>Book Found</b>")
            # See if button exists. If not, add button to send checkout command
            exists = False
            for each in children:
                if each.get_label() == "Remove Book":
                    exists = True
            if not exists:
                button = Gtk.Button.new_with_label("Remove Book")
                button.connect("clicked", self.remove_book)
                button = self._set_default_margins(button)
                self.grid.attach(button, 3, 4, 1, 1)

        self.grid.show_all()

    def remove_book(self, widget):
        """Perform checkout function"""
        command = {"table": "book", "command": common.get_template("delete")}
        command["command"]["filter"]["compare"] = self.book_uid
        command["command"]["filter"]["field"] = "uid"
        self.pipe.send(command)
        children = self.grid.get_children()
        for each in children:
            if each.get_label() == "Remove Book":
                button = each
            try:
                if (("Waiting for Book..." in each.get_text()) or ("Book Found" in each.get_text()) or ("Removed" in each.get_text())):
                    status = each
                elif ((each.get_text() == "----") or ("uid" in each.get_text()) or (each.get_text() in ("Book Not Found", "Not a Book", "An Error has occured")) or ("Removed" in each.get_text()) or ("Currently Checked Out" in each.get_text())):
                    details = each
            except AttributeError:
                pass
        response = self.pipe.recv()
        print(response)
        if response["status"] == 0:
            details.set_markup("An Error has occured")
            status.set_markup("Waiting for Book...")
        elif response["status"] == 1:
            details.set_markup("The book has been removed")
            status.set_markup("Book Successfully Removed")
        elif response["status"] == 2:
            status.set_markup("Book Found")
            message = "Currently Checked Out to "
            if response["user"] == self.user["uid"]:
                message = message + "You"
            else:
                message = message + "Someone Else"
            details.set_markup(message)
        self.grid.remove(button)
        self.show_all()

    def edit_book_ui(self, widget):
        """UI to edit certain book info.

        Cannot edit: UID, History
        """

    def add_user_ui(self, widget):
        """Add a new user to the system: UI function"""
        self.clear_window()

        self.keys = {"enter": self.add_user,
                     "esc": self.reset}

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>Add A User</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.grid.attach(label, 1, 1, 5, 1)

        name = Gtk.Entry()
        name.set_placeholder_text("First and Last Name")
        name = self._set_default_margins(name)
        self.grid.attach(name, 1, 2, 1, 1)

        uid = Gtk.Entry()
        uid.set_placeholder_text("UID (Unique ID)")
        uid = self._set_default_margins(uid)
        self.grid.attach(uid, 2, 2, 1, 1)

        button = Gtk.Button.new_with_label("Generate Random UID")
        button.connect("clicked", self.gen_uid)
        button = self._set_default_margins(button)
        self.grid.attach(button, 2, 3, 1, 1)

        phnum = Gtk.Entry()
        phnum.set_placeholder_text("Phone Number")
        phnum = self._set_default_margins(phnum)
        self.grid.attach(phnum, 1, 3, 1, 1)

        email = Gtk.Entry()
        email.set_placeholder_text("Email")
        email = self._set_default_margins(email)
        self.grid.attach(email, 1, 4, 1, 1)

        privs = Gtk.ComboBoxText.new()
        privs = self._set_default_margins(privs)
        privs.append("user", "User")
        privs.append("admin", "Administrator")
        privs.set_active_id("user")
        self.grid.attach(privs, 2, 4, 1, 1)


        button1 = Gtk.Button.new_with_label("<--Back")
        button1.connect("clicked", self.reset)
        button1 = self._set_default_margins(button1)
        self.grid.attach(button1, 1, 5, 1, 1)

        button2 = Gtk.Button.new_with_label("Add User")
        button2.connect("clicked", self.add_user)
        button2 = self._set_default_margins(button2)
        self.grid.attach(button2, 2, 5, 1, 1)

        self.show_all()


    def remove_user_ui(self, widget):
        """remove a user from the system: UI function"""

    def add_user(self, widget):
        """Add a new user to the system"""
        db_struct = common.get_template("db_users")
        command = common.get_template("add")
        contact_info = common.get_template("contact_info")
        children = self.grid.get_children()
        for each in children:
            if "<class 'gi.repository.Gtk.Entry'>" == str(type(each)):
                if each.get_placeholder_text() == "UID (Unique ID)":
                    db_struct["uid"] = int(each.get_text())
                elif each.get_placeholder_text() == "First and Last Name":
                    db_struct["name"] = each.get_text()
                elif each.get_placeholder_text() ==  "Phone Number":
                    contact_info["phone_numbers"] = each.get_text().split(",")
                elif each.get_placeholder_text() ==  "Email":
                    contact_info["emails"] = each.get_text().split(",")
            elif "<class 'gi.repository.Gtk.ComboBoxText'>" == str(type(each)):
                db_struct["privs"] = each.get_active_id()
        db_struct["contact_info"] = contact_info
        db_struct["checked_out_books"] = []
        command["data"] = db_struct
        command = {"table": "user", "command": command}
        self.pipe.send(command)
        output = self.pipe.recv()
        if output["status"] == 1:
            self.add_user_success(db_struct["name"], db_struct["uid"],
                                  db_struct["privs"])
        else:
            self.error()

    def add_user_success(self, name, uid, privs):
        """Tell administrator a new user has been successfully added"""
    def add_book_success(self, name, uid):
        """Tell administrator a new book has been successfully added"""
    def remove_user(self, widget):
        """Remove a user from the system"""

    def edit_user_ui(self, widget):
        """Edit user info: UI function"""

    def edit_user(self, widget):
        """Edit user info"""

def show(pipe):
    """Show Main UI"""
    window = PyLibMan_UI(pipe)
    window.set_decorated(True)
    window.set_resizable(False)
    window.connect("delete-event", PyLibMan_UI._exit)
    window.show_all()
    Gtk.main()
    window._exit("clicked")
    window.destroy()
