import pytesseract
from PIL import ImageGrab, Image, ImageDraw, ImageTk
import pyautogui
import tkinter as tk
import win32api
import win32gui
import win32con
import sys

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class Overlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Picker")
        self.root.geometry("400x200")
        self.root.configure(bg='white')

        # Title and description
        self.title_label = tk.Label(root, text="Text Picker", bg='white', font=("Helvetica", 16, "bold"))
        self.title_label.pack()

        self.description_label = tk.Label(root, text="Click on the information (text) you want to pick", bg='white', font=("Helvetica", 10))
        self.description_label.pack()

        # Input box for selected text
        self.selected_text_var = tk.StringVar()
        self.input_box_frame = tk.Frame(root, bg='white')
        self.input_box_frame.pack(pady=10)
        self.input_box = tk.Entry(self.input_box_frame, textvariable=self.selected_text_var, bg='#424242', fg='white', font=("Helvetica", 12), width=25)
        self.input_box.pack()

        # Add a stop button
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_script, bg='red', fg='white')
        self.stop_button.pack(pady=5)

        self.stored_text = ""
        self.running = True
        self.target_input_box = self.input_box

        # Bind mouse click event
        self.root.bind("<Button-1>", self.store_text)

        self.update_overlay()

    def capture_screen(self, region):
        # Capture the screen or a region of the screen
        screen = ImageGrab.grab(bbox=region)
        return screen

    def extract_text_boxes_from_image(self, image):
        # Use Tesseract to extract text bounding boxes
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            print(f"Extracted data: {data}")  # Debug statement
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

        print(f"Highlighted text: {highlighted_text}")  # Debug statement
        return highlighted_text

    def store_text(self, event):
        if self.current_highlighted_text:
            print(f"Storing text: {self.current_highlighted_text}")  # Debug statement
            self.target_input_box.delete(0, tk.END)
            self.target_input_box.insert(0, self.current_highlighted_text)

    def stop_script(self):
        self.running = False
        self.root.destroy()

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

            print(f"Capturing region: {region}")  # Debug info

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
