# **Goal** :

to develop the personal assistant for Windows PCs or laptops which are capable of accepting user’s voice input and executing Operating System level commands such as restarting, shut down, opening files, etc

# Description : 

- This project utilizes Python's open-source ecosystem (libraries, modules, and APIs) to develop a high-performance personal assistant for desktop environments.
- **Supported OS**: Windows 10 and 11.
- **Core Logic (Hybrid Intent Detection)**:
    - **Primary**: LLM-based Intent Classification (Ollama/OpenAI) to understand natural language and complex requests.
    - **Fallback/Safety**: Hard-coded keyword matching for critical OS-level tasks (e.g., shutdown, restart) to ensure reliability.
- **Voice Interaction**: Uses `SpeechRecognition` with noise reduction for input and `ElevenLabs` (Premium) or `pyttsx3` (Offline/Fast) for output.
- **Execution Environment**: Packaged as a background executable that initializes on system startup.
- **Interface**: A modern GUI (CustomTkinter) for configuration, history tracking, and manual interaction.
- **Design Philosophy**: Minimizing keyboard dependency while providing a "premium" assistant experience (akin to Jarvis).  
- Default Name of Assistant : LOQ  
- Suggested Name : Jarvis, Hercules, Optimus,   
- Available voice models from ElevenLabs: 


| Name | Voice ID |
| :---- | :---- |
| Mark | UgBBYS2sOqTuMpoF3BR0 |
| Jessica | cgSgspJ2msm6clMCkdW9 |
| Brian | nPczCjzI2devNBz1zQrb |
| lily | pFZP5JQG7iQjIQuC4Bku |


# **Objectives :** 

1. To reduce the minor tasks   
2. Reducing dependency on keyboards for minor tasks  
3. Enhancing user experience   
4. To Upskill 

# **Expected Outcomes** 

1. Personal Assistant runs successfully in background  
2. Accepts voice input from user correctly   
3. Executes the OS level commands successfully.

# **Project Roadmap (Tasks):** 

1. **Phase 1: Foundation**
    - [x] Analyze requirements and create `PROJECT_CONTEXT.md`.
    - [ ] Initialize project structure and Git repository.
    - [ ] Create virtual environment and install core dependencies.
2. **Phase 2: Core Engine**
    - [ ] Implement `OS_Automation` layer (System, Apps, Browser control).
    - [ ] Develop `STT_Engine` using SpeechRecognition and Vosk for offline fallback.
    - [ ] Develop `TTS_Engine` with dual-mode support (ElevenLabs/Pyttsx3).
3. **Phase 3: Intelligence Layer**
    - [ ] Integrate **Ollama** for local NLP intent detection.
    - [ ] Implement Hybrid logic: LLM for general queries, Hard-coded for critical OS actions.
    - [ ] Implement persistent memory (SQLite) for context and user preferences.
4. **Phase 4: Interface & Background**
    - [ ] Design and build CustomTkinter GUI.
    - [ ] Implement background service logic and system tray integration.
    - [ ] Add Auto-start functionality via Windows Startup.
5. **Phase 5: Polish & Deployment**
    - [ ] Noise cancellation tuning for better STT accuracy.
    - [ ] Package as `.exe` using PyInstaller.
    - [ ] Security audit: Ensure commands don't execute without proper context/confirmation.

# **Recommended Project Structure:**

```text
Personal_Assistant/
├── main.py                 # Entry point (Background service + GUI)
├── config/
│   ├── settings.json       # User preferences, API keys, Voice IDs
│   └── commands.json       # Hard-coded keyword mappings
├── core/
│   ├── intent_engine.py    # Hybrid Logic (LLM + Keyword Matching)
│   ├── automation.py       # OS, Browser, and App control logic
│   ├── stt.py              # Speech-to-Text implementation
│   └── tts.py              # Text-to-Speech implementation
├── ui/
│   ├── app.py              # CustomTkinter GUI components
│   └── assets/             # Icons, animations, sounds
├── data/
│   └── memory.db           # SQLite database for history and long-term memory
├── utils/
│   ├── logger.py           # Application logging
│   └── security.py         # Permission and safety checks
├── requirements.txt        # Project dependencies
└── PROJECT_CONTEXT.md      # This file
```

# **Tech stack:** 

| Component | Recommended |
| ----- | ----- |
| Programming Language | Python |
| Voice Input | SpeechRecognition |
| Offline STT (better) | Vosk |
| AI/NLP | Ollama or OpenAI API |
| Text-to-Speech | Pyttsx3 / eleven labs |
| GUI | CustomTkinter |
| OS Automation | os \+ subprocess \+ pyautogui |
| Wake Word | Porcupine / openWakeWord |
| Auto Start | Windows Startup Folder |
| Memory | SQLite / JSON |
| Local AI Model | Ollama  |

# **Flowchart :** 

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
Voice/Text Response

# **Commands :** 

## Major Categories of Commands 

| Category | Examples |
| ----- | ----- |
| System Control | Shutdown, restart, sleep |
| Application Control | Open/close apps |
| File Management | Create/delete/move files |
| Browser Automation | Open websites/search |
| Audio Control | Volume up/down/mute |
| Network Control | WiFi/Bluetooth |
| Hardware Control | Webcam, mic |
| Media Control | Play/pause music |
| Productivity | Notes, reminders |
| Security | Lock PC |
| Monitoring | CPU/RAM/battery |

## System Control Commands : 

| Voice Command | Action |
| ----- | ----- |
| shutdown pc | Shutdown |
| restart pc | Restart |
| sleep pc | Sleep |
| hibernate pc | Hibernate |
| lock pc | Lock Windows |
| sign out | Logout |
| cancel shutdown | Abort shutdown |
| open task manager | Launch task manager |
| open control panel | Open control panel |
| open settings | Open Windows settings |
| check battery | Speak battery level |
| check cpu usage | Show CPU usage |
| check ram usage | Show memory usage |
| clear temp files | Delete temporary files |
| empty recycle bin | Clear recycle bin |

## Application Control : 

| Command | Action |
| ----- | ----- |
| open chrome | Launch Chrome |
| open vscode | Launch VS Code |
| open spotify | Open Spotify |
| open discord | Launch Discord |
| close chrome | Kill Chrome |
| minimize all windows | Show desktop |
| switch window | ALT+TAB |
| maximize window | Maximize active window |
| close current window | ALT+F4 |

## File and Folder Management : 

| Command | Action |
| ----- | ----- |
| create folder projects | Create folder |
| delete file notes.txt | Delete file |
| move file to downloads | Move file |
| rename file | Rename |
| search file | Find file |
| open downloads | Open Downloads |
| open desktop | Open Desktop |
| zip this folder | Compress folder |
| extract zip | Extract archive |

## Internet and Browsing 

| Command | Action |
| ----- | ----- |
| open youtube | Open YouTube |
| search google for AI news | Search |
| open github | Launch GitHub |
| open linkedin | Open LinkedIn |
| play lofi music | Search/play |
| open chatgpt | Open ChatGPT |
| download file | Download content |
| summarize webpage | AI summarize |
| read article aloud | Text-to-speech |

## Audio Commands : 

| Command | Action |
| ----- | ----- |
| volume up | Increase volume |
| volume down | Decrease volume |
| mute pc | Mute |
| unmute pc | Unmute |
| set volume to 50 percent | Set exact volume |
| next song | Media next |
| previous song | Media previous |
| pause music | Pause |
| play music | Resume |

## Windows setting control 

| Command | Action |
| ----- | ----- |
| turn on bluetooth | Bluetooth |
| turn off wifi | Disable WiFi |
| enable dark mode | Change theme |
| increase brightness | Brightness |
| turn on hotspot | Hotspot |
| connect to wifi | WiFi |

# **Safety & Security :** 

1. **Confirmation Prompt**: Critical commands like `Shutdown` or `Delete File` should require a voice confirmation ("Are you sure?").
2. **Path Sanitization**: Ensure file management commands cannot access system-critical directories outside of user space.
3. **API Key Safety**: Store API keys in environment variables or encrypted config files, never hard-coded.
4. **Admin Privileges**: The app should check for administrative privileges when attempting commands like `restart pc`.

# **Challenges :** 

1. **Context Awareness**: Distinguishing between a command and normal conversation.
2. **Ambient Noise**: Filtering background sounds for reliable STT in various environments.
3. **Execution Latency**: Balancing LLM response time with the need for "instant" assistant feel.
4. **Offline Capability**: Ensuring basic OS commands work even without an internet connection (using Vosk + local scripts).
5. **Privacy**: Ensuring the microphone is only "active" when the wake word is detected or manual start is toggled.

# **Future Scope** 

1. Using Open Source LLM for NLP and text processing.  
2. Memory for Personal Assistant   
3. Integrated Database   
4. Advanced Operating System control (such as scrolling, making to-do lists, crafting emails)

# **UI Elements** 

1. Stop button : Stops the program (assistant stops listening, history retained, timer pause)   
2. Start button : starts the program (assistant starts listening)  
3. Restart button : restarts the program (all history deleted and timer resets)  
4. Change name: customize the name of assistant   
5. Change Voice: customize voice of assistant (elevenlabs API)  
6. History : list of all executed commands with time of execution   
7. Time : running time of program since it started.  
8. Sidebar : future Scope   
9. Animation (future scope):   
1. Animated Robotic face : moving eyes and mouth  
2. Animated sound waves : vibrates as assistant talks

