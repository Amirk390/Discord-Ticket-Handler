
# Purple RP Ticket Handler

**Purple RP Ticket Handler** is a graphical user interface (GUI) tool designed to capture and process text from the screen using OCR (Optical Character Recognition). This tool is specifically created for the Purple RP community by TotalStrike.

## Features

- Captures text from the screen with a simple mouse click.
- Extracts text using Tesseract OCR.
- Provides an easy-to-use interface to select and copy text.
- Predefined fields for User Name, Reason, Ban Time, and Ticket ID.
- Auto-populates Ban Time based on predefined values.
- Lookup buttons for past punishments and server logs.
- Copy concatenated text to the clipboard for easy sharing.

## Requirements

- Python 3.6+
- Tesseract OCR
- Python libraries: `pytesseract`, `Pillow`, `pyautogui`, `tkinter`, `pyperclip`, `pynput`

## Installation

1. **Clone the repository**:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install Python dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Install Tesseract OCR**:
    - Download and install Tesseract OCR from [here](https://github.com/UB-Mannheim/tesseract/wiki).
    - Make sure to configure the path to the Tesseract executable in the script (`pytesseract.pytesseract.tesseract_cmd`).

4. **Run the script**:
    ```sh
    python app.py
    ```

## Creating an Executable

To create an executable, follow these steps:

1. **Install PyInstaller**:
    ```sh
    pip install pyinstaller
    ```

2. **Create the executable**:
    ```sh
    pyinstaller --onefile --noconsole --name "PurpleRP_TicketHandler" --icon="path_to_your_icon.ico" --distpath "C:\Users\user\Downloads\DiscordTicketHandler\dist" app.py
    ```

## Usage

1. **Open the application**:
    - Run the executable or use `python app.py`.

2. **Use the interface**:
    - Click on the text you want to capture.
    - The text will be auto-filled into the corresponding fields.
    - Use the lookup buttons for additional functionalities.
    - Click "Copy" to copy the concatenated text to the clipboard.

## Contributing

Feel free to contribute to this project by creating issues or submitting pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

## Acknowledgements

- This program has been created by TotalStrike for the Purple RP community.
- Thanks to the contributors of Tesseract OCR and the Python libraries used in this project.
