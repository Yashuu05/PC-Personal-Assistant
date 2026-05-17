# *PC Personal Assistant*

# ABOUT

### Overview
- The project is about building a Basic Perosnal Assistant for windows users specifically for PCs or laptops.
- The Personal Assistant acts as a helping hand while you work on PC / laptop.
- The Assistant accepts the voice from user as input and execute the commands by interacting with the OS (Operating System)
- Example: opening a file, restarting PC, shut down PC, opening application and so on just by speaking.

### **Goal** :

to develop the personal assistant for Windows PCs or laptops which are capable of accepting user’s voice input and executing Operating System level commands such as restarting, shut down, opening files, etc

### **Objectives :** 

1. To reduce the minor tasks   
2. Reducing dependency on keyboards for minor tasks  
3. Enhancing user experience   
4. To Upskill 

### **Expected Outcomes** 

1. Personal Assistant runs successfully in background  
2. Accepts voice input from user correctly   
3. Executes the OS level commands successfully

### Project Structure

```text
Personal_Assistant/
├── main.py                 # Entry point (Background service + GUI)
├── config/
│   |__ settings.json
|   |__ commands.json
├── core/
│   ├── intent_engine.py    # Hybrid Logic (LLM + Keyword Matching)
│   ├── automation.py       # OS, Browser, and App control logic
│   ├── stt.py              # Speech-to-Text implementation
│   └── tts.py              # Text-to-Speech implementation
|__ design/
    |__ DESIGN.md
    |__ code.html
    |__ screen.png
|__ logs/
├── ui/
│   ├── app.py              # CustomTkinter GUI components
│   └── assets/             # Icons, animations, sounds
├── utils/
│   ├── logger.py           # Application logging
│   └── security.py         # Permission and safety checks
|__ .gitignore
|__ readme.md
├── requirements.txt        # Project dependencies
└── PROJECT_CONTEXT.md      # This file
```
# **Tech stack:** 

| Component | Recommended |
| ----- | ----- |
| Programming Language | Python |
| Voice Input | SpeechRecognition |
| Offline STT | Vosk |
| Text-to-Speech | Pyttsx3 / TTS |
| GUI | CustomTkinter |
| OS Automation | os \+ subprocess \+ pyautogui |
| Wake Word | Porcupine / openWakeWord |
| Auto Start | Windows Startup Folder |

---
# **Flowchart :** 

```
Microphone Input  
      ↓  
Speech-to-Text (STT)  
      ↓  
Command Processing / AI Brain  
      ↓  
Intent Detection  
      ↓  
OS Automation Layer  
      ↓  
Windows Executes Command  
      ↓  
Voice Respons
```
---


### Features: 

1. Multithreaded Non-Blocking Loop: Clicking START Listening now dispatches your voice capture (stt.py), intent matching (config/commands.json), and speech synthesis (tts.py) to a background daemon thread via run_cycle_async().
This ensures that 25-FPS sine-wave visualizers, LED pulses, and system telemetry progress bars never stutter or freeze while the assistant is capturing or generating audio.
2. Dynamic UI Option Mapping: Every time a voice cycle is triggered, the GUI reads the currently selected dropdown configurations dynamically. Selecting "Jessica (gTTS)", "Lily (ElevenLabs)", "Brian (ElevenLabs)", or "Mark (pyttsx3)" instantly routes the core synthesis engine to that specific voice profile.
3. Continuous Voice Loop: When a command finishes executing, on_cycle_finished() is called back on the main thread. It prints the logs, updates status labels, and automatically schedules the next cycle recursively after a short 1.2-second delay. This creates a fully hands-free, continuous conversational loop.
4. Custom Security Alerts: Any critical system commands (like PC shutdowns, restarts, or log-outs) are routed through a secure, GUI-friendly CustomTkinter-themed dialog (messagebox.askyesno). LOQ will pause and prompt you: "Do you want to authorize this operation?" before executing any destructive shells.
5. Instant Interruptive Stops: Clicking STOP or RESET LOG instantly updates the state flag and triggers self.assistant.stop(), terminating any ongoing cloud or offline audio playback immediately.
6. Dynamic Branding: The log console reads your assistant's name dynamically from the settings input. If you change the assistant's name in the entry field to something else (e.g., "Jarvis"), the logs will instantly shift from printing LOQ: "opening notepad" to Jarvis: "opening notepad".
7. Test Voice Controls: Click START Listening, wait for the LED to pulse cyan, and speak clearly: "Open Calculator" or "Please open notepad" $\rightarrow$ Watch the visualizer pulse active audio frequencies, hear the assistant speak the feedback, see the command logs print live on the console, and watch your application launch!
8.Test Security Alerts: Speak: "Shutdown PC" $\rightarrow$ LOQ will pop up a confirmation window and wait for your click before running any shell scripts

---

### **UI Elements** 

1. Stop button : Stops the program (assistant stops listening, history retained, timer pause)   
2. Start button : starts the program (assistant starts listening)  
3. Restart button : restarts the program (all history deleted and timer resets)  
4. Change name: customize the name of assistant   
5. Change Voice: customize voice of assistant (elevenlabs API)  
6. History : list of all executed commands with time of execution   
7. Time : running time of program since it started.  
8. Sidebar : for voice and mode settings
2. Animated sine waves : vibrates as assistant executes command

---

### **Future Scope** 

1. Using Open Source LLM for NLP and text processing.  
2. Memory for Personal Assistant   
3. Integrated Database   
4. Advanced Operating System control (such as scrolling, making to-do lists, crafting emails)

---
# **Challenges :** 

1. **Context Awareness**: Distinguishing between a command and normal conversation.
2. **Ambient Noise**: Filtering background sounds for reliable STT in various environments.
3. **Execution Latency**: Balancing LLM response time with the need for "instant" assistant feel.
4. **Offline Capability**: Ensuring basic OS commands work even without an internet connection (using Vosk + local scripts).
5. **Privacy**: Ensuring the microphone is only "active" when the wake word is detected or manual start is toggled.

---
### Installation Guide:

# Clone the repository  
```
git clone https://github.com/Yashuu05/PC-Personal-Assistant.git  
```

# Navigate to the project directory  
```
cd PC-Personal-Assistant
```  

# Create and activate the virtual environment (for Windows)  
```
python -m venv myenv 
# or

# using anaconda
conda create -n myenv python=3.x
```  

# Install dependencies  
```
pip install -r requirements.txt 
```

# Run the application  
```
cd ui
python app.py
```
---

### Aknowledgements

- [Google](https://google.com/)
- [Stack Overflow](https://stackoverflow.com/)
- [GitHub](https://github.com/)
- [Antigravity](https://antigravity.google/)
- [python](https://docs.python.org/)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
- [ElevenLabs](https://elevenlabs.io/)
- [pyttsx3](https://pypi.org/project/pyttsx3/)

### NOTE: This project is in progress. 
### STATUS : ACTIVE 
