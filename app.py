import pytesseract
from PIL import ImageGrab, Image
import pyautogui
import tkinter as tk
from tkinter import ttk
import pyperclip
from pynput import mouse
import re

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Overlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Purple RP Ticket Assistant")
        self.root.geometry("500x800")  # Adjusted to fit the layout
        self.root.configure(bg='#641d77')
        self.root.attributes("-topmost", True)  # Ensure the window stays on top

        # Set the icon
        self.root.iconphoto(True, tk.PhotoImage(file=r'C:\Users\user\Downloads\DiscordTicketHandler\app\image.png'))

        # Center align everything
        self.container = tk.Frame(root, bg='#641d77')
        self.container.pack(expand=True, fill=tk.BOTH)

        # Title and description
        self.title_label = tk.Label(self.container, text="Purple RP Ticket Assistant", bg='#641d77', fg='white', font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=(10, 0))

        self.description_label = tk.Label(self.container, text="Click on the information (text) you want to pick", bg='#641d77', fg='white', font=("Helvetica", 10))
        self.description_label.pack(pady=(0, 20))

        # Input boxes with labels
        self.input_boxes = {}
        self.current_box_index = 0
        self.labels = ["User Name", "Reason", "Ban Time", "Ticket ID"]

        self.input_frame = tk.Frame(self.container, bg='#641d77')
        self.input_frame.pack(pady=(5, 10))

        for label in self.labels:
            self.create_labeled_input(label)

        # Add Ban Time options
        self.ban_time_frame = tk.Frame(self.input_frame, bg='#641d77')
        self.ban_time_frame.pack(pady=(5, 10))
        self.create_ban_time_options()

        # Add control buttons
        self.buttons_frame = tk.Frame(self.container, bg='#641d77')
        self.buttons_frame.pack(pady=(5, 10))

        self.refresh_button = tk.Button(self.buttons_frame, text="Refresh", command=self.copy_to_clipboard, bg='green', fg='white')
        self.refresh_button.pack(side=tk.LEFT, padx=10)

        self.reset_button = tk.Button(self.buttons_frame, text="Reset", command=self.reset, bg='blue', fg='white')
        self.reset_button.pack(side=tk.LEFT, padx=10)

        # Big square input box for concatenated text
        self.big_input_var = tk.StringVar()
        self.big_input_box = tk.Text(self.container, height=6, width=40, bg='#424242', fg='white', font=("Courier", 12), wrap=tk.NONE)
        self.big_input_box.pack(pady=(10, 20), padx=20, fill=tk.X)

        self.stored_text = ""
        self.running = True

        self.current_highlighted_text = ""

        # Buttons under the big box
        self.lookup_buttons_frame = tk.Frame(self.container, bg='#641d77')
        self.lookup_buttons_frame.pack(pady=(5, 20))

        self.past_punishments_button = tk.Button(self.lookup_buttons_frame, text="Past punishments lookup", bg='#4a1a77', fg='white', command=self.past_punishments_lookup)
        self.past_punishments_button.pack(side=tk.LEFT, padx=20)

        self.server_logs_button = tk.Button(self.lookup_buttons_frame, text="Server logs lookup", bg='#4a1a77', fg='white', command=self.server_logs_lookup)
        self.server_logs_button.pack(side=tk.LEFT, padx=20)

        # Image
        self.image = tk.PhotoImage(file=r'C:\Users\user\Downloads\DiscordTicketHandler\app\image.png')
        self.image_label = tk.Label(self.container, image=self.image, bg='#641d77')
        self.image_label.pack(pady=(20, 0))

        # Footer text
        self.footer_label = tk.Label(self.container, text="This program has been created by TotalStrike for Purple RP community", bg='#641d77', fg='white', font=("Helvetica", 8), anchor='s')
        self.footer_label.pack(side=tk.BOTTOM, pady=(10, 0))

        # Version text
        self.version_label = tk.Label(self.container, text="Version 2.00365b", bg='#641d77', fg='white', font=("Helvetica", 8), anchor='s')
        self.version_label.pack(side=tk.BOTTOM, pady=(0, 10))

        # Start the global mouse listener
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

        self.update_overlay()

    def create_labeled_input(self, label_text):
        label = tk.Label(self.input_frame, text=label_text, bg='#641d77', fg='white', font=("Helvetica", 10, "bold"))
        label.pack()

        entry_var = tk.StringVar()
        entry = tk.Entry(self.input_frame, textvariable=entry_var, bg='#A98BC4', fg='white', font=("Helvetica", 12, "bold"), width=25, justify='center')
        entry.pack(pady=(5, 10))

        entry.bind("<Button-1>", self.on_entry_click)
        self.input_boxes[label_text] = entry

    def create_ban_time_options(self):
        self.ban_time_label = tk.Label(self.ban_time_frame, text="Ban Time", bg='#641d77', fg='white', font=("Helvetica", 10, "bold"))
        self.ban_time_label.pack(side=tk.LEFT)

        self.ban_time_value_var = tk.StringVar()
        self.ban_time_value_var.set("")
        self.ban_time_value_menu = ttk.Combobox(self.ban_time_frame, textvariable=self.ban_time_value_var, values=["1", "2", "3", "4", "5", "6", "7"], width=5)
        self.ban_time_value_menu.pack(side=tk.LEFT, padx=5)

        self.ban_time_unit_var = tk.StringVar()
        self.ban_time_unit_var.set("")
        self.ban_time_unit_menu = ttk.Combobox(self.ban_time_frame, textvariable=self.ban_time_unit_var, values=["Days", "Weeks", "Month", "Perm"], width=10)
        self.ban_time_unit_menu.pack(side=tk.LEFT, padx=5)

        self.ban_time_value_var.trace("w", self.update_ban_time_input)
        self.ban_time_unit_var.trace("w", self.update_ban_time_input)

    def update_ban_time_input(self, *args):
        if self.ban_time_unit_var.get() == "Perm":
            ban_time_text = "Perm"
        else:
            ban_time_text = f"{self.ban_time_value_var.get()} {self.ban_time_unit_var.get()}"
        self.input_boxes["Ban Time"].delete(0, tk.END)
        self.input_boxes["Ban Time"].insert(0, ban_time_text)
        self.update_big_box()

    def center_align_text(self, text, width):
        if len(text) >= width:
            return text[:width]
        padding = (width - len(text)) // 2
        return ' ' * padding + text + ' ' * (width - len(text) - padding)

    def update_input_box(self, label_text, text):
        width = 25  # Width of the Entry widget
        centered_text = self.center_align_text(text, width)
        self.input_boxes[label_text].delete(0, tk.END)
        self.input_boxes[label_text].insert(0, centered_text)

    def reset(self):
        # Clear all input boxes and reset index
        for label in self.labels:
            self.input_boxes[label].delete(0, tk.END)
        self.big_input_box.delete(1.0, tk.END)
        self.current_box_index = 0
        self.running = True
        self.ban_time_value_var.set("")
        self.ban_time_unit_var.set("")

    def capture_screen(self, region):
        try:
            screen = ImageGrab.grab(bbox=region)
            return screen
        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def extract_text_boxes_from_image(self, image):
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            return data
        except Exception as e:
            print(f"Error extracting text boxes: {e}")
            return None

    def highlight_text_under_cursor(self, data, cursor_x, cursor_y, region):
        region_x, region_y, _, _ = region
        cursor_relative_x = cursor_x - region_x
        cursor_relative_y = cursor_y - region_y

        highlighted_text = ""

        for i in range(len(data['text'])):
            if data['text'][i].strip():
                x1, y1, width, height = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                x2, y2 = x1 + width, y1 + height

                if x1 <= cursor_relative_x <= x2 and y1 <= cursor_relative_y <= y2:
                    highlighted_text = data['text'][i]
                    break

        return highlighted_text

    def on_click(self, x, y, button, pressed):
        if pressed and self.running:
            print(f"Mouse clicked at ({x}, {y})")
            self.process_click(x, y)

    def process_click(self, x, y):
        if self.current_box_index >= len(self.labels):
            print("All input boxes are filled.")
            self.running = False
            self.refresh_button.config(state=tk.NORMAL)
            self.update_big_box()
            return

        width, height = 200, 100
        screen_width, screen_height = pyautogui.size()

        left = max(0, x - width // 2)
        top = max(0, y - height // 2)
        right = min(screen_width, x + width // 2)
        bottom = min(screen_height, y + height // 2)

        if right <= left or bottom <= top:
            print("Invalid region dimensions")
            return

        region = (left, top, right, bottom)

        print(f"Capturing region: {region}")

        screen = self.capture_screen(region)
        if screen is None:
            return

        data = self.extract_text_boxes_from_image(screen)
        if data:
            self.current_highlighted_text = self.highlight_text_under_cursor(data, x, y, region)
        else:
            self.current_highlighted_text = ""

        if self.current_highlighted_text:
            print(f"Storing text: {self.current_highlighted_text}")
            current_label = self.labels[self.current_box_index]
            if current_label == "Ticket ID":
                numeric_text = re.sub(r'\D', '', self.current_highlighted_text)
                if numeric_text:
                    self.current_highlighted_text = numeric_text
                    self.update_input_box(current_label, self.current_highlighted_text)
                    self.current_box_index += 1
            else:
                self.update_input_box(current_label, self.current_highlighted_text)
                if self.current_box_index == 1:
                    self.current_box_index += 2  # Skip Ban Time
                else:
                    self.current_box_index += 1

            if self.current_box_index >= len(self.labels):
                self.running = False
                self.refresh_button.config(state=tk.NORMAL)
                self.update_big_box()

    def update_big_box(self):
        concatenated_text = '\n'.join(self.input_boxes[label].get().strip() for label in self.labels if self.input_boxes[label].get().strip())
        if self.ban_time_unit_var.get() == "Perm":
            ban_time_text = "Perm"
        else:
            ban_time_text = f"{self.ban_time_value_var.get()} {self.ban_time_unit_var.get()}"
        concatenated_text = concatenated_text.replace("\nBan Time", f"\n{ban_time_text}\nBan Time")
        self.big_input_box.delete(1.0, tk.END)
        self.big_input_box.insert(tk.END, concatenated_text)
        pyperclip.copy(concatenated_text)

    def copy_to_clipboard(self):
        concatenated_text = '\n'.join(self.input_boxes[label].get().strip() for label in self.labels if self.input_boxes[label].get().strip())
        self.big_input_box.delete(1.0, tk.END)
        self.big_input_box.insert(tk.END, concatenated_text + "\n")
        pyperclip.copy(concatenated_text)  # Copy the concatenated text to the clipboard

    def update_overlay(self):
        if not self.running:
            self.root.after(200, self.update_overlay)
            return

        try:
            x, y = pyautogui.position()
            width, height = 200, 100
            screen_width, screen_height = pyautogui.size()

            left = max(0, x - width // 2)
            top = max(0, y - height // 2)
            right = min(screen_width, x + width // 2)
            bottom = min(screen_height, y + height // 2)

            if right <= left or bottom <= top:
                print("Invalid region dimensions")
                self.root.after(200, self.update_overlay)
                return

            region = (left, top, right, bottom)

            print(f"Capturing region: {region}")

            screen = self.capture_screen(region)
            if screen is None:
                self.root.after(200, self.update_overlay)
                return

            data = self.extract_text_boxes_from_image(screen)
            if data:
                self.current_highlighted_text = self.highlight_text_under_cursor(data, x, y, region)
            else:
                self.current_highlighted_text = ""

            self.root.after(200, self.update_overlay)
        except Exception as e:
            print(f"Exception in update_overlay: {e}")
            self.root.after(200, self.update_overlay)

    def past_punishments_lookup(self):
        user_name = self.input_boxes[self.labels[0]].get().strip()
        result = f"in:#punishment-request {user_name}"
        self.big_input_box.delete(1.0, tk.END)
        self.big_input_box.insert(tk.END, result)
        pyperclip.copy(result)

    def server_logs_lookup(self):
        user_name = self.input_boxes[self.labels[0]].get().strip()
        result = f"in:#server-logs-shack {user_name}"
        self.big_input_box.delete(1.0, tk.END)
        self.big_input_box.insert(tk.END, result)
        pyperclip.copy(result)

    def on_entry_click(self, event):
        widget = event.widget
        for label, entry in self.input_boxes.items():
            if entry == widget:
                self.current_box_index = self.labels.index(label)
                break

# Create the main window
root = tk.Tk()
overlay = Overlay(root)

# Run the GUI event loop
root.mainloop()
