# Personal Assistant: Executable Conversion & Startup Guide

This guide provides step-by-step instructions to convert your Python-based Tkinter/CustomTkinter Personal Assistant into a standalone Windows `.exe` application and configure it to launch automatically when your PC starts.

## 1. Preparing the Environment

First, ensure you are using the correct Anaconda virtual environment where all your dependencies are installed.

1. Open your terminal (or Anaconda Prompt).
2. Activate your environment:
   ```powershell
   conda activate assist
   ```
3. Verify that `pyinstaller` is installed (it's listed in your `requirements.txt`):
   ```powershell
   pip install pyinstaller
   ```

## 2. Compiling the Executable

Since your application uses external assets (models, configurations, UI images) and complex libraries like `customtkinter` and `openwakeword`, we need to tell PyInstaller to bundle them.

Run the following command from the root of your project directory (`d:\projects\Personal_Assistant`):

```powershell
pyinstaller --noconfirm --onedir --windowed --name "PersonalAssistant" --add-data "config;config" --add-data "models;models" --add-data "ui/assets;ui/assets" --add-data ".env;." --collect-all customtkinter --collect-all openwakeword --icon "ui/assets/icon_logo.png" main.py
```

### Understanding the Flags:
*   `--noconfirm`: Automatically overwrite the output directory if it already exists.
*   `--onedir`: Creates a 1-folder bundle containing the `.exe` and all its dependencies. **Highly recommended** over `--onefile` because `--onefile` extracts heavy AI models and libraries to a temporary folder every time you launch, making startup extremely slow.
*   `--windowed`: Prevents the console window from appearing when you run the application (ideal for GUI apps). If you need to see terminal logs for debugging later, you can remove this flag.
*   `--name`: Names the output file (e.g., `PersonalAssistant.exe`).
*   `--add-data`: Bundles your custom folders (`config`, `models`, `ui/assets`) and your `.env` file so the exe can find them at runtime.
*   `--collect-all`: Forces PyInstaller to include all hidden imports and data files for tricky libraries like `customtkinter` and `openwakeword`.
*   `--icon`: Sets the application icon.

### Locating the Output
Once the process finishes, a new folder named `dist` will be created in your project folder. Inside `dist\PersonalAssistant`, you will find your **`PersonalAssistant.exe`** file along with its required libraries.

## 3. Adding the App to Windows Startup

To make the assistant instantly available when your PC starts:

1. Navigate to the `dist\PersonalAssistant` folder in File Explorer.
2. Right-click on **`PersonalAssistant.exe`** and select **Create shortcut**.
3. Press `Win + R` on your keyboard to open the Run dialog.
4. Type `shell:startup` and press **Enter**. This opens the Windows Startup folder.
5. **Move or cut/paste** the newly created shortcut from your `dist` folder into this Startup folder.

> [!TIP]
> Do not move the actual `.exe` file out of the `dist\PersonalAssistant` folder, as it needs to remain next to all the bundled DLLs, models, and configuration files. Always move the **shortcut** instead.

## 4. Troubleshooting Runtime Issues

If the `.exe` fails to launch or crashes silently:
1. Re-compile the application without the `--windowed` flag to see the console output.
2. Launch the new `.exe` from a command prompt to read the error traceback (often related to a missing file or pathing issue in one of the modules).
3. If specific files are missing, you can add them by modifying the generated `PersonalAssistant.spec` file and running `pyinstaller PersonalAssistant.spec`.
