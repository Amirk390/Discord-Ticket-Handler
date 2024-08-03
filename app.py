import pytesseract
from PIL import ImageGrab, Image, ImageDraw, ImageTk
import pyautogui
import tkinter as tk
import threading
from pynput import mouse

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Overlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Picker")
        self.root.geometry("400x500")
        self.root.configure(bg='white')
        self.root.attributes("-topmost", True)  # Ensure the window stays on top

        # Title and description
        self.title_label = tk.Label(root, text="Text Picker", bg='white', font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=(10, 0))  # Add padding to the top

        self.description_label = tk.Label(root, text="Click on the information (text) you want to pick", bg='white', font=("Helvetica", 10))
        self.description_label.pack(pady=(0, 20))  # Add padding to the bottom

        # Input boxes with labels
        self.input_boxes = {}
        self.current_box_index = 0
        self.labels = ["User Name", "Reason", "Ban Time", "Ticket ID"]
        
        for label in self.labels:
            self.create_labeled_input(label)

        # Add a stop button
        self.stop_button = tk.Button(root, text="Stop", command=self.toggle_script, bg='red', fg='white')
        self.stop_button.pack(pady=5)

        self.stored_text = ""
        self.running = True

        self.current_highlighted_text = ""

        # Start the global mouse listener
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

        self.update_overlay()

    def create_labeled_input(self, label_text):
        label = tk.Label(self.root, text=label_text, bg='white', font=("Helvetica", 10, "bold"))
        label.pack()

        frame = tk.Frame(self.root, bg='white')
        frame.pack(pady=(5, 10))  # Reduce padding between input boxes

        entry_var = tk.StringVar()
        entry = tk.Entry(frame, textvariable=entry_var, bg='#424242', fg='white', font=("Helvetica", 12, "bold"), width=25)
        entry.pack()

        self.input_boxes[label_text] = entry

    def capture_screen(self, region):
        # Capture the screen or a region of the screen
        screen = ImageGrab.grab(bbox=region)
        return screen

    def extract_text_boxes_from_image(self, image):
        # Use Tesseract to extract text bounding boxes
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            return data
        except Exception as e:
            print(f"Error extracting text boxes: {e}")
            return None

    def highlight_text_under_cursor(self, data, cursor_x, cursor_y, region):
        region_x, region_y, _, _ = region
        cursor_relative_x = cursor_x - region_x
        cursor_relative_y = cursor_y - region_y  # Y-coordinate in the image

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
            print(f"Mouse clicked at ({x, y})")
            self.process_click(x, y)

    def process_click(self, x, y):
        if self.current_box_index >= len(self.labels):
            print("All input boxes are filled.")
            return
        
        width, height = 200, 100  # Preset size of the region
        screen_width, screen_height = pyautogui.size()
        
        # Ensure the region is within the screen bounds and has valid dimensions
        left = max(0, x - width // 2)
        top = max(0, y - height // 2)
        right = min(screen_width, x + width // 2)
        bottom = min(screen_height, y + height // 2)

        # Ensure the region has a positive width and height
        if right <= left or bottom <= top:
            print("Invalid region dimensions")
            return

        region = (left, top, right, bottom)

        print(f"Capturing region: {region}")

        # Capture the screen region
        screen = self.capture_screen(region)

        # Extract text bounding boxes from the captured image
        data = self.extract_text_boxes_from_image(screen)

        # Highlight the text under the cursor and store the highlighted text
        if data:
            self.current_highlighted_text = self.highlight_text_under_cursor(data, x, y, region)
        else:
            self.current_highlighted_text = ""

        if self.current_highlighted_text:
            print(f"Storing text: {self.current_highlighted_text}")
            current_label = self.labels[self.current_box_index]
            self.input_boxes[current_label].delete(0, tk.END)
            self.input_boxes[current_label].insert(0, self.current_highlighted_text)
            self.current_box_index += 1

    def toggle_script(self):
        self.running = not self.running
        if self.running:
            self.stop_button.config(text="Stop", bg='red')
        else:
            self.stop_button.config(text="Start", bg='green')

    def update_overlay(self):
        if not self.running:
            return

        try:
            x, y = pyautogui.position()
            width, height = 200, 100  # Preset size of the region
            screen_width, screen_height = pyautogui.size()
            
            # Ensure the region is within the screen bounds and has valid dimensions
            left = max(0, x - width // 2)
            top = max(0, y - height // 2)
            right = min(screen_width, x + width // 2)
            bottom = min(screen_height, y + height // 2)

            # Ensure the region has a positive width and height
            if right <= left or bottom <= top:
                print("Invalid region dimensions")
                self.root.after(100, self.update_overlay)
                return

            region = (left, top, right, bottom)

            print(f"Capturing region: {region}")

            # Capture the screen region
            screen = self.capture_screen(region)

            # Extract text bounding boxes from the captured image
            data = self.extract_text_boxes_from_image(screen)

            # Highlight the text under the cursor and store the highlighted text
            if data:
                self.current_highlighted_text = self.highlight_text_under_cursor(data, x, y, region)
            else:
                self.current_highlighted_text = ""

            # Schedule the next update
            self.root.after(100, self.update_overlay)
        except Exception as e:
            print(f"Exception in update_overlay: {e}")
            self.root.after(100, self.update_overlay)

# Create the main window
root = tk.Tk()
overlay = Overlay(root)

# Run the GUI event loop
root.mainloop()
