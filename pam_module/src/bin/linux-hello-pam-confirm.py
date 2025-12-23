#!/usr/bin/env python3
"""
Linux Hello PAM Confirmation Dialog Helper
Displays GTK confirmation after successful facial recognition
"""

import sys
import argparse
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
    from PySide6.QtCore import Qt
except ImportError:
    print("Error: PySide6 not installed", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="PAM confirmation dialog")
    parser.add_argument("--username", required=True, help="Username to display")
    parser.add_argument("--pipe", required=True, help="FIFO path for response")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # Create dialog
    dialog = QDialog()
    dialog.setWindowTitle("Linux Hello - Face Recognition")
    dialog.setModal(True)
    dialog.resize(400, 200)

    layout = QVBoxLayout()

    # Title
    title = QLabel("Face Recognition Successful")
    title.setStyleSheet("font-weight: bold; font-size: 14px;")
    layout.addWidget(title)

    # Info
    info = QLabel(f"User '{args.username}' has been recognized.\n\nClick 'Confirm' to proceed.")
    info.setWordWrap(True)
    info.setAlignment(Qt.AlignCenter)
    layout.addWidget(info)

    # Buttons
    button_layout = QHBoxLayout()
    button_layout.addStretch()

    confirm_btn = QPushButton("Confirm")
    confirm_btn.setMinimumWidth(120)
    confirm_btn.clicked.connect(lambda: write_response("CONFIRM", args.pipe, dialog))
    button_layout.addWidget(confirm_btn)

    cancel_btn = QPushButton("Cancel")
    cancel_btn.setMinimumWidth(120)
    cancel_btn.clicked.connect(lambda: write_response("CANCEL", args.pipe, dialog))
    button_layout.addWidget(cancel_btn)

    button_layout.addStretch()
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    dialog.show()

    sys.exit(app.exec())


def write_response(response: str, pipe_path: str, dialog):
    """Write response to FIFO and close dialog"""
    try:
        with open(pipe_path, 'w') as f:
            f.write(response)
    except Exception as e:
        print(f"Error writing response: {e}", file=sys.stderr)
    finally:
        dialog.close()


if __name__ == "__main__":
    main()
