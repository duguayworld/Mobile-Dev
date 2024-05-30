Password Sharing Application

**Overview**

This mobile application facilitates the secure sharing of passwords between two instances using a secure socket connection. The connection is established through the scanning or uploading of a QR code, ensuring a straightforward and user-friendly experience.

Features:

  Secure Password Sharing: Utilizes a secure socket connection to share passwords safely between devices.
  QR Code Integration: Establish connections by scanning a QR code with the device camera (using OpenCV) or by uploading an image of the QR code.
  User-Friendly Interface: Built with Tkinter, it is not the best but it's manageable.
  JSON File Handling: Creates and shares a .json file containing usernames and passwords during the connection process.
  Cross-Platform Compatibility: Currently in development to ensure compatibility across various mobile platforms.

![screenshots](https://github.com/duguayworld/Mobile-Dev/assets/153779837/a9a09e98-3026-48b9-b009-c8561c8c4c89)

Technical Details:

  Programming Language: Python 3.12
  GUI Framework: Tkinter
  Image Processing: OpenCV for QR code scanning
  Data Format: JSON for storing and sharing passwords

Setup and Installation:

  Prerequisites:
  Python 3.12 or higher
  Required Python libraries: OpenCV, Tkinter, and any other dependencies listed in requirements.txt

**Installation:**

    git clone https://github.com/duguayworld/Mobile-Dev/password-share.git

**Navigate to the project directory:**

    cd password-sharing-app

**Install dependencies:**

    pip install -r requirements.txt

**Running the Application:**

    python mobile_app.py

**Usage**

    Establishing Connection:
    Create or Use an application that shares a socket connection QR Code on any device.
    
    Sharing Passwords:
    The app will automatically create a .json file with usernames and passwords.
    The file is securely shared between the connected instances via web socket connection.
