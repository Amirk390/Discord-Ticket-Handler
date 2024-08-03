import pytesseract
from PIL import ImageGrab, Image
import pyautogui
import tkinter as tk
import pyperclip
from pynput import mouse

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Overlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Picker")
        self.root.geometry("500x700")  # Adjusted to fit the layout
        self.root.configure(bg='white')
        self.root.attributes("-topmost", True)  # Ensure the window stays on top

        # Center align everything
        self.container = tk.Frame(root, bg='white')
        self.container.pack(expand=True, fill=tk.BOTH)

        # Title and description
        self.title_label = tk.Label(self.container, text="Text Picker", bg='white', font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=(10, 0))

        self.description_label = tk.Label(self.container, text="Click on the information (text) you want to pick", bg='white', font=("Helvetica", 10))
        self.description_label.pack(pady=(0, 20))

        # Input boxes with labels
        self.input_boxes = {}
        self.current_box_index = 0
        self.labels = ["User Name", "Reason", "Ban Time", "Ticket ID"]

        self.input_frame = tk.Frame(self.container, bg='white')
        self.input_frame.pack(pady=(5, 10))

        for label in self.labels:
            self.create_labeled_input(label)

        # Add control buttons
        self.buttons_frame = tk.Frame(self.container, bg='white')
        self.buttons_frame.pack(pady=(5, 10))

        self.stop_button = tk.Button(self.buttons_frame, text="Stop", command=self.toggle_script, bg='red', fg='white')
        self.stop_button.pack(side=tk.LEFT, padx=10)

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
        self.lookup_buttons_frame = tk.Frame(self.container, bg='white')
        self.lookup_buttons_frame.pack(pady=(5, 20))

        self.past_punishments_button = tk.Button(self.lookup_buttons_frame, text="Past punishments Lookup", bg='#ffd67f', fg='black', command=self.past_punishments_lookup)
        self.past_punishments_button.pack(side=tk.LEFT, padx=20)

        self.server_logs_button = tk.Button(self.lookup_buttons_frame, text="Server-logs lookup", bg='#ffd67f', fg='black', command=self.server_logs_lookup)
        self.server_logs_button.pack(side=tk.LEFT, padx=20)

        # Start the global mouse listener
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

        self.update_overlay()

    def create_labeled_input(self, label_text):
        label = tk.Label(self.input_frame, text=label_text, bg='white', font=("Helvetica", 10, "bold"))
        label.pack()

        entry_var = tk.StringVar()
        entry = tk.Entry(self.input_frame, textvariable=entry_var, bg='#424242', fg='white', font=("Helvetica", 12, "bold"), width=25, justify='center')
        entry.pack(pady=(5, 10))

        self.input_boxes[label_text] = entry

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
        self.stop_button.config(text="Stop", bg='red')
        self.stop_button.config(state=tk.NORMAL)

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
            self.update_input_box(current_label, self.current_highlighted_text)
            self.current_box_index += 1

            if self.current_box_index >= len(self.labels):
                self.running = False
                self.stop_button.config(text="Copy", bg='green')
                self.stop_button.config(state=tk.NORMAL)

    def copy_to_clipboard(self):
        # Concatenate texts from all input boxes
        concatenated_text = '\n'.join(self.input_boxes[label].get().strip() for label in self.labels)
        self.big_input_box.delete(1.0, tk.END)
        self.big_input_box.insert(tk.END, concatenated_text + "\n")
        pyperclip.copy(concatenated_text)  # Copy the concatenated text to the clipboard

    def toggle_script(self):
        if self.current_box_index >= len(self.labels):
            self.copy_to_clipboard()
            self.stop_button.config(text="Stop", bg='red')
            self.stop_button.config(state=tk.NORMAL)
            return

        self.running = not self.running
        if self.running:
            self.stop_button.config(text="Stop", bg='red')
        else:
            self.stop_button.config(text="Start", bg='green')

    def past_punishments_lookup(self):
        user_name = self.input_boxes["User Name"].get().strip()
        lookup_text = f"in:#punishment-request {user_name}"
        pyperclip.copy(lookup_text)
        print(lookup_text)

    def server_logs_lookup(self):
        user_name = self.input_boxes["User Name"].get().strip()
        lookup_text = f"in:#server-logs-shack {user_name}"
        pyperclip.copy(lookup_text)
        print(lookup_text)

    def update_overlay(self):
        if not self.running:
            self.root.after(100, self.update_overlay)
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
                self.root.after(100, self.update_overlay)
                return

            region = (left, top, right, bottom)

            print(f"Capturing region: {region}")

            screen = self.capture_screen(region)
            if screen is None:
                self.root.after(100, self.update_overlay)
                return

            data = self.extract_text_boxes_from_image(screen)
            if data:
                self.current_highlighted_text = self.highlight_text_under_cursor(data, x, y, region)
            else:
                self.current_highlighted_text = ""

            self.root.after(100, self.update_overlay)
        except Exception as e:
            print(f"Exception in update_overlay: {e}")
            self.root.after(100, self.update_overlay)

# Create the main window
root = tk.Tk()
overlay = Overlay(root)

# Run the GUI event loop
root.mainloop()
