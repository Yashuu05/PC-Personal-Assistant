---
name: Neon Sentinel
colors:
  surface: '#0e1417'
  surface-dim: '#0e1417'
  surface-bright: '#333a3d'
  surface-container-lowest: '#080f12'
  surface-container-low: '#161d1f'
  surface-container: '#1a2123'
  surface-container-high: '#242b2e'
  surface-container-highest: '#2f3639'
  on-surface: '#dde3e7'
  on-surface-variant: '#bbc9cf'
  inverse-surface: '#dde3e7'
  inverse-on-surface: '#2b3134'
  outline: '#859398'
  outline-variant: '#3c494e'
  surface-tint: '#3cd7ff'
  primary: '#a8e8ff'
  on-primary: '#003642'
  primary-container: '#00d4ff'
  on-primary-container: '#00586b'
  inverse-primary: '#00677e'
  secondary: '#fff9ef'
  on-secondary: '#3a3000'
  secondary-container: '#ffdb3c'
  on-secondary-container: '#725f00'
  tertiary: '#ffd9a1'
  on-tertiary: '#432c00'
  tertiary-container: '#feb528'
  on-tertiary-container: '#6c4900'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#b4ebff'
  primary-fixed-dim: '#3cd7ff'
  on-primary-fixed: '#001f27'
  on-primary-fixed-variant: '#004e5f'
  secondary-fixed: '#ffe16d'
  secondary-fixed-dim: '#e9c400'
  on-secondary-fixed: '#221b00'
  on-secondary-fixed-variant: '#544600'
  tertiary-fixed: '#ffdeae'
  tertiary-fixed-dim: '#ffba3d'
  on-tertiary-fixed: '#281900'
  on-tertiary-fixed-variant: '#604100'
  background: '#0e1417'
  on-background: '#dde3e7'
  surface-variant: '#2f3639'
  background-matte: '#1A1A1B'
  text-soft-white: '#E1E1E1'
  status-success: '#2ECC71'
  status-error: '#E74C3C'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-padding: 24px
  element-gap: 16px
  sidebar-width: 280px
  header-height: 80px
  footer-height: 64px
---

# UI Design Specification: PC Personal Assistant (LOQ)

## 1. Overview
The user interface for the Personal Assistant is designed to provide a "premium," futuristic experience reminiscent of advanced AI systems (like Jarvis). It leverages **CustomTkinter** to create a modern, sleek desktop application that prioritizes voice interaction while offering robust manual controls.

---

## 2. Visual Theme & Aesthetics
- **Design Philosophy**: Minimalist, high-tech, and responsive.
- **Color Palette**:
    - **Primary Background**: `#1A1A1B` (Deep Matte Charcoal)
    - **Accent Color (Primary)**: `#00D4FF` (Neon Cyan) - Used for buttons, borders, and active states.
    - **Accent Color (Secondary)**: `#FFD700` (Gold) - Used for alerts or special status indicators.
    - **Text Color**: `#E1E1E1` (Soft White) for readability.
    - **Success/Running**: `#2ECC71` (Emerald Green).
    - **Stop/Warning**: `#E74C3C` (Alizarin Crimson).
- **Typography**: 
    - Font: **Inter** or **Roboto** (Clean, sans-serif).
    - Styles: Bold headers for status, monospaced for history timestamps.

---

## 3. UI Structure & Layout

### A. Header Section
- **Assistant Name**: Displays the current name of the assistant (e.g., "LOQ").
- **Status Indicator**: A glowing ring or LED-style icon that changes color based on state:
    - **Blue Pulse**: Listening.
    - **Green Static**: Idle/Ready.
    - **Yellow Spin**: Processing/Thinking.
    - **Red Static**: Stopped.

### B. Main Central Area (Visualizer & History)
- **AI Visualizer (Top Half)**:
    - Space reserved for a robotic face animation or dynamic sound waves that vibrate when the assistant speaks.
- **Command History (Bottom Half)**:
    - A scrollable list showing:
        - `[14:20:05] User: "Open Chrome"`
        - `[14:20:06] LOQ: "Opening Google Chrome..."`
    - History persists during the session but can be cleared via "Restart."

### C. Sidebar (Configuration & Settings)
- **Personalization**:
    - Text box to change the assistant's name.
    - Dropdown menu to select voices (Mark, Jessica, Brian, Lily) via ElevenLabs API.
- **System Info**:
    - Real-time display of CPU, RAM, and Battery usage.

### D. Footer Section (Controls)
- **Action Buttons**:
    - **Start Button**: Icon-based (Play), activates the listening loop.
    - **Stop Button**: Icon-based (Pause/Stop), halts active listening and timers.
    - **Restart Button**: Icon-based (Refresh), resets history and application state.
- **Session Timer**: Displays `HH:MM:SS` elapsed since the current session started.

---

## 4. Interaction & Functionality

### Voice Interaction
- **Wake Word**: The UI should visually "ping" or flash when the wake word (e.g., "LOQ") is detected.
- **Feedback**: Text-to-speech responses are mirrored in the Command History UI.

### Manual Controls
- **Button Hover Effects**: Buttons glow or slightly enlarge when hovered to provide tactile feedback.
- **Real-time Updates**: The history list auto-scrolls to the bottom when new commands are executed.

### Background Mode
- The app can be minimized to the **System Tray**.
- Right-clicking the tray icon provides quick options: "Wake Up," "Mute," "Exit."

---

## 5. UI Elements Detail (CustomTkinter Components)
| Element | CTk Component | Description |
| :--- | :--- | :--- |
| **Main Window** | `CTk` | 800x600 resolution (resizable). |
| **Buttons** | `CTkButton` | Rounded corners (corner_radius=10), neon borders. |
| **History Log** | `CTkTextbox` | Read-only, auto-scroll enabled. |
| **Voice Selector** | `CTkOptionMenu` | Styled to match the dark theme. |
| **Name Input** | `CTkEntry` | Placeholder text "Enter Name...". |
| **Status Bar** | `CTkFrame` | Located at the bottom for timer and battery info. |
