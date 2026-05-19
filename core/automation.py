import comtypes
from pycaw.pycaw import AudioUtilities
import screen_brightness_control as sbc
from utils.logger import logging as log

class SystemController:
    """
    Handles native PC system controls (Volume, Mute, Brightness).
    Zero external dependencies required (e.g. nircmd).
    """
    
    @staticmethod
    def get_volume_interface():
        """Helper to fetch the IAudioEndpointVolume interface."""
        try:
            comtypes.CoInitialize()
            devices = AudioUtilities.GetSpeakers()
            return devices.EndpointVolume
        except Exception as e:
            log.error(f"Failed to get audio endpoint: {e}")
            return None

    @staticmethod
    def set_volume(percentage):
        """Sets master volume to a specific percentage (0-100)."""
        volume = SystemController.get_volume_interface()
        if not volume:
            return "Failed to access audio device."
            
        try:
            val = max(0.0, min(1.0, float(percentage) / 100.0))
            volume.SetMasterVolumeLevelScalar(val, None)
            log.info(f"Set volume to {percentage}%")
            return f"System volume set to {int(percentage)} percent."
        except Exception as e:
            log.error(f"Failed to set volume: {e}")
            return f"Error setting volume: {e}"

    @staticmethod
    def change_volume(delta):
        """Increases or decreases volume by delta percentage."""
        volume = SystemController.get_volume_interface()
        if not volume:
            return "Failed to access audio device."
            
        try:
            current_vol = volume.GetMasterVolumeLevelScalar()
            new_vol = max(0.0, min(1.0, current_vol + (float(delta) / 100.0)))
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            log.info(f"Changed volume by {delta}%. New level: {new_vol*100:.0f}%")
            return f"System volume is now {int(new_vol * 100)} percent."
        except Exception as e:
            log.error(f"Failed to change volume: {e}")
            return f"Error changing volume: {e}"

    @staticmethod
    def set_mute(is_muted):
        """Mutes or unmutes the master volume."""
        volume = SystemController.get_volume_interface()
        if not volume:
            return "Failed to access audio device."
            
        try:
            volume.SetMute(1 if is_muted else 0, None)
            state_str = "Muted" if is_muted else "Unmuted"
            log.info(f"{state_str} system volume.")
            return f"System volume {state_str.lower()}."
        except Exception as e:
            log.error(f"Failed to set mute state: {e}")
            return f"Error changing mute state: {e}"

    @staticmethod
    def set_brightness(percentage):
        """Sets display brightness to a specific percentage (0-100)."""
        try:
            val = max(0, min(100, int(percentage)))
            sbc.set_brightness(val)
            log.info(f"Set display brightness to {val}%")
            return f"Display brightness set to {val} percent."
        except Exception as e:
            log.error(f"Failed to set brightness: {e}")
            return f"Error setting brightness: {e}"

    @staticmethod
    def change_brightness(delta):
        """Increases or decreases display brightness by delta percentage."""
        try:
            current_brightness_list = sbc.get_brightness()
            if not current_brightness_list:
                return "Could not determine current brightness."
                
            current_brightness = current_brightness_list[0]
            new_brightness = max(0, min(100, current_brightness + int(delta)))
            sbc.set_brightness(new_brightness)
            log.info(f"Changed brightness by {delta}%. New level: {new_brightness}%")
            return f"Display brightness is now {new_brightness} percent."
        except Exception as e:
            log.error(f"Failed to change brightness: {e}")
            return f"Error changing brightness: {e}"

class DesktopAutomation:
    """
    Handles high-fidelity desktop navigation and interactions
    using PyAutoGUI (scrolling, clicking, hotkeys, screenshots).
    """
    
    @staticmethod
    def scroll(direction, amount=500):
        """Scrolls the active window."""
        import pyautogui
        try:
            if direction.lower() == "down":
                pyautogui.scroll(-amount)
                log.info("Scrolled active window down.")
                return "Scrolled down."
            elif direction.lower() == "up":
                pyautogui.scroll(amount)
                log.info("Scrolled active window up.")
                return "Scrolled up."
            return f"Invalid scroll direction: {direction}"
        except Exception as e:
            log.error(f"Failed to scroll: {e}")
            return f"Failed to scroll: {e}"

    @staticmethod
    def trigger_hotkey(*keys):
        """Sends key combinations (e.g. 'ctrl', 't')."""
        import pyautogui
        try:
            pyautogui.hotkey(*keys)
            log.info(f"Triggered hotkey shortcut: {keys}")
            return f"Triggered {', '.join(keys)}."
        except Exception as e:
            log.error(f"Hotkey execution failed: {e}")
            return f"Hotkey execution failed: {e}"

    @staticmethod
    def press_key(key):
        """Presses a single key."""
        import pyautogui
        try:
            pyautogui.press(key)
            log.info(f"Pressed key: {key}")
            return f"Pressed {key}."
        except Exception as e:
            log.error(f"Key press failed: {e}")
            return f"Key press failed: {e}"

    @staticmethod
    def take_screenshot(filename=None):
        """Takes a screenshot and saves it to the specified OneDrive folder."""
        import pyautogui
        import os
        from datetime import datetime
        
        try:
            screenshot_dir = r"C:\Users\chill\OneDrive\Pictures\Screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"LOQ_Screenshot_{timestamp}.png"
                
            filepath = os.path.join(screenshot_dir, filename)
            pyautogui.screenshot(filepath)
            log.info(f"Screenshot saved silently to: {filepath}")
            return "Screenshot saved successfully."
        except Exception as e:
            log.error(f"Screenshot failed: {e}")
            return f"Screenshot failed: {e}"

