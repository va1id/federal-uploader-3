""" ERM THE SIGMA DONT CHANGE ANYTHING BELOW IF YOU DONT KNOW WHAT YOUR DOING PLEASE AND THANKS AND BYE! join the discord server discord.gg/4wffQmV6mR"""
""" Note: For the people that come to me saying this doesn't work anymore idc, This use's a shitty ass ROBLOX API which gets detected fast ok bye now"""

""" Note: If this doesn't work, do pip install on the imports that are in the code, I forgot which one you should install :3 """

import sounddevice as sd
from scipy.io.wavfile import read
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from tkinter import ttk, PhotoImage
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from PIL import Image, ImageDraw, ImageFont, ImageTk
from notifypy import Notify
import io
import random
import sys
import os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Uploader:
    def __init__(self, asset_type_var, config_file=resource_path("./Data/config.json")):
        self.config_file = config_file
        self.load_config()
        self.asset_type_var = asset_type_var

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def load_user_info(self):
        user_info_file = resource_path("./Data/user_info.json")
        try:
            with open(user_info_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def save_user_info(self, user_info):
        userINFOFILE = resource_path("./Data/user_info.json")
        with open(userINFOFILE, "w") as f:
            json.dump(user_info, f, indent=4)

    def load_settings(self):
        p = resource_path("./Data/settings.json")
        try:
            with open(p, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def get_csrf_token(self):
        url = "https://auth.roblox.com/v2/logout"
        headers = {
            "Cookie": f".ROBLOSECURITY={self.config.get('cookie')}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(url, headers=headers)
        csrf_token = response.headers.get("X-CSRF-TOKEN")
        if csrf_token:
            return csrf_token
        else:
            raise ValueError("CSRF token not found")

    def get_user_info(self):
        url = "https://users.roblox.com/v1/users/authenticated"
        headers = {
            "Cookie": f".ROBLOSECURITY={self.config.get('cookie')}",
            "User-Agent": "Roblox/WinInet",
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            user_info = res.json()
            return user_info
        else:
            return None

    def create_api_key(self):
        xsrf_token = self.get_csrf_token()
        user_info = self.get_user_info()
        if user_info is None:
            return None
        payload = {
            "cloudAuthUserConfiguredProperties": {
                "name": "federal uploader >w<",
                "description": "always topping it off as the best uploader!",
                "isEnabled": True,
                "allowedCidrs": ["0.0.0.0/0"],
                "scopes": [
                    {
                        "scopeType": "asset",
                        "targetParts": ["U"],
                        "operations": ["read", "write"],
                    }
                ],
            }
        }
        headers = {
            "Cookie": f".ROBLOSECURITY={self.config.get('cookie')}",
            "Content-Type": "application/json",
            "X-CSRF-TOKEN": xsrf_token,
        }

        res = requests.post(
            "https://apis.roblox.com/cloud-authentication/v1/apiKey",
            json=payload,
            headers=headers,
        )

        if res.status_code == 200:
            try:
                api_key_info = res.json()
                self.config["api_key"] = api_key_info["apikeySecret"]
                self.save_config()
                return api_key_info["apikeySecret"]
            except json.JSONDecodeError:
                return "Error decoding JSON response: " + res.text
        else:
            return f"Error: {res.status_code} - {res.text}"

    def start_upload(self, img_data):
        url = "https://apis.roblox.com/assets/v1/assets"
        headers = {
            "x-api-key": self.config.get("api_key"),
            "Content-Type": "application/json",
        }
        user_info = self.load_user_info()
        if user_info is None:
            return "failed to get user info."

        with io.BytesIO(img_data) as file:
            form = MultipartEncoder(
                fields={
                    "fileContent": ("asset.png", file, "image/png"),
                    "request": json.dumps(
                        {
                            "assetType": self.asset_type_var.get(),
                            "displayName": "federal, owo:3",
                            "description": "federal uploader was used in da process. ",
                            "creationContext": {
                                "creator": {"userId": user_info["userID"]}
                            },
                        }
                    ),
                }
            )
            headers["Content-Type"] = form.content_type
            res = requests.post(url, data=form, headers=headers)

        if res.status_code == 200:
            return "asset uploaded successfully!!"
        else:
            return f"Error: {res.status_code} - {res.text}"

    def process_image(self, file_path):
        settings = self.load_settings()
        with Image.open(file_path) as image:
            max_size = 420
            width, height = image.size
            if width > max_size or height > max_size:
                ratio = min(max_size / width, max_size / height)
                width = int(width * ratio)
                height = int(height * ratio)
                image = image.resize((width, height), Image.LANCZOS)

            unique_identifier = "".join(
                random.choices(
                    "abcdefghijklmnopqrstuvwxyz0123456789", k=settings["letter_amount"]
                )
            )
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype("arial.ttf", settings["letter_size"])

            bbox = draw.textbbox((0, 0), unique_identifier, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = random.randint(0, width - text_width)
            y = random.randint(0, height - text_height)

            draw.text((x, y), unique_identifier, font=font, fill=(255, 255, 255))

            num_pixels_to_change = 5
            for _ in range(num_pixels_to_change):
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                pixel = image.getpixel((x, y))
                new_pixel = tuple(
                    (color + random.randint(0, 10)) % 256 for color in pixel
                )
                image.putpixel((x, y), new_pixel)

            output = io.BytesIO()
            image.save(output, format="PNG")
            output.seek(0)
            return output.read()


class ROUPLOADERUI:
    def __init__(self, root):
        self.root = root
        self.root.title("federal uploader, ro-uploader furry edition or something idfk")
        img = PhotoImage(file=resource_path("./Data/Icons/ro_uploader-5.png"))
        root.iconphoto(False, img)
        self.root.config(bg="#2d2926")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#2d2926")
        self.style.configure(
            "TButton", background="#4a4a4a", foreground="white", padding=[10, 5]
        )
        self.style.configure("TEntry", padding=[10, 5], relief="flat")
        self.style.configure("TLabel", background="#2d2926", foreground="white")

        self.tab_control = ttk.Notebook(root)

        self.create_api_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.create_api_tab, text="key creation.")

        self.cookie_label = tk.Label(self.create_api_tab, text="put your cookie here!!")
        self.cookie_label.pack(pady=(10, 5))
        self.cookie_entry = ttk.Entry(self.create_api_tab)
        self.cookie_entry.pack(pady=(0, 10))

        self.create_api_button = ttk.Button(
            self.create_api_tab, text="create!!", command=self.create_api_key
        )

        self.note_label = ttk.Label(
            self.create_api_tab,
            text="hey!! if you already created a open cloud key, you don't need to generate a new one, only if you get banned!! >.<",
            style="TLabel",
            font=("Helvetica", 10),
        )
        self.note_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.create_api_button.pack(pady=10)

        self.main_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.main_tab, text="uploading.")

        self.filepath_label = ttk.Label(self.main_tab, text="what asset would you want to upload?? :D")
        self.filepath_label.pack(pady=(10, 5))
        self.filepath_entry = ttk.Entry(self.main_tab, state="readonly")
        self.filepath_entry.pack(pady=(0, 10))

        self.image_preview_label = ttk.Label(self.main_tab)
        self.image_preview_label.pack(pady=(10, 10))

        self.browse_button = ttk.Button(
            self.main_tab, text="lemme browse :P", command=self.browse_file
        )
        self.browse_button.pack(pady=10)

        self.amount_label = ttk.Label(self.main_tab, text="how many assets?? :O")
        self.amount_label.pack(pady=(10, 5))
        self.amount_entry = ttk.Entry(self.main_tab)
        self.amount_entry.pack(pady=(0, 10))

        self.asset_type_label = ttk.Label(self.main_tab, text="what type of asset?? :0")
        self.asset_type_label.pack(pady=(10, 5))
        self.asset_type_var = tk.StringVar()
        self.asset_type_combobox = ttk.Combobox(
            self.main_tab, textvariable=self.asset_type_var, state="readonly"
        )
        self.asset_type_combobox["values"] = ("Decal", "TShirt")
        self.asset_type_combobox.current(0)
        self.asset_type_combobox.pack(pady=(0, 10))

        self.roblox = Uploader(self.asset_type_var)

        self.upload_button = ttk.Button(
            self.main_tab, text="get to uploading! >:3", command=self.upload_asset
        )
        self.upload_button.pack(pady=10)

        self.log_tab = ttk.Frame(self.tab_control, style="TFrame")
        self.tab_control.add(self.log_tab, text="console.")

        self.log_text = scrolledtext.ScrolledText(
            self.log_tab,
            wrap=tk.WORD,
            height=10,
            width=50,
            state="disabled",
            bg="#2d2926",
            fg="white",
        )
        self.log_text.pack(fill="both", expand=True)

        self.log("⠀ ／l、")
        self.log("（ﾟ､ ｡ ７            ")
        self.log("⠀ l、ﾞ ~ヽ          thanks for using federal uploader.. >w<")
        self.log("  じしf_, )ノ")
        self.log("\n")

        self.account_info_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.account_info_tab, text="information.")

        self.username_label = ttk.Label(self.account_info_tab, text="your username is..")
        self.username_label.pack(pady=(10, 5))
        self.username_value = ttk.Label(self.account_info_tab, text="")
        self.username_value.pack(pady=(0, 10))

        self.user_id_label = ttk.Label(self.account_info_tab, text="your id is..")
        self.user_id_label.pack(pady=(10, 5))
        self.user_id_value = ttk.Label(self.account_info_tab, text="")
        self.user_id_value.pack(pady=(0, 10))

        self.api_key_label = ttk.Label(self.account_info_tab, text="your key is..")
        self.api_key_label.pack(pady=(10, 5))
        self.api_key_value = ttk.Label(self.account_info_tab, text="click me to reveal!!")
        self.api_key_value.pack(pady=(0, 10))
        self.api_key_value.bind("<Button-1>", self.reveal_api_key)

        self.profile_button = ttk.Button(
            self.account_info_tab, text="profile??", command=self.open_profile
        )
        self.profile_button.pack(pady=10)

        self.inventory_button = ttk.Button(
            self.account_info_tab, text="inventory!!", command=self.open_inventory
        )
        self.inventory_button.pack(pady=10)

        self.load_account_info()

        self.settings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.settings_tab, text="settings.")

        self.letter_size_label = ttk.Label(
            self.settings_tab, text="letter size.."
        )
        self.letter_size_label.pack(pady=(10, 5))
        self.letter_size_slider = tk.Scale(
            self.settings_tab,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
            command=self.update_letter_size,
        )
        self.letter_size_slider.set(self.load_setting("letter_size", 1))
        self.letter_size_slider.pack(pady=(0, 10))

        self.letter_amount_label = ttk.Label(
            self.settings_tab, text="how many letters??"
        )
        self.letter_amount_label.pack(pady=(10, 5))
        self.letter_amount_slider = tk.Scale(
            self.settings_tab,
            from_=1,
            to=16,
            orient=tk.HORIZONTAL,
            command=self.update_letter_amount,
        )
        self.letter_amount_slider.set(self.load_setting("letter_amount", 16))
        self.letter_amount_slider.pack(pady=(0, 10))

        self.save_settings_button = ttk.Button(
            self.settings_tab, text="save dem settings!", command=self.save_settings
        )
        self.save_settings_button.pack(pady=10)

        self.credits_tab = ttk.Frame(self.tab_control, style="TFrame")
        self.tab_control.add(self.credits_tab, text="who made dis?")
        self.credits_text = ttk.Label(
            self.credits_tab,
            text="everything and most everything was coded by 5nz!! all i did was customize it :O",
            style="TLabel",
            font=("Helvetica", 12),
        )
        self.credits_text.pack()

        self.github_link = ttk.Label(
            self.credits_tab,
            text="youtube :D",
            style="Link.TLabel",
            cursor="hand2",
            font=("Helvetica", 20, "underline"),
            foreground="white",
        )
        self.github_link.pack()
        self.github_link.bind(
            "<Button-1>", lambda e: self.open_link("https://www.youtube.com/channel/UC83ywu-tO9OqNlKRB78XQGg")
        )

        self.discord_link = ttk.Label(
            self.credits_tab,
            text="the discord server.. :P",
            style="Link.TLabel",
            cursor="hand2",
            font=("Helvetica", 20, "underline"),
            foreground="white",
        )
        self.discord_link.pack()
        self.discord_link.bind(
            "<Button-1>", lambda e: self.open_link("https://discord.gg/b8qGfEs98h")
        )

        self.note_label = ttk.Label(
            self.credits_tab,
            text="customized by soul.wtf on discord!! :3",
            style="TLabel",
            font=("Helvetica", 10),
        )
        self.note_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.note_label2 = ttk.Label(
            self.credits_tab,
            text="educational purposes!! use at your own risk.. :(",
            style="TLabel",
            font=("Helvetica", 10),
        )
        self.note_label2.pack(side=tk.BOTTOM, fill=tk.X)
        self.tab_control.pack(expand=1, fill="both")
        
        
    success_Notification = Notify(
          default_notification_title="success!!",
          default_application_name="federal uploader ;3",
          default_notification_icon=resource_path("./Data/Icons/ro_uploader-5.png"),
          default_notification_audio=resource_path("./Data/SFX/upload_Success.wav")
    )       
    
    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.yview(tk.END)

    def create_api_key(self):
        cookie = self.cookie_entry.get()
        if cookie:
            self.roblox.config["cookie"] = cookie
            self.roblox.save_config()
            api_key = self.roblox.create_api_key()
            self.log(f"response: {api_key}")
            if "Error" in api_key:
                messagebox.showerror("error..", api_key)
                fs, data = read(resource_path("./Data/SFX/error.wav"))
                sd.play(data, fs)
                sd.wait()
            else:
                messagebox.showinfo("successy!", f"here ya go: {api_key}")
                user_info = self.roblox.get_user_info()
                if user_info is not None:
                    user_info_to_save = {
                        "userID": user_info["id"],
                        "userName": user_info["name"],
                    }
                    self.roblox.save_user_info(user_info_to_save)
                    self.load_account_info()
        else:
            messagebox.showwarning("Error", "please put in the roblox cookie.. >:(")
            fs, data = read(resource_path("./Data/SFX/error.wav"))
            sd.play(data, fs)
            sd.wait()

    def upload_asset(self):
        asset_file = self.filepath_entry.get()
        amount_str = self.amount_entry.get()
        if asset_file:
            try:
                amount = int(amount_str) if amount_str else 1
                messagebox.showinfo(
                    "we are uploading!!",
                    "if you wanna know when, check the console!",
                )
                self.upload_thread = threading.Thread(
                    target=self.perform_uploads, args=(asset_file, amount)
                )
                self.upload_thread.start()
            except ValueError:
                messagebox.showwarning(
                    "error!!", "please enter a valid number for the amount."
                )
        else:
            messagebox.showwarning("Error", "Please enter the asset file path.")

    def perform_uploads(self, asset_file, amount):
        processed_images = []

        for _ in range(amount):
            processed_images.append(self.roblox.process_image(asset_file))

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.roblox.start_upload, img_data)
                for img_data in processed_images
            ]
            results = []
            for i, future in enumerate(as_completed(futures), start=1):
                result = future.result()
                results.append(result)
                self.log(f"upload asset response? ({i}/{amount}): {result}")

        success_message = f"successfully uploaded {amount} assets!"
        messagebox.showinfo("upload complete!", success_message)
        self.success_Notification.message = "hi"
        self.success_Notification.send()
        fs, data = read(resource_path("./Data/SFX/upload_Success.wav"))
        sd.play(data, fs)
        sd.wait()

    def open_link(self, url):
        import webbrowser

        webbrowser.open(url)

    def browse_file(self):
        filepath = filedialog.askopenfilename()
        self.filepath_entry.config(state="normal")
        self.filepath_entry.delete(0, tk.END)
        self.filepath_entry.insert(0, filepath)
        self.filepath_entry.config(state="readonly")
        self.preview_image(filepath)

    def preview_image(self, filepath):
        image = Image.open(filepath)
        image.thumbnail((200, 200))
        photo = ImageTk.PhotoImage(image)
        self.image_preview_label.config(image=photo)
        self.image_preview_label.image = photo

    def load_account_info(self):
        user_info = self.roblox.load_user_info()
        if user_info is not None:
            self.username_value.config(text=user_info["userName"])
            self.user_id_value.config(text=str(user_info["userID"]))

    def reveal_api_key(self, event):
        api_key = self.roblox.config.get("api_key")
        if api_key:
            self.api_key_value.config(text=api_key, wraplength=400)
            self.api_key_frame = ttk.Frame(self.account_info_tab)
            self.api_key_frame.pack(pady=(0, 10))

            self.hide_button = ttk.Button(
                self.api_key_frame, text="Hide", command=self.hide_api_key
            )
            self.hide_button.pack(side=tk.LEFT, padx=(0, 5))

            self.copy_button = ttk.Button(
                self.api_key_frame,
                text="Copy",
                command=lambda: self.copy_to_clipboard(api_key),
            )
            self.copy_button.pack(side=tk.LEFT, padx=(0, 5))
        else:
            self.api_key_value.config(text="no key found :( ")

    def hide_api_key(self):
        self.api_key_value.config(text="click to reveal")
        self.api_key_frame.destroy()

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def open_profile(self):
        user_info = self.roblox.load_user_info()
        if user_info is not None:
            url = f"https://www.roblox.com/users/{user_info['userID']}/profile"
            self.open_link(url)

    def open_inventory(self):
        user_info = self.roblox.load_user_info()
        if user_info is not None:
            url = f"https://www.roblox.com/users/{user_info['userID']}/inventory#!/accessories"
            self.open_link(url)

    def update_letter_size(self, value):
        self.letter_size = int(value)
        self.log(f"Letter size updated to {self.letter_size}")

    def update_letter_amount(self, value):
        self.letter_amount = int(value)
        self.log(f"letter amount updated to {self.letter_amount}!")

    def load_setting(self, setting, default):
        try:
            with open(resource_path("./Data/settings.json"), "r") as f:
                settings = json.load(f)
                return settings.get(setting, default)
        except FileNotFoundError:
            return default

    def save_settings(self):
        settings = {
            "letter_size": self.letter_size_slider.get(),
            "letter_amount": self.letter_amount_slider.get(),
        }
        with open(resource_path("./Data/settings.json"), "w") as f:
            json.dump(settings, f, indent=4)
        self.log("settings saved successfully!")
        messagebox.showinfo("settings..?", "saved settings successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ROUPLOADERUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass