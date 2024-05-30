import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font
from tkextrafont import Font
import socket
import threading
from PIL import Image, ImageTk
import cv2
from pyzbar.pyzbar import decode
import json
from roundedbutton import RoundedButton

# Import the custom theme
import_black_theme = """
source /run/media/paulgrey/KRYPT/mobile/mobile/black.tcl
ttk::style theme use black
"""

class MobileApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Vault")
        self.geometry("360x800")
        self.configure()

        self.pages = {}

        # Apply the custom theme
        self.tk.call("eval", import_black_theme)

        # Creating a Font object of "TkDefaultFont"
        self.defaultFont = font.nametofont("TkDefaultFont")

        # Overriding default-font with custom settings
        # i.e changing font-family, size and weight
        self.defaultFont.configure(family="Noto Sans",
                                   size=16,
                                   weight=font.NORMAL)

        # Create frames for each page
        self.scan_page = ScanPage(self)
        self.scan_page.pack(side="bottom", fill="both", expand=False)
        self.pages["scan"] = self.scan_page

        self.input_page = InputPage(self)
        self.input_page.pack(side="top", fill="both", expand=True)
        self.pages["input"] = self.input_page

        self.display_page = DisplayPage(self)
        self.display_page.pack(side="top", fill="both", expand=True)
        self.pages["display"] = self.display_page

        self.connection_page = ConnectionPage(self)
        self.connection_page.pack(side="top", fill="both", expand=True)
        self.pages["connection"] = self.connection_page

        # Bottom bar
        self.bottom_bar = tk.Frame(self, bg="#24292e", bd=0)
        self.bottom_bar.pack(side="bottom", fill="both")

        self.buttons = {}
        for page_name in self.pages:
            icon = self.get_icon(page_name)
            button = tk.Button(self.bottom_bar, image=icon, command=lambda page=page_name: self.show_page(page),
                               bd=0, bg="#24292e", activebackground="#24292e", highlightthickness=0)
            button.image = icon
            button.pack(side="left", padx=10, pady=10, fill="x", expand=True)
            self.buttons[page_name] = button

        # Show the scan page by default
        self.show_page("scan")

    def get_icon(self, page_name):
        base_path = "designs/"
        if page_name == "scan":
            return tk.PhotoImage(file=base_path + "qr-code-scan.256x256.png").subsample(3, 3)
        elif page_name == "input":
            return tk.PhotoImage(file=base_path + "input.256x256.png").subsample(3, 3)
        elif page_name == "display":
            return tk.PhotoImage(file=base_path + "nc-passwords.180x256.png").subsample(3, 3)
        elif page_name == "connection":
            return tk.PhotoImage(file=base_path + "exchange.256x178.png").subsample(3, 3)

    def show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()

        self.pages[page_name].pack(side="top", fill="both", expand=True)


class CustomButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            relief=tk.FLAT,  # Remove button relief
            bd=0,  # Remove border
            highlightthickness=0,  # Remove highlight
            padx=20,  # Add horizontal padding
            pady=7,  # Add vertical padding
            font=("Arial", 18),  # Set font
            foreground="#39224b",  # Text color
            background="#e03b5f",  # Background color
        )
        # Bind events
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)

    def on_hover(self, event):
        self.config(background="#e93f64")  # Change color on hover

    def on_leave(self, event):
        self.config(background="#e03b5f")  # Restore original color


class MyEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        self.bg_filled = kwargs.pop("bg_filled", "#24292e")
        self.border_color = kwargs.pop("border_color", "#ff5733")
        self.app_bg = kwargs.pop("app_bg", "#24292e")

        super().__init__(master, **kwargs)

        # Define style names
        self.style_filled = f"{self._name}.TEntry"
        self.style_inactive = f"{self._name}.Inactive.TEntry"

        # Configure styles
        style = ttk.Style()
        style.configure(self.style_filled, background=self.bg_filled, fieldbackground=self.bg_filled,
                        foreground="#FFFFFF", font=("Source Code Pro", 14, "bold"),
                        bordercolor=self.border_color, justify='center')
        style.configure(self.style_inactive, background=self.app_bg, fieldbackground=self.app_bg,
                        foreground="#FFFFFF", font=("Source Code Pro", 14, "bold"),
                        bordercolor=self.border_color, justify='center')

        # Initial style setup
        self.configure(style=self.style_inactive)

        # Bind events
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, event):
        self.configure(style=self.style_filled)

    def on_focus_out(self, event):
        self.configure(style=self.style_inactive)


class ScanPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#24292e")

        self.label = ttk.Label(self, text="SCAN OR UPLOAD QR CODE TO CONNECT", font="14", background="#24292e")
        self.label.pack(pady=15)

        self.load_button = RoundedButton(self, text="Load QR Code Image", border_radius=8, padding=30, color="#e03b5f", command=self.load_image)
        self.load_button.pack(side="bottom", padx="40", pady=15)

        self.scan_button = RoundedButton(self, text="Scan", border_radius=8, padding=30, color="#e03b5f", command=self.scan_qr)
        self.scan_button.pack(side="bottom", padx="5", pady=5)

        self.qr_image_label = ttk.Label(self, background="#24292e")
        self.qr_image_label.pack(pady=20)

    def scan_qr(self):
        scanner = decode

        def scan_thread():
            cap = cv2.VideoCapture(0)

            while True:
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                decoded_objects = scanner(gray)

                for obj in decoded_objects:
                    scanned_info = obj.data.decode("utf-8")
                    ip_address, port = scanned_info.split(":")
                    port = int(port)

                    # Update connection information on ConnectionPage
                    self.master.connection_page.set_connection_info(ip_address, port)

                    # Connect to desktop application
                    try:
                        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip_address, port))
                        CustomMessageBox.showinfo("Success", "Connected to YOURAPP", label_padx=35, label_pady=20)
                        self.master.show_page("input")
                        cap.release()
                        return
                    except Exception as e:
                        CustomMessageBox.showerror("Error", "Failed to connect\nCan't read QR Code\nTake a picture from your device\nand\nUpload it trough the app.", label_padx=35, label_pady=20)
                        cap.release()
                        return

                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)

                self.qr_image_label.imgtk = imgtk
                self.qr_image_label.config(image=imgtk)

                self.qr_image_label.after(10, self.qr_image_label.update)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

        threading.Thread(target=scan_thread).start()

    def load_image(self):
        filetypes = [("All files", "*.*")]
        file_dialog = filedialog.Open(filetypes=filetypes)
        file_path = file_dialog.show()

        if file_path:
            try:
                img = Image.open(file_path)
                img = img.resize((300, 300), Image.ANTIALIAS)
                imgtk = ImageTk.PhotoImage(image=img)

                self.qr_image_label.config(image=imgtk)
                self.qr_image_label.image = imgtk  # Keep a reference to avoid garbage collection

                self.process_qr_code(file_path)
            except Exception as e:
                CustomMessageBox.showerror("Error", "Can't to load QR Code image\nMake sure the picture is visible\nand\nUploade it again.", label_padx=35, label_pady=20)

    def process_qr_code(self, file_path):
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        decoded_objects = decode(gray)

        for obj in decoded_objects:
            scanned_info = obj.data.decode("utf-8")
            ip_address, port = scanned_info.split(":")
            port = int(port)

            # Update connection information on ConnectionPage
            self.master.connection_page.set_connection_info(ip_address, port)

            # Connect to desktop application
            try:
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip_address, port))
                CustomMessageBox.showinfo("Success", "Connected to YOURAPP", label_padx=35, label_pady=20)
                self.master.show_page("input")
                return
            except Exception as e:
                CustomMessageBox.showerror("Error", "Can't connect to YOURAPP\nTake a picture\nof the QR Code\nand upload it to the\n** application",
                                           label_padx=30, label_pady=20)
                return


class CustomMessageBox(tk.Toplevel):
    def __init__(self, parent, title, message, font_size=12, label_padx=20, label_pady=10):
        super().__init__(parent)
        self.title(title)
        self.configure(bg="#24292e")  # Set background color

        # Remove borders
        self.overrideredirect(True)

        label = tk.Label(self, text=message, bg="#24292e", fg='white',
                         font=('Source Code Pro', font_size))  # Set background color, customize font, and colors
        label.pack(fill='x', expand=True, padx=label_padx, pady=label_pady)

        close_button = RoundedButton(self, text="Close", border_radius=8, padding=22, color="#e03b5f", command=self.destroy)
        close_button.pack(side="bottom", padx=10, pady=15, expand=True)

        # Center the window on the screen
        self.update_idletasks()
        self.geometry(f"+{(self.winfo_screenwidth() - self.winfo_reqwidth()) // 2}+{(self.winfo_screenheight() - self.winfo_reqheight()) // 2}")

    @classmethod
    def showerror(cls, title, message, font_size=12, label_padx=20, label_pady=10):
        messagebox = cls(None, title, message, font_size=font_size, label_padx=label_padx, label_pady=label_pady)
        messagebox.mainloop()

    @classmethod
    def showwarning(cls, title, message, font_size=12, label_padx=20, label_pady=10):
        messagebox = cls(None, title, message, font_size=font_size, label_padx=label_padx, label_pady=label_pady)
        messagebox.mainloop()

    @classmethod
    def showinfo(cls, title, message, font_size=12, label_padx=20, label_pady=10):
        messagebox = cls(None, title, message, font_size=font_size, label_padx=label_padx, label_pady=label_pady)
        messagebox.mainloop()

    @classmethod
    def show_custom_message(cls, title, message, font_size=12, label_padx=20, label_pady=10):
        messagebox = cls(None, title, message, font_size=font_size, label_padx=label_padx, label_pady=label_pady)
        messagebox.mainloop()


class InputPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#24292e")
        self.master = master

        self.label = ttk.Label(self, text="SELECT STREAMING PLATFORM", font=('Source Code Pro', 14), background="#24292e")
        self.label.grid(row=0, column=0, columnspan=2, pady=15)

        self.platforms = ['Netflix', 'Amazon Prime', 'Disney+', 'Hulu']
        self.selected_platform = tk.StringVar()
        self.selected_platform.set(self.platforms[0])

        self.platform_dropdown = ttk.OptionMenu(self, self.selected_platform, *self.platforms)
        self.platform_dropdown.grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')

        self.username_label = ttk.Label(self, text="Username:", font=('Source Code Pro', 11), background="#24292e", anchor='w')
        self.username_label.grid(row=2, column=0, pady=5, sticky='w')

        self.username_entry = MyEntry(self)
        self.username_entry.grid(row=2, column=1, pady=5, sticky='ew')

        self.password_label = ttk.Label(self, text="Password:", font=('Source Code Pro', 11), background="#24292e", anchor='w')
        self.password_label.grid(row=3, column=0, pady=5, sticky='w')

        self.password_entry = MyEntry(self, show="*")
        self.password_entry.grid(row=3, column=1, pady=5, sticky='ew')

        # Add a stretchable row to push the save button to the bottom
        self.grid_rowconfigure(4, weight=1)

        self.save_button = RoundedButton(self, text="Save", border_radius=8, padding=30, color="#e03b5f", command=self.save_data)
        self.save_button.grid(row=5, column=0, columnspan=2, pady=10, sticky='s')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def save_data(self):
        platform = self.selected_platform.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Show the data in the display frame
        self.master.display_page.add_credentials(platform, username, password)

        platform = (platform)  # For demonstration, replace with actual platform
        message = f"Credentials for {platform} saved."
        self.show_custom_message("Saved", message)

        # Clear input fields
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def show_custom_message(self, title, message):
        messagebox = CustomMessageBox(self.master, title, message)
        messagebox.mainloop()


class DisplayPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#24292e")

        self.label = ttk.Label(self, text="SAVED ACCOUNTS", font="14", background="#24292e")
        self.label.pack(pady=15)

        self.credentials_frame = ttk.Frame(self)
        self.credentials_frame.pack(pady=10)

        self.credentials = {}

    def add_credentials(self, platform, username, password):
        if platform not in self.credentials:
            self.credentials[platform] = []

        self.credentials[platform].append((username, password))
        self.update_display()

    def update_display(self):
        # Clear previous entries
        for widget in self.credentials_frame.winfo_children():
            widget.destroy()

        for platform, creds in self.credentials.items():
            platform_label = ttk.Label(self.credentials_frame, text=platform, font=('Source Code Pro', 16, 'bold'),
                                       foreground="#b41857",
                                       background="#20192a", anchor='w')  # Anchor text to the left
            platform_label.grid(sticky='ew', padx=130, pady=5)  # Remove excessive horizontal padding

            for username, password in creds:
                cred_label = ttk.Label(self.credentials_frame,
                                       text=f"Username: {username}\nPassword: {'*' * len(password)} ",
                                       font=('Source Code Pro', 13, 'normal'),
                                       background="#20192a", anchor='w')  # Anchor text to the left
                cred_label.grid(sticky='ew', padx=5, pady=5)  # Remove excessive horizontal padding

        # Make the columns expand to fill the available space
        self.credentials_frame.columnconfigure(0, weight=1)

        # Save credentials to a local file
        with open("credentials.json", "w") as file:
            json.dump(self.credentials, file)

class ConnectionPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#24292e")

        self.label = ttk.Label(self, text="CONNECTION INFORMATION", font=('Source Code Pro', 14), background="#24292e")
        self.label.grid(row=0, column=0, columnspan=2, pady=15)

        self.ip_label = ttk.Label(self, text="IP ADDRESS", font=('Source Code Pro', 11), background="#24292e", anchor='w')
        self.ip_label.grid(row=1, column=0, pady=5, columnspan=2)

        self.ip_entry = MyEntry(self)
        self.ip_entry.grid(row=2, column=0, pady=5, columnspan=2,)

        self.port_label = ttk.Label(self, text="PORT", font=('Source Code Pro', 11), background="#24292e", anchor='w')
        self.port_label.grid(row=3, column=0, pady=5, columnspan=2,)

        self.port_entry = MyEntry(self)
        self.port_entry.grid(row=4, column=0, pady=5, columnspan=2,)

        # Add a stretchable row to push buttons to the bottom
        self.grid_rowconfigure(5, weight=1)

        self.connect_button = RoundedButton(self, text="Connect", border_radius=8, padding=30, color="#e03b5f",
                                            command=self.connect)
        self.connect_button.grid(row=5, column=0, columnspan=2, pady=5, sticky='s')

        self.send_button = RoundedButton(self, text="Send Passwords", border_radius=8, padding=30, color="#e03b5f",
                                         command=self.send_data)
        self.send_button.grid(row=6, column=0, columnspan=2, pady=15, sticky='s')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.connection = None  # Initialize the connection attribute

    def center_window(self):
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')

        self.center_window()

    def set_connection_info(self, ip_address, port):
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, ip_address)
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, port)

    def connect(self):
        ip_address = self.ip_entry.get()
        port = int(self.port_entry.get())

        try:
            # Establish connection
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((ip_address, port))
            CustomMessageBox.showinfo("Success", "Connected to YOURAPP", label_padx=35, label_pady=20)
        except Exception as e:
            CustomMessageBox.showerror("Error", "Failed to connect\nCheck you device permissions\nMake sure your wifi is open.", label_padx=35, label_pady=20)

    def send_data(self):
        ip_address = self.ip_entry.get()
        port = int(self.port_entry.get())

        # Always reconnect before sending data
        self.connect()

        # Read credentials from the local file
        try:
            with open("credentials.json", "r") as file:
                credentials = json.load(file)
        except FileNotFoundError:
            CustomMessageBox.showerror("Error", "No credentials found.", label_padx=35, label_pady=20)
            return

        data = json.dumps({"credentials": credentials})

        try:
            if self.connection:
                # Send data through the existing connection
                self.connection.sendall(data.encode())
                messagebox.showinfo("Success" "Data Transfered", label_padx=35, label_pady=20)
            else:
                CustomMessageBox.showerror("Error", "Bad connection\nCheck you device permissions\nMake sure your wifi is open\nand\nEnter connection info manually.", label_padx=35, label_pady=20)
        except Exception as e:
            CustomMessageBox.showerror("Error","Bad connection\nCheck you device permissions\nMake sure your wifi is open\nand\nEnter connection info manually.", label_padx=35, label_pady=20)

    def on_exit(self):
        # Close the connection when the app exits
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    app = MobileApp()
    app.mainloop()
