# PCDROP

## About the Project

**pc-drop** is a file transfer web application based on FastAPI and includes a Tkinter GUI for selecting files. This project provides users with a platform to perform file transfers quickly and easily.

![image](https://github.com/user-attachments/assets/bba74871-e50c-44b3-b78f-043f9200095d)

![image](https://github.com/user-attachments/assets/4eeb4c79-fce0-43e1-b9f1-a0d57eb9a021)

![image](https://github.com/user-attachments/assets/2832c6ae-ce31-4a32-b8fd-e11764f8838b)




## Requirements

The following requirements must be installed for the project to work:

- Python 3.13 or higher
- The following Python libraries:
  - FastAPI
  - Uvicorn
  - Jinja2
  - Aiofiles

## Running the Project

run app.py

## Build the Application

You can use `build.py` to automate the building of the project into a single executable file using PyInstaller. This will allow your application to run as a standalone `.exe` file on Windows.

### 1. Run `build.py`

To build the application, run the `build.py` script with the following command:


This script will compile the project into a single executable file.

### 2. Access the Dist Folder

After the build process, the compiled `.exe` file will be located in the `dist/` folder. This file will be a runnable executable on Windows operating systems.

### 3. Use the Executable File

Navigate to the `dist/` folder and double-click the `app.exe` file to run it. This file will allow your application to run independently, including the FastAPI and Tkinter GUI components.

## License

This project is licensed under the MIT License. For more details, refer to the LICENSE file.




