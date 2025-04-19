import gi # type: ignore
import hashlib
import subprocess
import dataClass
import uuid

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Pango # type: ignore

class ClipboardManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="GTK Clipboard Manager")
        self.set_default_size(350, 400)
        self.set_border_width(10)

        self.set_resizable(False)

        # Clipboard and history tracking
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.history = []
        self.current_text = ""
        self.current_image_hash = ""
        self.text_id = {}
        self.MAX_HISTORY = 50

        # Prevent focus stealing
        self.set_accept_focus(False)
        self.set_focus_on_map(False)

        # Always on top, hide from taskbar & Alt+Tab
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        # Layout setup
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.vbox)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.vbox.pack_start(self.scrolled_window, True, True, 0)

        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-selected", self.on_row_selected)
        self.scrolled_window.add(self.listbox)
        
        self.connect("map", self.on_map)
        self.connect("delete-event", self.on_window_close)
        self.connect("visibility-notify-event", self.on_visibility_changed)


        GLib.timeout_add(300, self.check_clipboard)
        self.apply_css()
        self.start_socket_server()

    def simulate_paste(self):
        subprocess.run(['xdotool', 'key', "--clearmodifiers", 'ctrl+shift+v'])

    def on_row_selected(self, listbox, row):
        if not row:
            print("TF are you selecting?")
            return
        
        print(row.uuid, "workings")
        obj = self.text_id[row.uuid]
        if obj.is_text:
            self.clipboard.set_text(obj.text, -1)
            self.clipboard.store()
            self.simulate_paste()
            self.current_text = obj.text
        else:
            pixbuf = obj.image
            if pixbuf:
                self.clipboard.set_image(pixbuf)
                self.clipboard.store()
                self.simulate_paste()
                self.current_image_hash = obj.image_hash
        
        self.listbox.unselect_all()

    def check_clipboard(self):
        # Handle text
        text = self.clipboard.wait_for_text()
        if text == self.current_text:
            pass
            
        else:
            if text:
                print("new copy")
                not_available = True
                for i in self.text_id.keys():
                    if self.text_id[i].text == text:
                        self.current_text = text
                        not_available = False

                        row = self.text_id[i].widget
                        self.listbox.remove(row)
                        self.listbox.insert(row, 0)
                        self.listbox.show_all()
                    
                        break


                if not_available:
                    self.current_text = text
                    uuid_unique = uuid.uuid4()
                    print(uuid_unique)
                    obj = dataClass.clipboardEntry(uuid_unique, text=text, is_text=True)
                    self.text_id[uuid_unique] = obj
                    self.history.insert(0, uuid_unique)

                    if len(self.history) > self.MAX_HISTORY:
                        self.history.pop()
                    self.add_text_entry(uuid_unique)


        # Handle image
        image = self.clipboard.wait_for_image()
        if image:
            image_hash = self.get_image_hash(image)
            if self.current_image_hash != image_hash:
                print("possible new image detected")
                not_available = True
                for i in self.text_id.keys():
                    if self.text_id[i].image_hash == image_hash:
                        self.current_image_hash = image_hash
                        not_available = False
                        break
                if not_available:
                    self.current_image_hash = image_hash
                    uuid_unique = uuid.uuid4()
                    print(uuid_unique)
                    obj = dataClass.clipboardEntry(uuid_unique, image=image, image_hash=image_hash, is_text=False)
                    self.text_id[uuid_unique] = obj
                    self.history.insert(0, uuid_unique)

                    self.add_image_entry(uuid_unique)

        return True

    def add_text_entry(self, uuid):
        if self.text_id[uuid].text.strip() != "": #remove this uuid if its empty
            display_text = self.text_id[uuid].text_to_display
            
            
            label = Gtk.Label(label=display_text, xalign=0)
            label.set_line_wrap(True)
            label.set_ellipsize(Pango.EllipsizeMode.END)
            label.set_max_width_chars(20)
            label.set_lines(1) 
            label.set_size_request(-1, 50)

            button = Gtk.Button(label="✕")
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.get_style_context().add_class("remove-button") 

            
            button.connect("clicked", self.remove_entry, uuid)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            hbox.pack_start(label, True, True, 0)
            hbox.pack_end(button, False, False, 0)

            row = Gtk.ListBoxRow()
            row.add(hbox)
            row.uuid = uuid
            self.text_id[uuid].widget = row


            row.get_style_context().add_class("clipboard-row")
            self.listbox.insert(row, 0)
            self.listbox.show_all()

    def remove_entry(self, button, uuid):
        
        self.listbox.remove(self.text_id[uuid].widget)
        self.history.remove(uuid)
        del self.text_id[uuid]


    def add_image_entry(self, uuid):
        pixbuf = self.text_id[uuid].image
        
        original_width = pixbuf.get_width()
        original_height = pixbuf.get_height()
        scale_factor = 50.0 / original_height
        new_width = int(original_width * scale_factor)
        new_pixbuf = pixbuf.scale_simple(new_width, 50, GdkPixbuf.InterpType.BILINEAR)
        
        self.text_id[uuid].image_to_display = new_pixbuf

        image = Gtk.Image.new_from_pixbuf(new_pixbuf)
        image.set_size_request(-1, 50)

        button = Gtk.Button(label="✕")
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.get_style_context().add_class("remove-button") 
        button.connect("clicked", self.remove_entry, uuid)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.pack_start(image, False, False, 0)
        box.pack_end(button, False, False, 0)

        row = Gtk.ListBoxRow()
        row.add(box)
        row.uuid = uuid
        self.text_id[uuid].widget = row

        row.get_style_context().add_class("clipboard-row")

        self.listbox.insert(row, 0)
        self.listbox.show_all()

    def get_image_hash(self, pixbuf):
        data = pixbuf.get_pixels()
        return hashlib.md5(data).hexdigest()

    def apply_css(self):
        css_provider = Gtk.CssProvider()
        try:
            css_provider.load_from_path("style.css")
        except:
            print("Styleshet not found, applying defaults")
            css_provider.load_from_data("""
                .clipboard-row {
                    background-color: #2b2b2b;
                    border-radius: 10px;
                    padding: 10px;
                    margin: 6px;

                    border: 1px solid #cccccc;  /* Greyish white border */
                }

                .clipboard-row:hover {
                    background-color: #3a3a3a;
                }

                button {
                    background-color: #2b2b2b;
                    border: none;
                    color: white;
                }

                button:hover {
                    background-color: #ff4c4c; /* Red hover for the ✕ button */
                    color: white;
                }
            """.encode("utf-8"))




        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


    def on_map(self, window):
        self.present()
        

    def on_window_close(self, widget, event):
        # Hide the window instead of closing it
        print("Hiding")
        self.hide()
        return True  

    def on_visibility_changed(self, widget, event):
        if self.get_visible():
            print("Window is visible")
        else:
            print("Window is not visible")

    def start_socket_server(self):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.server_socket.bind(SOCKET_PATH)

        def listen():
            while True:
                try:
                    data, _ = self.server_socket.recvfrom(1024)
                    if data.decode() == "show":
                        GLib.idle_add(self.present_window)
                except Exception as e:
                    print("Socket error:", e)
                    break

        threading.Thread(target=listen, daemon=True).start()

    def present_window(self):
        self.deiconify()
        self.present()

    def on_destroy(self, *args):
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)


import socket
import os
import threading

SOCKET_PATH = f"/tmp/clipboard_manager_{os.getuid()}.sock"




def main():
    # If socket exists, send "show" to running instance and exit
    if os.path.exists(SOCKET_PATH):
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            client.sendto(b"show", SOCKET_PATH)
            return
        except Exception as e:
            print("Socket send failed:", e)

    # Otherwise start app normally
    win = ClipboardManager()
    win.connect("destroy", win.on_destroy)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()