#!/usr/bin/env python3
"""
Linux Hello PAM Confirmation Dialog Helper
Displays confirmation dialog after successful facial recognition.
Supports KDE (kdialog), GNOME/D-Bus notifications, and fallback PySide6 GUI.
"""

import sys
import argparse
import os
import subprocess
import locale
import gettext
from pathlib import Path

# Setup i18n
TEXTDOMAIN = "linux-hello"
LOCALEDIR = "/usr/share/locale"

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

try:
    translation = gettext.translation(TEXTDOMAIN, localedir=LOCALEDIR, fallback=True)
    _ = translation.gettext
except Exception:
    _ = lambda x: x

# Try D-Bus notifications (works on KDE, GNOME, etc.)
try:
    import dbus
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False

try:
    from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
    from PySide6.QtCore import Qt, QTimer
except ImportError:
    print("Error: PySide6 not installed", file=sys.stderr)
    sys.exit(1)


def detect_desktop_env():
    """Detect desktop environment (KDE, GNOME, etc.)"""
    desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    if 'kde' in desktop or 'plasma' in desktop:
        return 'kde'
    elif 'gnome' in desktop:
        return 'gnome'
    elif 'xfce' in desktop:
        return 'xfce'
    return 'generic'


def send_dbus_notification(title: str, message: str, urgency: int = 1):
    """Send D-Bus desktop notification (works on KDE, GNOME, etc.)
    urgency: 0=low, 1=normal, 2=critical
    """
    if not DBUS_AVAILABLE:
        return False
    
    try:
        bus = dbus.SessionBus()
        notify_obj = bus.get_object('org.freedesktop.Notifications',
                                   '/org/freedesktop/Notifications')
        notify_iface = dbus.Interface(notify_obj, 'org.freedesktop.Notifications')
        
        # Call Notify method
        notify_iface.Notify(
            'linux-hello',              # app_name
            0,                          # replaces_id
            'face-recognition',         # app_icon
            title,                      # summary
            message,                    # body
            [],                         # actions
            {'urgency': dbus.Byte(urgency)},  # hints
            5000                        # expire_timeout (ms)
        )
        return True
    except Exception as e:
        print(f"D-Bus notification failed: {e}", file=sys.stderr)
        return False


def use_kdialog(username: str, pipe_path: str) -> bool:
    """Use kdialog for KDE native dialog (if available)"""
    try:
        # First show "processing" notification
        subprocess.run([
            'kdialog', '--passivepopup',
            _("Facial recognition successful. Confirm to proceed?"),
            '3'
        ], timeout=3, check=False)
        
        # Then show confirmation dialog
        result = subprocess.run([
            'kdialog', '--yesno',
            _("User \"{username}\" recognized.\n\nConfirm to authenticate?").format(username=username)
        ], timeout=30)
        
        response = "CONFIRM" if result.returncode == 0 else "CANCEL"
        with open(pipe_path, 'w') as f:
            f.write(response)
        return True
    except Exception as e:
        print(f"kdialog failed: {e}", file=sys.stderr)
        return False


def use_zenity(username: str, pipe_path: str) -> bool:
    """Use zenity for GNOME/generic dialog (if available)"""
    try:
        result = subprocess.run([
            'zenity', '--question',
            f'--title={_("Linux Hello - Face Recognition")}',
            f'--text={_("User \\"{username}\\" recognized.\\n\\nConfirm to authenticate?").format(username=username)}',
            f'--ok-label={_("Confirm")}',
            f'--cancel-label={_("Cancel")}'
        ], timeout=30)
        
        response = "CONFIRM" if result.returncode == 0 else "CANCEL"
        with open(pipe_path, 'w') as f:
            f.write(response)
        return True
    except Exception as e:
        print(f"zenity failed: {e}", file=sys.stderr)
        return False


def use_pyside6_gui(username: str, pipe_path: str):
    """Fallback: Use PySide6 GUI with processing notification"""
    app = QApplication(sys.argv)
    
    # Send notification first (in background)
    send_dbus_notification(
        _("Linux Hello"),
        _("Face recognition in progress for {username}...").format(username=username)
    )
    
    # Create confirmation dialog
    dialog = QDialog()
    dialog.setWindowTitle(_("Linux Hello - Face Recognition"))
    dialog.setModal(True)
    dialog.resize(450, 220)
    
    layout = QVBoxLayout()
    
    # Title
    title = QLabel(_("Face Recognition Successful ✓"))
    title.setStyleSheet("font-weight: bold; font-size: 16px; color: #27ae60;")
    layout.addWidget(title)
    
    # Info with username
    info = QLabel(_("User '{username}' has been recognized.\n\nWould you like to proceed with authentication?").format(username=username))
    info.setWordWrap(True)
    info.setAlignment(Qt.AlignCenter)
    layout.addWidget(info)
    
    layout.addStretch()
    
    # Buttons
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    
    confirm_btn = QPushButton(_("✓ Confirm"))
    confirm_btn.setMinimumWidth(130)
    confirm_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
    confirm_btn.clicked.connect(lambda: write_response("CONFIRM", pipe_path, dialog))
    button_layout.addWidget(confirm_btn)
    
    cancel_btn = QPushButton(_("✕ Cancel"))
    cancel_btn.setMinimumWidth(130)
    cancel_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 8px;")
    cancel_btn.clicked.connect(lambda: write_response("CANCEL", pipe_path, dialog))
    button_layout.addWidget(cancel_btn)
    
    button_layout.addStretch()
    layout.addLayout(button_layout)
    
    dialog.setLayout(layout)
    dialog.show()
    
    # Auto-cancel after 60 seconds if no response
    def timeout_handler():
        send_dbus_notification(_("Linux Hello"), _("Confirmation timed out - authentication cancelled"))
        write_response("CANCEL", pipe_path, dialog)
    
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(timeout_handler)
    timer.start(60000)  # 60 seconds
    
    sys.exit(app.exec())


def write_response(response: str, pipe_path: str, dialog=None):
    """Write response to FIFO and close dialog"""
    try:
        with open(pipe_path, 'w') as f:
            f.write(response)
    except Exception as e:
        print(f"Error writing response: {e}", file=sys.stderr)
    finally:
        if dialog:
            dialog.close()


def main():
    parser = argparse.ArgumentParser(description="PAM confirmation dialog")
    parser.add_argument("--username", required=True, help="Username to display")
    parser.add_argument("--pipe", required=True, help="FIFO path for response")
    parser.add_argument("--no-gui", action="store_true", help="Headless mode (use CLI only)")
    args = parser.parse_args()
    
    desktop = detect_desktop_env()
    
    # Try platform-specific dialogs first
    if not args.no_gui:
        # Try KDE (kdialog) on KDE desktop
        if desktop == 'kde':
            if subprocess.run(['which', 'kdialog'], capture_output=True).returncode == 0:
                if use_kdialog(args.username, args.pipe):
                    return
        
        # Try Zenity on GNOME/generic
        if subprocess.run(['which', 'zenity'], capture_output=True).returncode == 0:
            if use_zenity(args.username, args.pipe):
                return
    
    # Fallback to PySide6 GUI
    use_pyside6_gui(args.username, args.pipe)


if __name__ == "__main__":
    main()
