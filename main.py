import threading
import tkinter as tk
from tkinter import ttk
import webview
from PIL import Image, ImageTk
import requests
from io import BytesIO
import speech_recognition as sr

print("NAME: Qorath Browser")
print("INFO: Closing This Window (or CTRL+C) Will Close The Browser.")
print("INFO: All Interactions with the Toolbar and with the \"Voice To URL\" Feature are logged Here.")
print("INFO: The Webpage And Toolbar do not close together. You manually have to close both of them.")
print("INFO: You can modify the code of Qorath Browser.")


# Helper to load image (local fallback to URL)
def load_image(path, fallback_url, size=(32, 32)):
    try:
        img = Image.open(path)
    except Exception:
        try:
            response = requests.get(fallback_url, timeout=5)
            img = Image.open(BytesIO(response.content))
        except Exception:
            img = Image.new("RGBA", size, (200, 200, 200, 255))
    img = img.resize(size)
    return ImageTk.PhotoImage(img)

# Tkinter overlay toolbar
class OverlayUI(threading.Thread):
    def __init__(self, webview_window):
        super().__init__(daemon=True)
        self.webview_window = webview_window
        self.pin_toolbar = True

    def run(self):
        root = tk.Tk()
        root.title("Qorath Browser Toolbar")
        root.geometry("1200x140+100+50")
        root.resizable(False, False)
        root.attributes("-topmost", self.pin_toolbar)

        style = ttk.Style(root)
        style.theme_use("alt")

        # Window icon
        icon = load_image("browsericon.png", "https://qorathstudio.neocities.org/browsericon.png", size=(48, 48))
        if icon:
            root.iconphoto(False, icon)

        toolbar = ttk.Frame(root, padding=15)
        toolbar.pack(fill=tk.BOTH, expand=True)

        # Toolbar buttons
        btn_frame = ttk.Frame(toolbar)
        btn_frame.pack(side=tk.TOP, fill=tk.X)

        self.back_btn = ttk.Button(btn_frame, text="←", command=self.go_back)
        self.back_btn.pack(side=tk.LEFT, padx=4, ipadx=10, ipady=6)

        self.forward_btn = ttk.Button(btn_frame, text="→", command=self.go_forward)
        self.forward_btn.pack(side=tk.LEFT, padx=4, ipadx=10, ipady=6)

        self.url_entry = ttk.Entry(btn_frame, font=("Arial", 16))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, ipady=6)

        go_btn = ttk.Button(btn_frame, text="Go", command=self.load_url)
        go_btn.pack(side=tk.LEFT, padx=4, ipadx=10, ipady=6)

        # Voice To URL button
        voice_btn = ttk.Button(btn_frame, text="🎤 Voice To URL", command=self.voice_to_url)
        voice_btn.pack(side=tk.LEFT, padx=4, ipadx=10, ipady=6)

        # Pin Toolbar button
        self.pin_toolbar_btn = ttk.Checkbutton(toolbar, text="Pin Toolbar",
                                               command=lambda: self.toggle_pin_toolbar(root))
        self.pin_toolbar_btn.pack(side=tk.TOP, fill=tk.X, pady=5)
        if self.pin_toolbar:
            self.pin_toolbar_btn.state(['selected'])

        root.mainloop()

    # Toggle toolbar always-on-top
    def toggle_pin_toolbar(self, root):
        self.pin_toolbar = not self.pin_toolbar
        root.attributes("-topmost", self.pin_toolbar)
        print("Toggled \"Pin Toolbar\"")

    # Toolbar actions
    def load_url(self):
        url = self.url_entry.get()
        print(f"Loading \"{url}\"")
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            self.webview_window.load_url(url)
        except Exception:
            print(f"Attempted To Load \"{url}\": Failed")
            pass

    def go_back(self):
        try:
            self.webview_window.evaluate_js("window.history.back();")
        except Exception:
            pass

    def go_forward(self):
        try:
            self.webview_window.evaluate_js("window.history.forward();")
        except Exception:
            pass

    # Voice to URL
    def voice_to_url(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for URL...")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, text)
                self.load_url()
            except sr.WaitTimeoutError:
                print("Listening timed out.")
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")

# Main PyWebView window
def main():
    window = webview.create_window(
        "Qorath Browser",
        "https://www.google.com",
        width=1200,
        height=800,
        frameless=False
    )

    overlay = OverlayUI(window)
    overlay.start()

    webview.start(gui="tkinter")

if __name__ == "__main__":
    main()
