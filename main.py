"""
Personal Assistant Entry Point (LOQ).
Launches the custom high-fidelity CustomTkinter graphical user interface.
"""

import sys
import os

# Add project root to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ui.app import PersonalAssistantApp

def main():
    print("Launching LOQ Personal Assistant GUI (Phase 1)...")
    app = PersonalAssistantApp()
    app.mainloop()

if __name__ == "__main__":
    main()
