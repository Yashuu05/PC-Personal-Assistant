"""
CustomTkinter GUI Layout for PC Personal Assistant (LOQ).
Fulfills Phase 1: Implements the premium, neon-futuristic visual structure, 
animated visualizers, real-time system monitoring, and core control panel layouts.
"""

import os
import sys
import time
import math
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Add project root to sys.path to ensure absolute imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.speech_to_speech import SpeechToSpeechSystem

# Fallback for CPU/RAM status monitoring if psutil isn't in virtualenv
try:
    import psutil
except ImportError:
    psutil = None

# Configure CustomTkinter appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LOQVisualizer(ctk.CTkCanvas):
    """
    High-tech premium Canvas Visualizer drawing animated glowing audio waves.
    Changes dynamics based on assistant states (Idle, Listening, Processing, Stopped).
    """
    def __init__(self, master, **kwargs):
        # Set dark-matte charcoal canvas background
        kwargs.setdefault("bg", "#1A1A1B")
        kwargs.setdefault("highlightthickness", 0)
        super().__init__(master, **kwargs)
        
        self.phase = 0.0
        self.state = "Idle"  # Idle, Listening, Processing, Stopped
        self.amplitude = 15.0
        self.animate()

    def set_state(self, state):
        self.state = state
        if state == "Listening":
            self.amplitude = 40.0
        elif state == "Processing":
            self.amplitude = 25.0
        elif state == "Stopped":
            self.amplitude = 0.0
        else:
            self.amplitude = 15.0

    def animate(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width > 1 and height > 1:
            mid_y = height / 2
            self.phase += 0.15
            
            if self.state == "Stopped":
                # Flat red line
                self.create_line(0, mid_y, width, mid_y, fill="#E74C3C", width=2)
            elif self.state == "Processing":
                # Glowing concentric circular pulses (Jarvis-like ring visualizer)
                pulse_r1 = 40 + math.sin(self.phase) * 10
                pulse_r2 = 60 + math.cos(self.phase) * 5
                
                cx, cy = width / 2, height / 2
                self.create_oval(cx - pulse_r2, cy - pulse_r2, cx + pulse_r2, cy + pulse_r2, outline="#FFD700", width=1, stipple="gray25")
                self.create_oval(cx - pulse_r1, cy - pulse_r1, cx + pulse_r1, cy + pulse_r1, outline="#00D4FF", width=3)
                self.create_oval(cx - 15, cy - 15, cx + 15, cy + 15, fill="#00D4FF")
            else:
                # Glowing overlapping sine waves
                colors = ["#00586B", "#00D4FF", "#A8E8FF"]
                opacities = [1, 2, 3] # Represent widths
                
                # Draw 3 offset waves
                for i in range(3):
                    points = []
                    freq = 0.015 + (i * 0.005)
                    speed_offset = self.phase + (i * 1.5)
                    
                    for x in range(0, width, 5):
                        # Fade out waves at boundaries to create elegant visual tapering
                        boundary_fade = math.sin(math.pi * x / width)
                        y = mid_y + (self.amplitude * boundary_fade) * math.sin(x * freq - speed_offset)
                        points.append((x, y))
                        
                    # Draw continuous smooth line
                    self.create_line(points, fill=colors[i], width=opacities[i], smooth=True)
                    
        # Request next animation frame in 40ms (~25 FPS)
        self.after(40, self.animate)


class GlowingStatusLED(ctk.CTkCanvas):
    """Circular glowing status LED reflecting the current operational state."""
    def __init__(self, master, **kwargs):
        kwargs.setdefault("bg", "#0e1417")
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("width", 30)
        kwargs.setdefault("height", 30)
        super().__init__(master, **kwargs)
        self.state = "Idle"
        self.pulse = 0.0
        self.animate()

    def set_state(self, state):
        self.state = state

    def animate(self):
        self.delete("all")
        self.pulse += 0.1
        
        # Color mapper
        state_colors = {
            "Idle": "#2ECC71",       # Green
            "Listening": "#00D4FF",  # Cyan
            "Processing": "#FFD700", # Gold
            "Stopped": "#E74C3C"     # Red
        }
        color = state_colors.get(self.state, "#2ECC71")
        
        # Draw pulsing outer glow ring
        glow_add = 0.0
        if self.state in ["Listening", "Processing"]:
            glow_add = math.sin(self.pulse) * 3
            
        r_glow = 12 + glow_add
        r_inner = 7
        
        # Center coordinates
        cx, cy = 15, 15
        
        # Outer glow
        self.create_oval(cx - r_glow, cy - r_glow, cx + r_glow, cy + r_glow, fill=color, stipple="gray25", outline="")
        # Inner LED solid core
        self.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner, fill=color, outline="#ffffff", width=1)
        
        self.after(100, self.animate)


class PersonalAssistantApp(ctk.CTk):
    """
    Main CustomTkinter Frontend Layout Class.
    Implements:
      - Left Sidebar (Settings + Live System Telemetry)
      - Right Main Panel (AI Wave Visualizer + Scrollable Log Console)
      - Controls Footer (Play, Stop, Restart buttons + Session Timer)
    """
    def __init__(self):
        super().__init__()
        
        # 1. Main Window Settings
        self.title("LOQ - Futuristic Personal Assistant")
        self.geometry("850x650")
        self.configure(fg_color="#0e1417") # Design specification deep charcoal
        
        self.grid_columnconfigure(0, weight=0, minsize=280) # Sidebar
        self.grid_columnconfigure(1, weight=1)              # Main Panel
        self.grid_rowconfigure(0, weight=1)
        
        # Session state variables
        self.session_active = False
        self.start_time = None
        self.elapsed_time_secs = 0
        self.assistant_state = "Idle"
        
        # 2. Build Components
        self.create_sidebar()
        self.create_main_panel()
        self.create_footer()
        
        # 3. Core Voice Assistant Engine
        self.assistant = SpeechToSpeechSystem(tts_method="gtts", voice_name="Jessica")
        
        # 3. Start Telemetry and Timers
        self.update_telemetry()
        self.update_timer_loop()
        
        # Add welcome print to log console
        self.append_log("LOQ", "System initialized and ready in Standby Mode.")
        self.append_log("System", "Select a voice model and press Start to initialize listening loop.")

    def create_sidebar(self):
        """Creates the styled personalization and telemetry side panel."""
        sidebar = ctk.CTkFrame(self, fg_color="#161d1f", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Sidebar Logo
        logo_label = ctk.CTkLabel(sidebar, text="LOQ OS", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color="#00D4FF")
        logo_label.pack(pady=(30, 20), padx=20)
        
        # Subtitle Divider
        divider = ctk.CTkFrame(sidebar, height=2, fg_color="#3c494e")
        divider.pack(fill="x", padx=30, pady=(0, 25))
        
        # Group 1: Personalization Panel
        personalization_frame = ctk.CTkFrame(sidebar, fg_color="#1a2123", corner_radius=10)
        personalization_frame.pack(fill="x", padx=15, pady=10)
        
        p_title = ctk.CTkLabel(personalization_frame, text="PERSONALIZATION", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#859398")
        p_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Name Entry
        name_label = ctk.CTkLabel(personalization_frame, text="Assistant Name:", font=ctk.CTkFont(family="Inter", size=12), text_color="#bbc9cf")
        name_label.pack(anchor="w", padx=15, pady=(5, 0))
        
        self.name_entry = ctk.CTkEntry(personalization_frame, placeholder_text="LOQ", fg_color="#0e1417", border_color="#3c494e", text_color="#dde3e7", height=32)
        self.name_entry.insert(0, "LOQ")
        self.name_entry.pack(fill="x", padx=15, pady=(2, 10))
        
        # Voice Dropdown Selector
        voice_label = ctk.CTkLabel(personalization_frame, text="Active Voice (TTS):", font=ctk.CTkFont(family="Inter", size=12), text_color="#bbc9cf")
        voice_label.pack(anchor="w", padx=15, pady=(5, 0))
        
        self.voice_dropdown = ctk.CTkOptionMenu(
            personalization_frame, 
            values=["Jessica (gTTS)", "Lily (ElevenLabs)", "Brian (ElevenLabs)", "Mark (pyttsx3)"],
            fg_color="#0e1417",
            button_color="#242b2e",
            button_hover_color="#333a3d",
            dropdown_fg_color="#161d1f",
            dropdown_hover_color="#242b2e",
            text_color="#dde3e7",
            height=32
        )
        self.voice_dropdown.set("Jessica (gTTS)")
        self.voice_dropdown.pack(fill="x", padx=15, pady=(2, 15))
        
        # Group 2: Live Telemetry Dashboard
        telemetry_frame = ctk.CTkFrame(sidebar, fg_color="#1a2123", corner_radius=10)
        telemetry_frame.pack(fill="both", expand=True, padx=15, pady=(10, 20))
        
        t_title = ctk.CTkLabel(telemetry_frame, text="LIVE TELEMETRY", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#859398")
        t_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # CPU Display
        self.cpu_label = ctk.CTkLabel(telemetry_frame, text="CPU Usage: 0%", font=ctk.CTkFont(family="JetBrains Mono", size=12), text_color="#bbc9cf")
        self.cpu_label.pack(anchor="w", padx=15, pady=5)
        self.cpu_bar = ctk.CTkProgressBar(telemetry_frame, progress_color="#00D4FF", fg_color="#0e1417", height=6)
        self.cpu_bar.set(0.0)
        self.cpu_bar.pack(fill="x", padx=15, pady=(0, 15))
        
        # RAM Display
        self.ram_label = ctk.CTkLabel(telemetry_frame, text="RAM Usage: 0%", font=ctk.CTkFont(family="JetBrains Mono", size=12), text_color="#bbc9cf")
        self.ram_label.pack(anchor="w", padx=15, pady=5)
        self.ram_bar = ctk.CTkProgressBar(telemetry_frame, progress_color="#FFD700", fg_color="#0e1417", height=6)
        self.ram_bar.set(0.0)
        self.ram_bar.pack(fill="x", padx=15, pady=(0, 15))
        
        # Battery Display
        self.battery_label = ctk.CTkLabel(telemetry_frame, text="Battery: 100% (AC)", font=ctk.CTkFont(family="JetBrains Mono", size=12), text_color="#bbc9cf")
        self.battery_label.pack(anchor="w", padx=15, pady=5)
        self.battery_bar = ctk.CTkProgressBar(telemetry_frame, progress_color="#2ECC71", fg_color="#0e1417", height=6)
        self.battery_bar.set(1.0)
        self.battery_bar.pack(fill="x", padx=15, pady=(0, 15))

    def create_main_panel(self):
        """Creates the main visual presentation area."""
        main_panel = ctk.CTkFrame(self, fg_color="#0e1417", corner_radius=0)
        main_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=(20, 10))
        
        main_panel.grid_rowconfigure(0, weight=0) # Header title
        main_panel.grid_rowconfigure(1, weight=3) # Visualizer
        main_panel.grid_rowconfigure(2, weight=4) # Console history
        main_panel.grid_columnconfigure(0, weight=1)
        
        # Header bar
        header_frame = ctk.CTkFrame(main_panel, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        self.indicator_led = GlowingStatusLED(header_frame)
        self.indicator_led.pack(side="left", padx=(5, 10))
        
        self.status_label = ctk.CTkLabel(header_frame, text="SYSTEM STATUS: STANDBY", font=ctk.CTkFont(family="Inter", size=15, weight="bold"), text_color="#2ECC71")
        self.status_label.pack(side="left")
        
        # AI Wave Visualizer
        visualizer_container = ctk.CTkFrame(main_panel, fg_color="#1A1A1B", border_color="#3c494e", border_width=1, corner_radius=12)
        visualizer_container.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        
        self.visualizer = LOQVisualizer(visualizer_container)
        self.visualizer.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Command History Log Console
        console_container = ctk.CTkFrame(main_panel, fg_color="#080f12", border_color="#3c494e", border_width=1, corner_radius=12)
        console_container.grid(row=2, column=0, sticky="nsew")
        
        c_title = ctk.CTkLabel(console_container, text="COMMAND HISTORY CONSOLE LOG", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#859398")
        c_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        self.console_textbox = ctk.CTkTextbox(
            console_container, 
            fg_color="#080f12", 
            text_color="#dde3e7", 
            font=ctk.CTkFont(family="JetBrains Mono", size=13),
            wrap="word",
            corner_radius=0
        )
        self.console_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.console_textbox.configure(state="disabled") # Set read-only by default

    def create_footer(self):
        """Creates the bottom panel hosting buttons and the session duration indicator."""
        footer_frame = ctk.CTkFrame(self, fg_color="#0e1417", height=70, corner_radius=0)
        footer_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20))
        
        # Action Buttons Layout (Left side of footer)
        # 1. Start Listening Button
        self.start_btn = ctk.CTkButton(
            footer_frame,
            text="START Listening",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#00586B",
            hover_color="#00D4FF",
            border_color="#00D4FF",
            border_width=1,
            text_color="#A8E8FF",
            corner_radius=10,
            width=150,
            height=40,
            command=self.start_action
        )
        self.start_btn.pack(side="left", padx=5)
        
        # 2. Stop Listening Button
        self.stop_btn = ctk.CTkButton(
            footer_frame,
            text="STOP",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#2b3134",
            hover_color="#E74C3C",
            border_color="#E74C3C",
            border_width=1,
            text_color="#bbc9cf",
            corner_radius=10,
            width=100,
            height=40,
            command=self.stop_action
        )
        self.stop_btn.pack(side="left", padx=5)
        
        # 3. Restart/Reset Button
        self.restart_btn = ctk.CTkButton(
            footer_frame,
            text="RESET LOG",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="transparent",
            hover_color="#333a3d",
            border_color="#3c494e",
            border_width=1,
            text_color="#bbc9cf",
            corner_radius=10,
            width=110,
            height=40,
            command=self.restart_action
        )
        self.restart_btn.pack(side="left", padx=5)
        
        # Session Timer (Right side of footer)
        self.timer_label = ctk.CTkLabel(
            footer_frame,
            text="SESSION TIME: 00:00:00",
            font=ctk.CTkFont(family="JetBrains Mono", size=14, weight="bold"),
            text_color="#FFD700"
        )
        self.timer_label.pack(side="right", padx=10)

    # ----------------- UI Operational Logic & Telemetry -----------------

    def append_log(self, sender, message):
        """Helper to print timestamped logs cleanly inside the read-only textbox."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {sender}: {message}\n"
        
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert("end", log_entry)
        self.console_textbox.configure(state="disabled")
        
        # Auto-scroll console to the very bottom
        self.console_textbox.see("end")

    def update_telemetry(self):
        """Gathers system CPU, RAM, and Battery states dynamically in background."""
        # 1. Update CPU telemetry
        cpu_val = 0.0
        if psutil:
            try:
                cpu_val = psutil.cpu_percent()
            except Exception:
                pass
        else:
            # Safe sin-drifting simulation if psutil isn't installed
            cpu_val = round(15.0 + math.sin(time.time() * 0.1) * 10.0, 1)
            
        self.cpu_label.configure(text=f"CPU Usage: {cpu_val}%")
        self.cpu_bar.set(min(max(cpu_val / 100.0, 0.0), 1.0))
        
        # 2. Update RAM telemetry
        ram_val = 0.0
        if psutil:
            try:
                ram_val = psutil.virtual_memory().percent
            except Exception:
                pass
        else:
            # Safe sin-drifting simulation if psutil isn't installed
            ram_val = round(45.0 + math.cos(time.time() * 0.05) * 5.0, 1)
            
        self.ram_label.configure(text=f"RAM Usage: {ram_val}%")
        self.ram_bar.set(min(max(ram_val / 100.0, 0.0), 1.0))
        
        # 3. Update Battery/Charging telemetry
        bat_pct = 100
        charging_str = "AC"
        if psutil and hasattr(psutil, "sensors_battery"):
            try:
                battery = psutil.sensors_battery()
                if battery:
                    bat_pct = battery.percent
                    charging_str = "Charging" if battery.power_plugged else "Discharging"
            except Exception:
                pass
        else:
            bat_pct = 95
            charging_str = "AC Power"
            
        self.battery_label.configure(text=f"Battery: {bat_pct}% ({charging_str})")
        self.battery_bar.set(bat_pct / 100.0)
        
        # Schedule next update in 1 second
        self.after(1000, self.update_telemetry)

    def update_timer_loop(self):
        """Updates the session clock every second if listening is active."""
        if self.session_active:
            self.elapsed_time_secs = int(time.time() - self.start_time)
            
            hours = self.elapsed_time_secs // 3600
            minutes = (self.elapsed_time_secs % 3600) // 60
            seconds = self.elapsed_time_secs % 60
            
            self.timer_label.configure(text=f"SESSION TIME: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
        self.after(1000, self.update_timer_loop)

    def change_ui_state(self, state, status_msg=None, status_color=None):
        """Updates visual state of LED indicators, status labels, and canvas visualizers."""
        self.assistant_state = state
        self.visualizer.set_state(state)
        self.indicator_led.set_state(state)
        
        if not status_msg:
            status_msg = f"SYSTEM STATUS: {state.upper()}"
        if not status_color:
            colors = {
                "Idle": "#2ECC71",
                "Listening": "#00D4FF",
                "Processing": "#FFD700",
                "Stopped": "#E74C3C"
            }
            status_color = colors.get(state, "#2ECC71")
            
        self.status_label.configure(text=status_msg, text_color=status_color)

    # ----------------- Button Callbacks (Phase 2 Operational Logic) -----------------

    def confirm_critical_command(self, matched_key):
        """Displays a secure Yes/No GUI messagebox for critical operations in CustomTkinter."""
        approved = messagebox.askyesno(
            "LOQ Security Alert",
            f"Warning: You are attempting to trigger a critical system action: '{matched_key}'.\n\nDo you want to authorize this operation?"
        )
        return approved

    def trigger_listening_cycle(self):
        """Runs a Speech-to-Speech loop asynchronously, fetching live dropdown voice configs."""
        if not self.session_active or self.assistant_state == "Stopped":
            return
            
        self.change_ui_state("Listening", "SYSTEM STATUS: LISTENING...", "#00D4FF")
        
        # Read the currently selected voice dynamically from the UI option menu
        voice_selection = self.voice_dropdown.get()
        
        # Parse selected engine configurations
        tts_method = "pyttsx3"
        voice_name = "Jessica"
        
        if "gTTS" in voice_selection:
            tts_method = "gtts"
        elif "ElevenLabs" in voice_selection:
            tts_method = "elevenlabs"
            if "Lily" in voice_selection:
                voice_name = "Lily"
            else:
                voice_name = "Brian"
        else:
            tts_method = "pyttsx3"
            voice_name = "Mark"
            
        # Dispatch to background daemon thread to keep CustomTkinter completely fluid
        self.assistant.run_cycle_async(
            callback=self.on_cycle_finished,
            confirmation_callback=self.confirm_critical_command,
            tts_method=tts_method,
            voice_name=voice_name
        )

    def on_cycle_finished(self, results):
        """Processes the Speech-to-Speech results back on the GUI main thread."""
        if not self.session_active or self.assistant_state == "Stopped":
            return
            
        user_text = results.get("user_text")
        response = results.get("response")
        command_executed = results.get("command_executed")
        
        # Fetch current assistant name dynamically from user setting
        current_name = self.name_entry.get().strip() or "LOQ"
        
        if user_text:
            self.append_log("User", f'"{user_text}"')
            
        if response:
            self.append_log(current_name, f'"{response}"')
            
        if command_executed:
            self.append_log("System", f"Command executed successfully: '{command_executed}'.")
            
        # Shift status indicator to gold (Processing/Done) and then smoothly back to Green (Ready/Idle)
        self.change_ui_state("Processing", "SYSTEM STATUS: DONE", "#FFD700")
        
        def reset_to_idle():
            if self.session_active and self.assistant_state != "Stopped":
                self.change_ui_state("Idle", "SYSTEM STATUS: READY", "#2ECC71")
                # Recursively schedule the next listening block after a short 1.2-second wait (continuous voice loop!)
                self.after(1200, self.trigger_listening_cycle)
                
        self.after(800, reset_to_idle)

    def start_action(self):
        """Activates the continuous, hands-free voice command execution loop."""
        if not self.session_active:
            self.session_active = True
            self.start_time = time.time()
            self.append_log("System", "Assistant session started.")
            
        # Clear stopped state and trigger first listening cycle
        self.change_ui_state("Listening", "SYSTEM STATUS: LISTENING...", "#00D4FF")
        self.append_log("System", "Microphone listening active...")
        
        # Style active start button
        self.start_btn.configure(fg_color="#00D4FF", text_color="#001F27")
        
        # Trigger the first cycle
        self.trigger_listening_cycle()

    def stop_action(self):
        """Instantly halts the active voice loop and cancels speech output."""
        self.session_active = False
        self.change_ui_state("Stopped", "SYSTEM STATUS: STOPPED", "#E74C3C")
        self.append_log("System", "Voice loop paused. Standby.")
        
        # Instantly interrupt any active audio stream
        self.assistant.stop()
        
        # Reset button styles
        self.start_btn.configure(fg_color="#00586B", text_color="#A8E8FF")

    def restart_action(self):
        """Resets console history, active session timers, and shuts down current loops."""
        self.session_active = False
        self.elapsed_time_secs = 0
        self.timer_label.configure(text="SESSION TIME: 00:00:00")
        
        # Clear textbox
        self.console_textbox.configure(state="normal")
        self.console_textbox.delete("1.0", "end")
        self.console_textbox.configure(state="disabled")
        
        # Interrupt voice
        self.assistant.stop()
        
        # Shift back to Ready
        self.change_ui_state("Idle", "SYSTEM STATUS: READY", "#2ECC71")
        self.append_log("System", "Logs cleared. Assistant reset to Standby Ready.")
        
        # Reset buttons styles
        self.start_btn.configure(fg_color="#00586B", text_color="#A8E8FF")


if __name__ == "__main__":
    app = PersonalAssistantApp()
    app.mainloop()
