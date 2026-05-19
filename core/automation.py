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
