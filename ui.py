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
        self.user = common.get_template("db_users")
        # Make our tabs
        self.page0 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
        # Book UID so we can get the data we need
        self.book_uid = None

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

        self.page1 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)

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

        self.page2 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)

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

        self.page3 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>User Administration</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.page3.attach(label, 1, 1, 5, 1)

        self.page4 = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)

        label = Gtk.Label()
        label.set_markup("""<span size="x-large"><b>Book Administration</b></span>""")
        label.set_justify(Gtk.Justification.CENTER)
        label = self._set_default_margins(label)
        self.page4.attach(label, 1, 1, 5, 1)

        self.main_menu("clicked")

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
        if "status" in input[0]:
            if input[0]["status"] == 0:
                details.set_markup("An Error has occured")
        elif input == []:
            details.set_markup("Book Not Found")
            # see if button exists. Delete if so
            for each in children:
                if each.get_label() == "Check Out Book":
                    self.page0.remove(each)
                    break
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
        if response[0]["privs"] == "user":
            self.user_menu("clicked")
        elif response[0]["privs"] == "admin":
            self.admin_menu("clicked")
        else:
            self.main_menu("invalid")

    def user_menu(self, widget):
        """Menu for Users"""
        self.clear_window()

        stack = Gtk.Stack()
        stack.add_titled(self.page0, "page0", "Check Out")
        stack.add_titled(self.page1, "page1", "Check In")
        stack.add_titled(self.page2, "page2", "Renew")
        stack = self._set_default_margins(stack)
        self.grid.attach(stack, 1, 2, 4, 1)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        stack_switcher = self._set_default_margins(stack_switcher)
        self.grid.attach(stack_switcher, 2, 1, 2, 1)

        button1 = Gtk.Button.new_with_label("Log Out")
        button1.connect("clicked", self.main_menu)
        button1 = self._set_default_margins(button1)
        self.grid.attach(button1, 3, 4, 1, 1)

        self.show_all()

    def admin_menu(self, widget):
        """Menu for Admin"""
        self.clear_window()

        self.clear_window()
        stack = Gtk.Stack()
        stack.add_titled(self.page0, "page0", "Check Out")
        stack.add_titled(self.page1, "page1", "Check In")
        stack.add_titled(self.page2, "page2", "Renew")
        stack.add_titled(self.page3, "page3", "User Admin")
        stack.add_titled(self.page4, "page4", "Book Admin")
        stack = self._set_default_margins(stack)
        self.grid.attach(stack, 1, 2, 4, 1)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(stack)
        stack_switcher = self._set_default_margins(stack_switcher)
        self.grid.attach(stack_switcher, 2, 1, 2, 1)

        button1 = Gtk.Button.new_with_label("Log Out")
        button1.connect("clicked", self.main_menu)
        button1 = self._set_default_margins(button1)
        self.grid.attach(button1, 3, 4, 1, 1)

        self.show_all()

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
