"""Standalone centered proposal window (PySide6).

Run as a separate process so the MCP server never blocks on the GUI:
    python proposal_window.py < proposal.json

Expects a JSON object on stdin with keys:
    proposal_title, proposal_reason, reference_shot_ID, proposed_command
Optional key:
    screen: index (int, 0 = primary) or exact screen name (str, e.g. "DP-1")
"""

import json
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QGuiApplication, QKeySequence, QShortcut
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPlainTextEdit,
                               QPushButton, QSplitter, QVBoxLayout, QWidget)

WIDTH, HEIGHT = 720, 520  # Default size; the window is freely resizable
MIN_WIDTH, MIN_HEIGHT = 420, 320


def pick_screen(selector) -> object:
    """Returns the requested QScreen, falling back to the primary screen."""
    screens = QGuiApplication.screens()
    if isinstance(selector, int) and 0 <= selector < len(screens):
        return screens[selector]
    if isinstance(selector, str):
        for screen in screens:
            if screen.name() == selector:
                return screen
    return QGuiApplication.primaryScreen()


def labelled(text: str, widget: QWidget) -> QWidget:
    """Wraps a widget with a bold heading so both panes can be resized by the splitter."""
    box = QWidget()
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 0, 0, 0)
    heading = QLabel(text)
    heading.setFont(QFont("Sans", 11, QFont.Weight.Bold))
    layout.addWidget(heading)
    layout.addWidget(widget)
    return box


def build(data: dict) -> QWidget:
    win = QWidget()
    win.setWindowTitle("GOLEM discharge proposal")
    win.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
    win.resize(WIDTH, HEIGHT)

    title = QLabel(data.get("proposal_title", ""))
    title.setWordWrap(True)
    title.setFont(QFont("Sans", 16, QFont.Weight.Bold))

    shot = QLabel(f"Reference shot: {data.get('reference_shot_ID', '')}")

    reason = QPlainTextEdit(data.get("proposal_reason", ""))
    reason.setReadOnly(True)
    reason.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

    command = QPlainTextEdit(data.get("proposed_command", ""))
    command.setReadOnly(True)
    command.setFont(QFont("Monospace", 10))
    command.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

    # Vertical splitter: drag the handle to give reasoning or command more room.
    splitter = QSplitter(Qt.Orientation.Vertical)
    splitter.addWidget(labelled("Reasoning", reason))
    splitter.addWidget(labelled("Proposed command", command))
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 1)

    close = QPushButton("Close")
    close.clicked.connect(win.close)
    buttons = QHBoxLayout()
    buttons.addStretch()
    buttons.addWidget(close)

    layout = QVBoxLayout(win)
    layout.addWidget(title)
    layout.addWidget(shot)
    layout.addWidget(splitter, stretch=1)
    layout.addLayout(buttons)

    QShortcut(QKeySequence(Qt.Key.Key_Escape), win, activated=win.close)
    return win


def center_on(win: QWidget, screen) -> None:
    """Moves the window so it is centered on the given screen's available area."""
    area = screen.availableGeometry()
    geo = win.frameGeometry()
    geo.moveCenter(area.center())
    win.move(geo.topLeft())


def main() -> int:
    data = json.load(sys.stdin)
    app = QApplication(sys.argv[:1])
    win = build(data)
    screen = pick_screen(data.get("screen", 0))
    win.move(screen.availableGeometry().topLeft())  # Place on the target screen before sizing
    win.show()
    center_on(win, screen)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
