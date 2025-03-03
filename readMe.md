# PCDROP

PC Drop is a tool that allows you to quickly and easily transfer files from your phone or other devices to your computer, and vice versa.

## 🚀 Features

- **Easy File Transfer**: Quick file transfer from other devices via QR code or IP address
- **Automatic File Organization**: Automatically organizes incoming files into date-based folders
- **Duplicate File Control**: Option to prevent re-downloading files with the same name
- **Instant Messaging**: Inter-device instant messaging feature
- **Sharing Folder**: Ability to share desired files with other devices
- **User-Friendly Interface**: Modern and easy-to-use graphical interface
- **QR Code Integration**: QR code support for easy connection from mobile devices

## 💻 System Requirements

- Windows operating system
- Python 3.8 or higher

## 🛠️ Installation

### Running from Source Code

1. Install the required Python packages:
```bash
pip install -r requirements.txt
```

2. Start the application:
```bash
python run.py
```

### Running the Compiled Version

1. Download the latest release from the Releases section
2. Extract the downloaded zip file
3. Run the `PcDrop.exe` file

## 🔨 Building the Application

If you want to build the application yourself:

1. Install the required packages:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

2. Run the build script:
```bash
python build.py
```

3. After compilation, the `PcDrop.exe` file will be created in the `dist` folder.

## 📱 Usage

1. Start the application
2. Select the download folder from the "INBOX" section
3. Select the folder you want to share from the "SHARING BOX" section
4. Scan the QR code with your mobile device or open the displayed IP address in a web browser
5. You can send and receive files and messages through the opened web page

## ⚙️ Configuration Options

- **Automatic File Organization**: Automatically organizes incoming files into year/month folders
- **Skip Duplicate Files**: Prevents re-downloading of previously downloaded files

## License

This project is licensed under the [Mozilla Public License 2.0](https://www.mozilla.org/en-US/MPL/2.0/).  

- You are free to use, modify, and distribute this software as long as any modifications to the original source code remain open-source under the same license.  
- Commercial use is allowed, but **if you use this code in a commercial application, you must credit the original source**.  
- You **cannot** take this code and incorporate it into a proprietary project without proper attribution.  

For more details, please refer to the full [MPL-2.0 license text](https://www.mozilla.org/en-US/MPL/2.0/).

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push your branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request




