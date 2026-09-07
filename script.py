import re
import sys
import json
import math
import random
import shutil
import time

from pathlib import Path
from datetime import datetime

from PySide6 import QtCore, QtGui, QtWidgets


# ============================================================
# CATALYST // FORERUNNER HUD
# ============================================================

APP_NAME = "CATALYST"
VERSION = "6.0"

BASE_DIR = Path(__file__).resolve().parent
TOOLS_DIR = BASE_DIR / "tools"
CONFIG_FILE = BASE_DIR / "tools.json"
LOG_FILE = BASE_DIR / "catalyst.log"

TOOLS_DIR.mkdir(exist_ok=True)


# ============================================================
# REAL LOCAL TOOLS
# ============================================================

DEFAULT_DATABASE = {

    "NMAP": {
        "name": "NMAP",
        "description": "Network discovery and security auditing",
        "command": "nmap",
        "category": "NETWORK"
    },

    "WIRESHARK": {
        "name": "WIRESHARK",
        "description": "Network protocol analyzer",
        "command": "wireshark",
        "category": "NETWORK"
    },

    "CURL": {
        "name": "CURL",
        "description": "HTTP and network transfer utility",
        "command": "curl",
        "category": "UTILITY"
    },

    "NSLOOKUP": {
        "name": "NSLOOKUP",
        "description": "DNS query and diagnostic utility",
        "command": "nslookup",
        "category": "DNS"
    },

    "TRACERT": {
        "name": "TRACERT",
        "description": "Network route tracing utility",
        "command": "tracert",
        "category": "NETWORK"
    },

    "NETSTAT": {
        "name": "NETSTAT",
        "description": "Active network connection viewer",
        "command": "netstat",
        "category": "NETWORK"
    },

    "PING": {
        "name": "PING",
        "description": "Network connectivity diagnostic",
        "command": "ping",
        "category": "NETWORK"
    },

    "IPCONFIG": {
        "name": "IPCONFIG",
        "description": "Local network configuration viewer",
        "command": "ipconfig",
        "category": "SYSTEM"
    },

    "TASKLIST": {
        "name": "TASKLIST",
        "description": "Local process enumeration utility",
        "command": "tasklist",
        "category": "SYSTEM"
    }
}


# ============================================================
# DATABASE
# ============================================================

def save_database(database):

    try:

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                database,
                file,
                indent=4
            )

    except Exception as error:

        print(
            "Database error:",
            error
        )


def load_database():

    if not CONFIG_FILE.exists():

        save_database(
            DEFAULT_DATABASE
        )

        return dict(
            DEFAULT_DATABASE
        )

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, dict):

            return data

    except Exception:
        pass

    save_database(
        DEFAULT_DATABASE
    )

    return dict(
        DEFAULT_DATABASE
    )


# ============================================================
# LOGGING
# ============================================================

def write_log(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    try:

        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"[{timestamp}] {message}\n"
            )

    except Exception:
        pass


# ============================================================
# EXECUTABLE DETECTION
# ============================================================

def find_executable(command):

    if not command:
        return None

    command = command.strip()

    found = shutil.which(
        command
    )

    if found:
        return found

    candidates = [

        TOOLS_DIR / command,

        TOOLS_DIR / f"{command}.exe",

        TOOLS_DIR / f"{command}.bat",

        TOOLS_DIR / f"{command}.cmd"

    ]

    for path in candidates:

        if path.exists():

            return str(path)

    return None


def discover_tool_executables():
    """Return every .exe directly inside the CATALYST tools folder."""
    if not TOOLS_DIR.exists():
        return []

    return sorted(
        [path for path in TOOLS_DIR.glob("*.exe") if path.is_file()],
        key=lambda p: p.name.lower()
    )


def tool_already_registered(executable, database):
    """Match a local executable against saved command/path entries."""
    try:
        target = Path(executable).resolve()
    except Exception:
        target = Path(executable)

    for tool in database.values():
        command = str(tool.get("command", "")).strip()
        if not command:
            continue

        candidate = find_executable(command)
        if candidate:
            try:
                if Path(candidate).resolve() == target:
                    return True
            except Exception:
                pass

        if Path(command).name.lower() == target.name.lower():
            return True

    return False


# ============================================================
# HOLO BACKGROUND
# ============================================================

class HoloBackground(QtWidgets.QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.phase = 0

        self.particles = []

        for _ in range(50):

            self.particles.append({

                "x": random.random(),

                "y": random.random(),

                "speed": random.uniform(
                    0.0002,
                    0.0008
                ),

                "size": random.choice(
                    [1, 1, 1, 2]
                )

            })

        self.timer = QtCore.QTimer(
            self
        )

        self.timer.timeout.connect(
            self.animate
        )

        self.timer.start(
            35
        )

    def animate(self):

        self.phase += 1

        for particle in self.particles:

            particle["y"] -= (
                particle["speed"]
            )

            if particle["y"] < 0:

                particle["y"] = 1

        self.update()

    def paintEvent(
        self,
        event
    ):

        painter = QtGui.QPainter(
            self
        )

        painter.setRenderHint(
            QtGui.QPainter.Antialiasing
        )

        width = self.width()
        height = self.height()

        painter.fillRect(
            self.rect(),
            QtGui.QColor(
                "#02070b"
            )
        )

        # ----------------------------------------------------
        # GRID
        # ----------------------------------------------------

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#071923"
                )
            )
        )

        spacing = 48

        offset = (
            self.phase // 3
        ) % spacing

        for x in range(
            -spacing,
            width + spacing,
            spacing
        ):

            painter.drawLine(
                x + offset,
                0,
                x + offset,
                height
            )

        for y in range(
            -spacing,
            height + spacing,
            spacing
        ):

            painter.drawLine(
                0,
                y + offset,
                width,
                y + offset
            )

        # ----------------------------------------------------
        # HORIZON
        # ----------------------------------------------------

        horizon = int(
            height * 0.72
        )

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#10343f"
                )
            )
        )

        painter.drawLine(
            0,
            horizon,
            width,
            horizon
        )

        # ----------------------------------------------------
        # PARTICLES
        # ----------------------------------------------------

        painter.setPen(
            QtCore.Qt.NoPen
        )

        painter.setBrush(
            QtGui.QColor(
                "#287f90"
            )
        )

        for particle in self.particles:

            x = int(
                particle["x"] * width
            )

            y = int(
                particle["y"] * height
            )

            size = particle["size"]

            painter.drawEllipse(
                x,
                y,
                size,
                size
            )

        # ----------------------------------------------------
        # SCANLINE
        # ----------------------------------------------------

        scan_y = (
            self.phase * 2
        ) % max(
            height,
            1
        )

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#0d3e4b"
                )
            )

        )

        painter.drawLine(
            0,
            scan_y,
            width,
            scan_y
        )

        # ----------------------------------------------------
        # CORNER MARKERS
        # ----------------------------------------------------

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#176070"
                ),
                1
            )
        )

        corner = 35
        margin = 18

        painter.drawLine(
            margin,
            margin,
            margin + corner,
            margin
        )

        painter.drawLine(
            margin,
            margin,
            margin,
            margin + corner
        )

        painter.drawLine(
            width - margin,
            margin,
            width - margin - corner,
            margin
        )

        painter.drawLine(
            width - margin,
            margin,
            width - margin,
            margin + corner
        )

        painter.drawLine(
            margin,
            height - margin,
            margin + corner,
            height - margin
        )

        painter.drawLine(
            margin,
            height - margin,
            margin,
            height - margin - corner
        )

        painter.drawLine(
            width - margin,
            height - margin,
            width - margin - corner,
            height - margin
        )

        painter.drawLine(
            width - margin,
            height - margin,
            width - margin,
            height - margin - corner
        )


# ============================================================
# HUD LINE
# ============================================================

class HudLine(QtWidgets.QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setFixedHeight(
            1
        )

    def paintEvent(
        self,
        event
    ):

        painter = QtGui.QPainter(
            self
        )

        painter.fillRect(
            self.rect(),
            QtGui.QColor(
                "#124755"
            )
        )


# ============================================================
# CORE DISPLAY
# ============================================================

class CoreWidget(QtWidgets.QWidget):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.angle = 0

        self.setFixedSize(
            145,
            145
        )

        self.timer = QtCore.QTimer(
            self
        )

        self.timer.timeout.connect(
            self.animate
        )

        self.timer.start(
            35
        )

    def animate(self):

        self.angle += 1

        if self.angle >= 360:

            self.angle = 0

        self.update()

    def paintEvent(
        self,
        event
    ):

        painter = QtGui.QPainter(
            self
        )

        painter.setRenderHint(
            QtGui.QPainter.Antialiasing
        )

        center = QtCore.QPointF(
            self.width() / 2,
            self.height() / 2
        )

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#123d49"
                ),
                1
            )
        )

        painter.drawEllipse(
            center,
            57,
            57
        )

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#1c6170"
                )
            )
        )

        painter.drawEllipse(
            center,
            39,
            39
        )

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#4ae5f2"
                ),
                2
            )
        )

        rect = QtCore.QRectF(
            18,
            18,
            109,
            109
        )

        painter.drawArc(
            rect,
            self.angle * 16,
            85 * 16
        )

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#71eff8"
                )
            )
        )

        painter.setBrush(
            QtGui.QBrush(
                QtGui.QColor(
                    "#0b3039"
                )
            )
        )

        diamond = QtGui.QPolygonF([

            QtCore.QPointF(
                center.x(),
                center.y() - 14
            ),

            QtCore.QPointF(
                center.x() + 14,
                center.y()
            ),

            QtCore.QPointF(
                center.x(),
                center.y() + 14
            ),

            QtCore.QPointF(
                center.x() - 14,
                center.y()
            )

        ])

        painter.drawPolygon(
            diamond
        )

        painter.setBrush(
            QtGui.QColor(
                "#8ef6ff"
            )
        )

        painter.setPen(
            QtCore.Qt.NoPen
        )

        painter.drawEllipse(
            center,
            4,
            4
        )

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#1b5664"
                )
            )
        )

        for i in range(8):

            angle = math.radians(
                i * 45
            )

            x1 = (
                center.x()
                + math.cos(angle)
                * 62
            )

            y1 = (
                center.y()
                + math.sin(angle)
                * 62
            )

            x2 = (
                center.x()
                + math.cos(angle)
                * 68
            )

            y2 = (
                center.y()
                + math.sin(angle)
                * 68
            )

            painter.drawLine(
                QtCore.QPointF(
                    x1,
                    y1
                ),
                QtCore.QPointF(
                    x2,
                    y2
                )
            )


# ============================================================
# TOOL ENTRY
# ============================================================

class ToolEntry(
    QtWidgets.QWidget
):

    launchRequested = QtCore.Signal(
        str
    )

    def __init__(
        self,
        key,
        tool,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.key = key
        self.tool = tool
        self.hovered = False

        self.setMinimumHeight(
            112
        )

        self.setMaximumHeight(
            125
        )

        layout = QtWidgets.QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            12,
            10,
            12,
            10
        )

        layout.setSpacing(
            10
        )

        marker = QtWidgets.QLabel(
            ">"
        )

        marker.setObjectName(
            "ToolArrow"
        )

        marker.setFixedWidth(
            15
        )

        layout.addWidget(
            marker
        )

        name_column = QtWidgets.QVBoxLayout()

        name_column.setSpacing(
            5
        )

        name = QtWidgets.QLabel(
            tool.get(
                "name",
                key
            )
        )

        name.setObjectName(
            "ToolName"
        )

        description = QtWidgets.QLabel(
            tool.get(
                "description",
                "No description"
            )
        )

        description.setObjectName(
            "ToolDescription"
        )

        description.setWordWrap(
            True
        )

        name_column.addWidget(
            name
        )

        name_column.addWidget(
            description
        )

        name_column.addStretch()

        layout.addLayout(
            name_column,
            1
        )

        right = QtWidgets.QVBoxLayout()

        right.setSpacing(
            6
        )

        category = QtWidgets.QLabel(
            tool.get(
                "category",
                "UTILITY"
            )
        )

        category.setObjectName(
            "ToolCategory"
        )

        right.addWidget(
            category,
            alignment=QtCore.Qt.AlignRight
        )

        executable = find_executable(
            tool.get(
                "command",
                ""
            )
        )

        self.status = QtWidgets.QLabel()

        if executable:

            self.status.setText(
                "● READY"
            )

            self.status.setObjectName(
                "Online"
            )

        else:

            self.status.setText(
                "● MISSING"
            )

            self.status.setObjectName(
                "Offline"
            )

        right.addWidget(
            self.status,
            alignment=QtCore.Qt.AlignRight
        )

        right.addStretch()

        button = QtWidgets.QPushButton(
            "OPEN"
        )

        button.setObjectName(
            "OpenButton"
        )

        button.setCursor(
            QtGui.QCursor(
                QtCore.Qt.PointingHandCursor
            )
        )

        button.clicked.connect(
            lambda:
            self.launchRequested.emit(
                self.key
            )
        )

        right.addWidget(
            button,
            alignment=QtCore.Qt.AlignRight
        )

        layout.addLayout(
            right
        )

    def enterEvent(
        self,
        event
    ):

        self.hovered = True

        self.update()

        super().enterEvent(
            event
        )

    def leaveEvent(
        self,
        event
    ):

        self.hovered = False

        self.update()

        super().leaveEvent(
            event
        )

    def paintEvent(
        self,
        event
    ):

        painter = QtGui.QPainter(
            self
        )

        painter.setRenderHint(
            QtGui.QPainter.Antialiasing
        )

        rect = self.rect().adjusted(
            1,
            1,
            -1,
            -1
        )

        if self.hovered:

            border = QtGui.QColor(
                "#3dd9e9"
            )

            background = QtGui.QColor(
                9,
                43,
                51,
                150
            )

        else:

            border = QtGui.QColor(
                "#174956"
            )

            background = QtGui.QColor(
                3,
                15,
                20,
                125
            )

        painter.setBrush(
            background
        )

        painter.setPen(
            QtGui.QPen(
                border,
                1
            )
        )

        painter.drawRect(
            rect
        )

        painter.setPen(
            QtGui.QPen(
                QtGui.QColor(
                    "#39cbd9"
                ),
                2
            )
        )

        length = 8

        painter.drawLine(
            rect.left(),
            rect.top(),
            rect.left() + length,
            rect.top()
        )

        painter.drawLine(
            rect.left(),
            rect.top(),
            rect.left(),
            rect.top() + length
        )

        painter.drawLine(
            rect.right(),
            rect.bottom(),
            rect.right() - length,
            rect.bottom()
        )

        painter.drawLine(
            rect.right(),
            rect.bottom(),
            rect.right(),
            rect.bottom() - length
        )


# ============================================================
# FIELD HELPERS
# ============================================================

def make_line_edit(
    placeholder,
    default=""
):

    widget = QtWidgets.QLineEdit()

    widget.setPlaceholderText(
        placeholder
    )

    if default:

        widget.setText(
            default
        )

    return widget


def make_spinbox(
    minimum,
    maximum,
    value
):

    widget = QtWidgets.QSpinBox()

    widget.setRange(
        minimum,
        maximum
    )

    widget.setValue(
        value
    )

    return widget


def add_form_row(
    layout,
    label_text,
    widget
):

    row = QtWidgets.QHBoxLayout()

    label = QtWidgets.QLabel(
        label_text
    )

    label.setObjectName(
        "OptionLabel"
    )

    label.setFixedWidth(
        125
    )

    row.addWidget(
        label
    )

    row.addWidget(
        widget,
        1
    )

    layout.addLayout(
        row
    )


# ============================================================
# BASE OPTION DIALOG
# ============================================================

class ToolOptionsDialog(
    QtWidgets.QDialog
):

    def __init__(
        self,
        tool_name,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.tool_name = tool_name

        self.setWindowTitle(
            f"CATALYST // {tool_name} OPTIONS"
        )

        self.setMinimumWidth(
            540
        )

        self.setModal(
            True
        )

        self.main_layout = QtWidgets.QVBoxLayout(
            self
        )

        self.main_layout.setContentsMargins(
            24,
            22,
            24,
            22
        )

        self.main_layout.setSpacing(
            12
        )

        title = QtWidgets.QLabel(
            f"{tool_name} // LAUNCH CONFIGURATION"
        )

        title.setObjectName(
            "DialogTitle"
        )

        self.main_layout.addWidget(
            title
        )

        subtitle = QtWidgets.QLabel(
            "CONFIGURE PARAMETERS BEFORE LOCAL EXECUTION"
        )

        subtitle.setObjectName(
            "DialogSubtitle"
        )

        self.main_layout.addWidget(
            subtitle
        )

        self.main_layout.addWidget(
            HudLine()
        )

        self.options_layout = QtWidgets.QVBoxLayout()

        self.options_layout.setSpacing(
            9
        )

        self.main_layout.addLayout(
            self.options_layout
        )

        self.preview = QtWidgets.QLineEdit()

        self.preview.setReadOnly(
            True
        )

        self.preview.setObjectName(
            "CommandPreview"
        )

        self.main_layout.addWidget(
            QtWidgets.QLabel(
                "COMMAND PREVIEW"
            ),
        )

        self.main_layout.addWidget(
            self.preview
        )

        buttons = QtWidgets.QHBoxLayout()

        cancel = QtWidgets.QPushButton(
            "CANCEL"
        )

        launch = QtWidgets.QPushButton(
            "LAUNCH"
        )

        cancel.setObjectName(
            "DialogButton"
        )

        launch.setObjectName(
            "LaunchButton"
        )

        cancel.clicked.connect(
            self.reject
        )

        launch.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            cancel
        )

        buttons.addStretch()

        buttons.addWidget(
            launch
        )

        self.main_layout.addLayout(
            buttons
        )

        self.launch_button = launch

    def update_preview(
        self
    ):

        self.preview.setText(
            self.command_preview()
        )

    def command_preview(
        self
    ):

        return self.tool_name

    def get_arguments(
        self
    ):

        return []


# ============================================================
# NMAP OPTIONS
# ============================================================

class NmapOptionsDialog(
    ToolOptionsDialog
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            "NMAP",
            parent
        )

        self.target = make_line_edit(
            "TARGET / HOST / IP"
        )

        self.scan_type = QtWidgets.QComboBox()

        self.scan_type.addItems([
            "Basic scan",
            "Ping discovery",
            "Service/version detection",
            "OS detection"
        ])

        self.ports = make_line_edit(
            "OPTIONAL, e.g. 80,443"
        )

        self.timing = QtWidgets.QComboBox()

        self.timing.addItems([
            "Normal",
            "Polite",
            "Fast"
        ])

        add_form_row(
            self.options_layout,
            "TARGET",
            self.target
        )

        add_form_row(
            self.options_layout,
            "SCAN TYPE",
            self.scan_type
        )

        add_form_row(
            self.options_layout,
            "PORTS",
            self.ports
        )

        add_form_row(
            self.options_layout,
            "TIMING",
            self.timing
        )

        self.target.textChanged.connect(
            self.update_preview
        )

        self.scan_type.currentIndexChanged.connect(
            self.update_preview
        )

        self.ports.textChanged.connect(
            self.update_preview
        )

        self.timing.currentIndexChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def command_preview(
        self
    ):

        args = self.get_arguments()

        return "nmap " + " ".join(
            f'"{x}"' if " " in x else x
            for x in args
        )

    def get_arguments(
        self
    ):

        args = []

        scan_index = (
            self.scan_type.currentIndex()
        )

        if scan_index == 1:

            args.append(
                "-sn"
            )

        elif scan_index == 2:

            args.append(
                "-sV"
            )

        elif scan_index == 3:

            args.append(
                "-O"
            )

        ports = self.ports.text().strip()

        if ports:

            args.extend([
                "-p",
                ports
            ])

        timing = (
            self.timing.currentIndex()
        )

        if timing == 1:

            args.append(
                "-T2"
            )

        elif timing == 2:

            args.append(
                "-T4"
            )

        target = self.target.text().strip()

        if target:

            args.append(
                target
            )

        return args


# ============================================================
# PING OPTIONS
# ============================================================

class PingOptionsDialog(
    ToolOptionsDialog
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            "PING",
            parent
        )

        self.target = make_line_edit(
            "HOST / IP"
        )

        self.count = make_spinbox(
            1,
            100,
            4
        )

        self.timeout = make_spinbox(
            100,
            60000,
            4000
        )

        add_form_row(
            self.options_layout,
            "TARGET",
            self.target
        )

        add_form_row(
            self.options_layout,
            "PACKETS",
            self.count
        )

        add_form_row(
            self.options_layout,
            "TIMEOUT MS",
            self.timeout
        )

        self.target.textChanged.connect(
            self.update_preview
        )

        self.count.valueChanged.connect(
            self.update_preview
        )

        self.timeout.valueChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def command_preview(
        self
    ):

        return "ping " + " ".join(
            self.get_arguments()
        )

    def get_arguments(
        self
    ):

        args = [
            "-n",
            str(self.count.value()),
            "-w",
            str(self.timeout.value())
        ]

        target = self.target.text().strip()

        if target:

            args.append(
                target
            )

        return args


# ============================================================
# TRACERT OPTIONS
# ============================================================

class TracertOptionsDialog(
    ToolOptionsDialog
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            "TRACERT",
            parent
        )

        self.target = make_line_edit(
            "HOST / IP"
        )

        self.hops = make_spinbox(
            1,
            255,
            30
        )

        add_form_row(
            self.options_layout,
            "TARGET",
            self.target
        )

        add_form_row(
            self.options_layout,
            "MAX HOPS",
            self.hops
        )

        self.target.textChanged.connect(
            self.update_preview
        )

        self.hops.valueChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def command_preview(
        self
    ):

        return "tracert " + " ".join(
            self.get_arguments()
        )

    def get_arguments(
        self
    ):

        args = [
            "-h",
            str(self.hops.value())
        ]

        target = self.target.text().strip()

        if target:

            args.append(
                target
            )

        return args


# ============================================================
# NSLOOKUP OPTIONS
# ============================================================

class NslookupOptionsDialog(
    ToolOptionsDialog
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            "NSLOOKUP",
            parent
        )

        self.hostname = make_line_edit(
            "HOSTNAME / DOMAIN"
        )

        self.server = make_line_edit(
            "OPTIONAL DNS SERVER"
        )

        add_form_row(
            self.options_layout,
            "HOSTNAME",
            self.hostname
        )

        add_form_row(
            self.options_layout,
            "DNS SERVER",
            self.server
        )

        self.hostname.textChanged.connect(
            self.update_preview
        )

        self.server.textChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def command_preview(
        self
    ):

        return "nslookup " + " ".join(
            self.get_arguments()
        )

    def get_arguments(
        self
    ):

        args = []

        hostname = self.hostname.text().strip()

        server = self.server.text().strip()

        if hostname:

            args.append(
                hostname
            )

        if server:

            args.append(
                server
            )

        return args


# ============================================================
# NETSTAT OPTIONS
# ============================================================

class NetstatOptionsDialog(
    ToolOptionsDialog
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            "NETSTAT",
            parent
        )

        self.mode = QtWidgets.QComboBox()

        self.mode.addItems([
            "Connections",
            "All connections + listening ports",
            "Numerical addresses",
            "Routing table",
            "Process IDs"
        ])

        add_form_row(
            self.options_layout,
            "DISPLAY MODE",
            self.mode
        )

        self.mode.currentIndexChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def command_preview(
        self
    ):

        return "netstat " + " ".join(
            self.get_arguments()
        )

    def get_arguments(
        self
    ):

        index = self.mode.currentIndex()

        if index == 1:
            return ["-a"]

        if index == 2:
            return ["-n"]

        if index == 3:
            return ["-r"]

        if index == 4:
            return ["-o"]

        return []


# ============================================================
# IPCONFIG OPTIONS
# ============================================================

class IpconfigOptionsDialog(
    ToolOptionsDialog
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            "IPCONFIG",
            parent
        )

        self.mode = QtWidgets.QComboBox()

        self.mode.addItems([
            "Basic configuration",
            "Full configuration"
        ])

        add_form_row(
            self.options_layout,
            "DISPLAY MODE",
            self.mode
        )

        self.mode.currentIndexChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def command_preview(
        self
    ):

        return "ipconfig " + " ".join(
            self.get_arguments()
        )

    def get_arguments(
        self
    ):

        if self.mode.currentIndex() == 1:

            return [
                "/all"
            ]

        return []


# ============================================================
# TASKLIST OPTIONS
# ============================================================

class TasklistOptionsDialog(
    ToolOptionsDialog
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            "TASKLIST",
            parent
        )

        self.mode = QtWidgets.QComboBox()

        self.mode.addItems([
            "All processes",
            "Verbose information",
            "Services",
            "Modules"
        ])

        add_form_row(
            self.options_layout,
            "DISPLAY MODE",
            self.mode
        )

        self.mode.currentIndexChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def command_preview(
        self
    ):

        return "tasklist " + " ".join(
            self.get_arguments()
        )

    def get_arguments(
        self
    ):

        index = self.mode.currentIndex()

        if index == 1:
            return ["/v"]

        if index == 2:
            return ["/svc"]

        if index == 3:
            return ["/m"]

        return []


# ============================================================
# CURL OPTIONS
# ============================================================

class CurlOptionsDialog(
    ToolOptionsDialog
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            "CURL",
            parent
        )

        self.url = make_line_edit(
            "https://example.com"
        )

        self.method = QtWidgets.QComboBox()

        self.method.addItems([
            "GET",
            "HEAD"
        ])

        add_form_row(
            self.options_layout,
            "URL",
            self.url
        )

        add_form_row(
            self.options_layout,
            "METHOD",
            self.method
        )

        self.url.textChanged.connect(
            self.update_preview
        )

        self.method.currentIndexChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def command_preview(
        self
    ):

        return "curl " + " ".join(
            f'"{x}"' if "://" in x else x
            for x in self.get_arguments()
        )

    def get_arguments(
        self
    ):

        args = []

        if self.method.currentIndex() == 1:

            args.append(
                "-I"
            )

        url = self.url.text().strip()

        if url:

            args.append(
                url
            )

        return args


# ============================================================
# GENERIC COMMAND OPTIONS
# ============================================================

class GenericOptionsDialog(
    ToolOptionsDialog
):

    def __init__(
        self,
        tool_name,
        parent=None
    ):

        super().__init__(
            tool_name,
            parent
        )

        self.arguments = make_line_edit(
            "OPTIONAL ARGUMENTS"
        )

        add_form_row(
            self.options_layout,
            "ARGUMENTS",
            self.arguments
        )

        self.arguments.textChanged.connect(
            self.update_preview
        )

        self.update_preview()

    def command_preview(
        self
    ):

        return (
            self.tool_name.lower()
            + " "
            + self.arguments.text()
        ).strip()

    def get_arguments(
        self
    ):

        # Simple whitespace splitting.
        # This intentionally doesn't use a shell.
        return self.arguments.text().split()


# ============================================================
# DIALOG FACTORY
# ============================================================

def create_options_dialog(
    key,
    parent
):

    dialogs = {

        "NMAP":
            NmapOptionsDialog,

        "PING":
            PingOptionsDialog,

        "TRACERT":
            TracertOptionsDialog,

        "NSLOOKUP":
            NslookupOptionsDialog,

        "NETSTAT":
            NetstatOptionsDialog,

        "IPCONFIG":
            IpconfigOptionsDialog,

        "TASKLIST":
            TasklistOptionsDialog,

        "CURL":
            CurlOptionsDialog

    }

    dialog_class = dialogs.get(
        key
    )

    if dialog_class:

        return dialog_class(
            parent
        )

    return GenericOptionsDialog(
        key,
        parent
    )


# ============================================================
# CUSTOM TOOL CONFIGURATION
# ============================================================

class CustomToolDialog(QtWidgets.QDialog):

    TAB_NAMES = [
        "COMMAND",
        "RESEARCH",
        "CODE LAB",
        "PERMISSIONS"
    ]

    def __init__(self, executable, parent=None):
        super().__init__(parent)

        self.executable = Path(executable)

        self.setWindowTitle(
            f"CATALYST // NEW TOOL // {self.executable.name.upper()}"
        )

        self.setMinimumWidth(560)
        self.setModal(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("NEW TOOL DETECTED")
        title.setObjectName("DialogTitle")
        layout.addWidget(title)

        subtitle = QtWidgets.QLabel(
            "CUSTOM REGISTRY // CONFIGURE BEFORE FIRST USE"
        )
        subtitle.setObjectName("DialogSubtitle")
        layout.addWidget(subtitle)

        layout.addWidget(HudLine())

        detected = QtWidgets.QLabel(
            f"[NEW] {self.executable.name.upper()}\n"
            f"PATH  : {self.executable}"
        )
        detected.setObjectName("DetectedTool")
        detected.setWordWrap(True)
        layout.addWidget(detected)

        self.name = make_line_edit(
            "DISPLAY NAME",
            self.executable.stem.upper()
        )

        self.description = make_line_edit(
            "DESCRIPTION",
            "Custom local executable"
        )

        self.tab = QtWidgets.QComboBox()
        self.tab.addItems(self.TAB_NAMES)

        self.mode = QtWidgets.QComboBox()
        self.mode.addItems([
            "Command line / terminal output",
            "GUI application"
        ])

        self.arguments = make_line_edit(
            "OPTIONAL STARTUP ARGUMENTS"
        )

        add_form_row(layout, "NAME", self.name)
        add_form_row(layout, "DESCRIPTION", self.description)
        add_form_row(layout, "TAB", self.tab)
        add_form_row(layout, "LAUNCH MODE", self.mode)
        add_form_row(layout, "ARGUMENTS", self.arguments)

        preview_label = QtWidgets.QLabel("REGISTRY PREVIEW")
        preview_label.setObjectName("TinyLabel")
        layout.addWidget(preview_label)

        self.preview = QtWidgets.QLabel()
        self.preview.setObjectName("CustomPreview")
        self.preview.setWordWrap(True)
        layout.addWidget(self.preview)

        for widget in (
            self.name,
            self.description,
            self.arguments
        ):
            widget.textChanged.connect(self.update_preview)

        self.tab.currentIndexChanged.connect(self.update_preview)
        self.mode.currentIndexChanged.connect(self.update_preview)

        buttons = QtWidgets.QHBoxLayout()

        cancel = QtWidgets.QPushButton("IGNORE")
        cancel.setObjectName("DialogButton")

        save = QtWidgets.QPushButton("REGISTER TOOL")
        save.setObjectName("LaunchButton")

        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.accept)

        buttons.addWidget(cancel)
        buttons.addStretch()
        buttons.addWidget(save)

        layout.addLayout(buttons)

        self.update_preview()

    def update_preview(self):
        name = self.name.text().strip() or self.executable.stem.upper()
        tab = self.tab.currentText()
        mode = "GUI" if self.mode.currentIndex() == 1 else "CLI"

        self.preview.setText(
            f"{name}  //  {tab}  //  {mode}\n"
            f"EXECUTABLE: {self.executable.name}"
        )

    def get_tool(self):
        name = self.name.text().strip() or self.executable.stem.upper()

        key = name.upper()
        key = re.sub(r"[^A-Z0-9_]+", "_", key).strip("_")

        if not key:
            key = self.executable.stem.upper()

        return key, {
            "name": name,
            "description": (
                self.description.text().strip()
                or "Custom local executable"
            ),
            "command": str(self.executable),
            "category": self.tab.currentText(),
            "tab": self.tab.currentText(),
            "launch_mode": (
                "gui"
                if self.mode.currentIndex() == 1
                else "cli"
            ),
            "arguments": self.arguments.text().split(),
            "custom": True
        }


# ============================================================
# ADD TOOL DIALOG
# ============================================================

class AddToolDialog(
    QtWidgets.QDialog
):

    def __init__(
        self,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.setWindowTitle(
            "CATALYST // REGISTER TOOL"
        )

        self.setMinimumWidth(
            470
        )

        layout = QtWidgets.QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        layout.setSpacing(
            12
        )

        title = QtWidgets.QLabel(
            "REGISTER TOOL"
        )

        title.setObjectName(
            "DialogTitle"
        )

        layout.addWidget(
            title
        )

        subtitle = QtWidgets.QLabel(
            "ADD A LOCAL EXECUTABLE TO THE CATALYST DATABASE"
        )

        subtitle.setObjectName(
            "DialogSubtitle"
        )

        layout.addWidget(
            subtitle
        )

        self.name = QtWidgets.QLineEdit()

        self.name.setPlaceholderText(
            "DISPLAY NAME"
        )

        self.command = QtWidgets.QLineEdit()

        self.command.setPlaceholderText(
            "EXECUTABLE / COMMAND"
        )

        self.description = QtWidgets.QLineEdit()

        self.description.setPlaceholderText(
            "DESCRIPTION"
        )

        self.category = QtWidgets.QComboBox()

        self.category.addItems([
            "COMMAND",
            "RESEARCH",
            "CODE LAB",
            "PERMISSIONS"
        ])

        layout.addWidget(
            self.name
        )

        layout.addWidget(
            self.command
        )

        layout.addWidget(
            self.description
        )

        layout.addWidget(
            self.category
        )

        buttons = QtWidgets.QHBoxLayout()

        cancel = QtWidgets.QPushButton(
            "CANCEL"
        )

        register = QtWidgets.QPushButton(
            "REGISTER"
        )

        cancel.clicked.connect(
            self.reject
        )

        register.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            cancel
        )

        buttons.addStretch()

        buttons.addWidget(
            register
        )

        layout.addLayout(
            buttons
        )

    def get_tool(
        self
    ):

        name = self.name.text().strip()

        command = self.command.text().strip()

        if not name or not command:

            return None

        key = (
            name
            .upper()
            .replace(
                " ",
                "_"
            )
        )

        return key, {

            "name":
                name,

            "description":
                self.description.text().strip()
                or "Custom tool",

            "command":
                command,

            "category":
                self.category.currentText(),

            "tab":
                self.category.currentText(),

            "custom":
                True,

            "launch_mode":
                "cli",

            "arguments":
                []

        }


# ============================================================
# MAIN WINDOW
# ============================================================

class CatalystWindow(
    QtWidgets.QMainWindow
):

    def __init__(
        self
    ):

        super().__init__()

        self.database = load_database()

        self.start_time = time.time()

        self.tool_entries = {}

        self.processes = {}

        self.active_key = None

        self.setWindowTitle(
            "CATALYST // FORERUNNER"
        )

        self.resize(
            1400,
            820
        )

        self.setMinimumSize(
            1100,
            680
        )

        self.build_ui()

        self.setup_shortcuts()

        self.boot_sequence()

        self.telemetry_timer = QtCore.QTimer(
            self
        )

        self.telemetry_timer.timeout.connect(
            self.update_telemetry
        )

        self.telemetry_timer.start(
            1000
        )

        self.update_telemetry()

        self.tool_scan_timer = QtCore.QTimer(self)
        self.tool_scan_timer.timeout.connect(self.background_tool_scan)
        self.tool_scan_timer.start(2500)

    def background_tool_scan(self):
        """Automatically notice new .exe files without restarting."""
        new_files = [
            exe
            for exe in discover_tool_executables()
            if not tool_already_registered(exe, self.database)
        ]

        if not new_files:
            return

        self.log_message(
            f"[AUTO-DETECT] {len(new_files)} new tool(s) waiting for configuration"
        )

        self.scan_new_executables(show_dialogs=True)

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(
        self
    ):

        background = HoloBackground()

        self.setCentralWidget(
            background
        )

        root = QtWidgets.QVBoxLayout(
            background
        )

        root.setContentsMargins(
            30,
            24,
            30,
            20
        )

        root.setSpacing(
            12
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = QtWidgets.QHBoxLayout()

        logo_column = QtWidgets.QVBoxLayout()

        logo_column.setSpacing(
            1
        )

        logo = QtWidgets.QLabel(
            "CATALYST"
        )

        logo.setObjectName(
            "Logo"
        )

        version = QtWidgets.QLabel(
            f"FORERUNNER INTERFACE // V{VERSION}"
        )

        version.setObjectName(
            "Designation"
        )

        logo_column.addWidget(
            logo
        )

        logo_column.addWidget(
            version
        )

        header.addLayout(
            logo_column
        )

        header.addSpacing(
            35
        )

        header_status = QtWidgets.QLabel(
            "LOCAL SECURITY TOOL CONTROL"
        )

        header_status.setObjectName(
            "HeaderStatus"
        )

        header.addWidget(
            header_status
        )

        header.addStretch()

        self.core_status = QtWidgets.QLabel(
            "● CORE ONLINE"
        )

        self.core_status.setObjectName(
            "CoreStatus"
        )

        header.addWidget(
            self.core_status
        )

        root.addLayout(
            header
        )

        root.addWidget(
            HudLine()
        )

        # ----------------------------------------------------
        # MAIN
        # ----------------------------------------------------

        main = QtWidgets.QHBoxLayout()

        main.setSpacing(
            25
        )

        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        nav_column = QtWidgets.QVBoxLayout()

        nav_column.setSpacing(
            4
        )

        nav_title = QtWidgets.QLabel(
            "NAVIGATION"
        )

        nav_title.setObjectName(
            "TinyLabel"
        )

        nav_column.addWidget(
            nav_title
        )

        nav_hint = QtWidgets.QLabel(
            "NUMBER KEYS 1-7"
        )

        nav_hint.setObjectName(
            "NavHint"
        )

        nav_column.addWidget(
            nav_hint
        )

        nav_column.addSpacing(
            10
        )

        self.nav_buttons = []

        tabs = [
            "COMMAND",
            "RESEARCH",
            "CODE LAB",
            "STATS",
            "PERMISSIONS",
            "LOGS",
            "CUSTOM"
        ]

        for index, text in enumerate(
            tabs
        ):

            button = QtWidgets.QPushButton(
                f"[{index + 1}]  {text}"
            )

            button.setCheckable(
                True
            )

            button.setMinimumWidth(
                170
            )

            button.setMinimumHeight(
                40
            )

            button.setCursor(
                QtGui.QCursor(
                    QtCore.Qt.PointingHandCursor
                )
            )

            button.clicked.connect(
                lambda checked,
                i=index:
                self.pages.setCurrentIndex(
                    i
                )
            )

            nav_column.addWidget(
                button
            )

            self.nav_buttons.append(
                button
            )

        nav_column.addStretch()

        nav_column.addWidget(
            HudLine()
        )

        link_label = QtWidgets.QLabel(
            "CONNECTION"
        )

        link_label.setObjectName(
            "TinyLabel"
        )

        nav_column.addWidget(
            link_label
        )

        self.system_status = QtWidgets.QLabel(
            "● ONLINE"
        )

        self.system_status.setObjectName(
            "Online"
        )

        nav_column.addWidget(
            self.system_status
        )

        main.addLayout(
            nav_column,
            0
        )

        # ----------------------------------------------------
        # PAGES
        # ----------------------------------------------------

        self.pages = QtWidgets.QStackedWidget()

        self.pages.setObjectName(
            "Pages"
        )

        self.pages.addWidget(
            self.make_command_page()
        )

        self.pages.addWidget(
            self.make_tool_page(
                "RESEARCH",
                "RESEARCH TOOLS // LOCAL UTILITIES"
            )
        )

        self.pages.addWidget(
            self.make_tool_page(
                "CODE LAB",
                "DEVELOPMENT TOOLS // LOCAL UTILITIES"
            )
        )

        self.pages.addWidget(
            self.make_stats_page()
        )

        self.pages.addWidget(
            self.make_tool_page(
                "PERMISSIONS",
                "AUTHORIZED LOCAL EXECUTION // TOOL CONTROL"
            )
        )

        self.pages.addWidget(
            self.make_logs_page()
        )

        self.pages.addWidget(
            self.make_custom_page()
        )

        self.pages.currentChanged.connect(
            self.nav_changed
        )

        main.addWidget(
            self.pages,
            1
        )

        root.addLayout(
            main,
            1
        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        root.addWidget(
            HudLine()
        )

        footer = QtWidgets.QHBoxLayout()

        self.footer_text = QtWidgets.QLabel(
            "CATALYST // LOCAL EXECUTION MODE // AUTHORIZED TOOLS"
        )

        self.footer_text.setObjectName(
            "FooterText"
        )

        footer.addWidget(
            self.footer_text
        )

        footer.addStretch()

        self.clock = QtWidgets.QLabel()

        self.clock.setObjectName(
            "Clock"
        )

        footer.addWidget(
            self.clock
        )

        root.addLayout(
            footer
        )

        self.nav_buttons[0].setChecked(
            True
        )

    # ========================================================
    # SHORTCUTS
    # ========================================================

    def setup_shortcuts(
        self
    ):

        for index in range(
            7
        ):

            shortcut = QtGui.QShortcut(
                QtGui.QKeySequence(
                    str(index + 1)
                ),
                self
            )

            shortcut.activated.connect(
                lambda i=index:
                self.pages.setCurrentIndex(
                    i
                )
            )

        stop_shortcut = QtGui.QShortcut(
            QtGui.QKeySequence(
                "Ctrl+Q"
            ),
            self
        )

        stop_shortcut.activated.connect(
            self.stop_active_process
        )

    # ========================================================
    # COMMAND PAGE
    # ========================================================

    def make_command_page(
        self
    ):

        page = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            5,
            0,
            5,
            0
        )

        layout.setSpacing(
            10
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = QtWidgets.QHBoxLayout()

        title_column = QtWidgets.QVBoxLayout()

        title_column.setSpacing(
            2
        )

        title = QtWidgets.QLabel(
            "COMMAND DECK"
        )

        title.setObjectName(
            "PageTitle"
        )

        subtitle = QtWidgets.QLabel(
            "SELECT A TOOL TO CONFIGURE AND EXECUTE"
        )

        subtitle.setObjectName(
            "PageSubtitle"
        )

        title_column.addWidget(
            title
        )

        title_column.addWidget(
            subtitle
        )

        header.addLayout(
            title_column
        )

        header.addStretch()

        self.core_widget = CoreWidget()

        header.addWidget(
            self.core_widget
        )

        header.addSpacing(
            12
        )

        self.tool_count = QtWidgets.QLabel(
            "0 / 0 READY"
        )

        self.tool_count.setObjectName(
            "BigCounter"
        )

        header.addWidget(
            self.tool_count,
            alignment=QtCore.Qt.AlignTop
        )

        layout.addLayout(
            header
        )

        # ----------------------------------------------------
        # TELEMETRY
        # ----------------------------------------------------

        telemetry = QtWidgets.QHBoxLayout()

        telemetry.setSpacing(
            28
        )

        telemetry_data = [
            ("CORE", "ONLINE"),
            ("MODE", "LOCAL"),
            ("DATABASE", "READY"),
            ("EXECUTION", "AUTHORIZED")
        ]

        self.telemetry_values = {}

        for label, value in telemetry_data:

            block = QtWidgets.QVBoxLayout()

            block.setSpacing(
                2
            )

            label_widget = QtWidgets.QLabel(
                label
            )

            label_widget.setObjectName(
                "TinyLabel"
            )

            value_widget = QtWidgets.QLabel(
                value
            )

            value_widget.setObjectName(
                "Telemetry"
            )

            block.addWidget(
                label_widget
            )

            block.addWidget(
                value_widget
            )

            telemetry.addLayout(
                block
            )

            self.telemetry_values[
                label
            ] = value_widget

        telemetry.addStretch()

        add_button = QtWidgets.QPushButton(
            "+ REGISTER TOOL"
        )

        add_button.setObjectName(
            "MinimalButton"
        )

        add_button.clicked.connect(
            self.add_tool
        )

        telemetry.addWidget(
            add_button
        )

        rescan_button = QtWidgets.QPushButton(
            "⟳ RESCAN TOOLS"
        )

        rescan_button.setObjectName(
            "MinimalButton"
        )

        rescan_button.clicked.connect(
            self.rescan_tools
        )

        telemetry.addWidget(
            rescan_button
        )

        layout.addLayout(
            telemetry
        )

        layout.addWidget(
            HudLine()
        )

        # ----------------------------------------------------
        # TOOL HEADER
        # ----------------------------------------------------

        tool_header = QtWidgets.QHBoxLayout()

        available = QtWidgets.QLabel(
            "AVAILABLE SYSTEMS"
        )

        available.setObjectName(
            "TinyLabel"
        )

        tool_header.addWidget(
            available
        )

        tool_header.addStretch()

        self.search = QtWidgets.QLineEdit()

        self.search.setPlaceholderText(
            "SEARCH TOOLS..."
        )

        self.search.setMaximumWidth(
            270
        )

        self.search.setClearButtonEnabled(
            True
        )

        self.search.textChanged.connect(
            self.filter_tools
        )

        tool_header.addWidget(
            self.search
        )

        layout.addLayout(
            tool_header
        )

        # ----------------------------------------------------
        # LIVE OUTPUT HEADER
        # ----------------------------------------------------

        terminal_header = QtWidgets.QHBoxLayout()

        terminal_title = QtWidgets.QLabel(
            "LIVE OUTPUT"
        )

        terminal_title.setObjectName(
            "TinyLabel"
        )

        terminal_header.addWidget(
            terminal_title
        )

        terminal_header.addStretch()

        self.terminal_status = QtWidgets.QLabel(
            "IDLE // STDOUT + STDERR"
        )

        self.terminal_status.setObjectName(
            "TerminalStatus"
        )

        terminal_header.addWidget(
            self.terminal_status
        )

        clear_button = QtWidgets.QPushButton(
            "CLEAR"
        )

        clear_button.setObjectName(
            "TerminalButton"
        )

        clear_button.clicked.connect(
            self.clear_terminal
        )

        terminal_header.addWidget(
            clear_button
        )

        self.stop_button = QtWidgets.QPushButton(
            "STOP"
        )

        self.stop_button.setObjectName(
            "StopButton"
        )

        self.stop_button.setEnabled(
            False
        )

        self.stop_button.clicked.connect(
            self.stop_active_process
        )

        terminal_header.addWidget(
            self.stop_button
        )

        layout.addLayout(
            terminal_header
        )

        # ----------------------------------------------------
        # LIVE OUTPUT
        # ----------------------------------------------------

        self.terminal_output = QtWidgets.QPlainTextEdit()

        self.terminal_output.setObjectName(
            "TerminalOutput"
        )

        self.terminal_output.setReadOnly(
            True
        )

        self.terminal_output.setLineWrapMode(
            QtWidgets.QPlainTextEdit.NoWrap
        )

        self.terminal_output.setMaximumBlockCount(
            5000
        )

        self.terminal_output.setMinimumHeight(
            150
        )

        self.terminal_output.setMaximumHeight(
            190
        )

        layout.addWidget(
            self.terminal_output
        )

        # ----------------------------------------------------
        # TOOL GRID HEADER
        # ----------------------------------------------------

        tool_grid_header = QtWidgets.QLabel(
            "TOOL REGISTRY"
        )

        tool_grid_header.setObjectName(
            "TinyLabel"
        )

        layout.addWidget(
            tool_grid_header
        )

        # ----------------------------------------------------
        # TOOL GRID
        # ----------------------------------------------------

        scroll = QtWidgets.QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QtWidgets.QFrame.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )

        container = QtWidgets.QWidget()

        self.tools_grid = QtWidgets.QGridLayout(
            container
        )

        self.tools_grid.setContentsMargins(
            0,
            4,
            8,
            8
        )

        self.tools_grid.setHorizontalSpacing(
            12
        )

        self.tools_grid.setVerticalSpacing(
            10
        )

        for column in range(
            3
        ):

            self.tools_grid.setColumnStretch(
                column,
                1
            )

        scroll.setWidget(
            container
        )

        layout.addWidget(
            scroll,
            1
        )

        self.refresh_tools()

        return page

    # ========================================================
    # GENERIC TOOL PAGE
    # ========================================================

    def make_tool_page(
        self,
        title_text,
        description
    ):
        page = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(10)

        title = QtWidgets.QLabel(title_text)
        title.setObjectName("PageTitle")

        subtitle = QtWidgets.QLabel(description)
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(HudLine())

        registry = QtWidgets.QLabel("ASSIGNED TOOLS")
        registry.setObjectName("TinyLabel")
        layout.addWidget(registry)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )

        container = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(container)
        grid.setContentsMargins(0, 4, 8, 8)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        for column in range(3):
            grid.setColumnStretch(column, 1)

        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        page.setProperty("tool_tab", title_text)
        page._tool_grid = grid

        return page

    def make_custom_page(self):
        page = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(10)

        title = QtWidgets.QLabel("CUSTOM")
        title.setObjectName("PageTitle")

        subtitle = QtWidgets.QLabel(
            "DROP .EXE FILES INTO /TOOLS — CATALYST WILL DETECT THEM"
        )
        subtitle.setObjectName("PageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(HudLine())

        self.custom_status = QtWidgets.QLabel(
            "SCANNING TOOL DIRECTORY..."
        )
        self.custom_status.setObjectName("TerminalStatus")
        layout.addWidget(self.custom_status)

        self.custom_list = QtWidgets.QVBoxLayout()
        self.custom_list.setSpacing(7)
        layout.addLayout(self.custom_list)

        layout.addStretch()

        return page

    def rebuild_assigned_tool_pages(self):
        """Put configured tools on their selected navigation page."""
        page_names = {
            0: "COMMAND",
            1: "RESEARCH",
            2: "CODE LAB",
            4: "PERMISSIONS"
        }

        for index, page_name in page_names.items():
            page = self.pages.widget(index)
            grid = getattr(page, "_tool_grid", None)

            if grid is None:
                continue

            while grid.count():
                item = grid.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            entries = [
                (key, tool)
                for key, tool in self.database.items()
                if tool.get("tab", "COMMAND").upper() == page_name
            ]

            for position, (key, tool) in enumerate(entries):
                entry = ToolEntry(key, tool)
                entry.launchRequested.connect(self.launch_tool)

                row = position // 3
                column = position % 3
                grid.addWidget(entry, row, column)

        if hasattr(self, "custom_status"):
            custom_count = sum(
                1 for tool in self.database.values()
                if tool.get("custom", False)
            )
            self.custom_status.setText(
                f"CUSTOM REGISTRY // {custom_count} CONFIGURED // "
                f"DROP .EXE INTO TOOLS TO ADD MORE"
            )

    def rebuild_custom_page(self):
        if not hasattr(self, "custom_list"):
            return

        while self.custom_list.count():
            item = self.custom_list.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        custom_tools = [
            (key, tool)
            for key, tool in self.database.items()
            if tool.get("custom", False)
        ]

        if not custom_tools:
            empty = QtWidgets.QLabel(
                "[ CUSTOM REGISTRY EMPTY ]\n\n"
                "Drop an .EXE into the tools folder and restart CATALYST."
            )
            empty.setObjectName("ModuleText")
            empty.setAlignment(QtCore.Qt.AlignCenter)
            self.custom_list.addWidget(empty)
            return

        for key, tool in custom_tools:
            line = QtWidgets.QLabel(
                f"> {tool.get('name', key).upper()}   //   "
                f"{tool.get('tab', 'COMMAND')}   //   "
                f"{tool.get('command', '')}"
            )
            line.setObjectName("CustomRegistryLine")
            self.custom_list.addWidget(line)

    # ========================================================
    # INFO PAGE
    # ========================================================

    def make_info_page(
        self,
        title_text,
        description
    ):

        page = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            5,
            0,
            5,
            0
        )

        title = QtWidgets.QLabel(
            title_text
        )

        title.setObjectName(
            "PageTitle"
        )

        subtitle = QtWidgets.QLabel(
            description
        )

        subtitle.setObjectName(
            "PageSubtitle"
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addWidget(
            HudLine()
        )

        readout = QtWidgets.QVBoxLayout()

        readout.addStretch()

        message = QtWidgets.QLabel(
            "[ MODULE READY ]"
        )

        message.setAlignment(
            QtCore.Qt.AlignCenter
        )

        message.setObjectName(
            "ModuleText"
        )

        readout.addWidget(
            message
        )

        hint = QtWidgets.QLabel(
            "USE THE NAVIGATION PANEL TO RETURN TO COMMAND"
        )

        hint.setAlignment(
            QtCore.Qt.AlignCenter
        )

        hint.setObjectName(
            "ModuleHint"
        )

        readout.addWidget(
            hint
        )

        readout.addStretch()

        layout.addLayout(
            readout,
            1
        )

        return page

    # ========================================================
    # STATS PAGE
    # ========================================================

    def make_stats_page(
        self
    ):

        page = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            5,
            0,
            5,
            0
        )

        title = QtWidgets.QLabel(
            "SYSTEM TELEMETRY"
        )

        title.setObjectName(
            "PageTitle"
        )

        subtitle = QtWidgets.QLabel(
            "LIVE CATALYST STATUS"
        )

        subtitle.setObjectName(
            "PageSubtitle"
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addWidget(
            HudLine()
        )

        self.stat_labels = {}

        stats = [
            "TOOLS",
            "ONLINE",
            "OFFLINE",
            "UPTIME"
        ]

        grid = QtWidgets.QGridLayout()

        grid.setHorizontalSpacing(
            80
        )

        grid.setVerticalSpacing(
            35
        )

        for index, name in enumerate(
            stats
        ):

            block = QtWidgets.QVBoxLayout()

            label = QtWidgets.QLabel(
                name
            )

            label.setObjectName(
                "TinyLabel"
            )

            value = QtWidgets.QLabel(
                "0"
            )

            value.setObjectName(
                "HugeNumber"
            )

            block.addWidget(
                label
            )

            block.addWidget(
                value
            )

            grid.addLayout(
                block,
                index // 2,
                index % 2
            )

            self.stat_labels[
                name
            ] = value

        layout.addLayout(
            grid
        )

        layout.addStretch()

        return page

    # ========================================================
    # LOG PAGE
    # ========================================================

    def make_logs_page(
        self
    ):

        page = QtWidgets.QWidget()

        layout = QtWidgets.QVBoxLayout(
            page
        )

        layout.setContentsMargins(
            5,
            0,
            5,
            0
        )

        title = QtWidgets.QLabel(
            "SYSTEM LOG"
        )

        title.setObjectName(
            "PageTitle"
        )

        subtitle = QtWidgets.QLabel(
            "CATALYST ACTIVITY FEED"
        )

        subtitle.setObjectName(
            "PageSubtitle"
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addWidget(
            HudLine()
        )

        self.log_output = QtWidgets.QPlainTextEdit()

        self.log_output.setReadOnly(
            True
        )

        self.log_output.setObjectName(
            "Console"
        )

        layout.addWidget(
            self.log_output,
            1
        )

        return page

    # ========================================================
    # REFRESH TOOLS
    # ========================================================

    def refresh_tools(
        self
    ):
        # COMMAND keeps the original live-output/tool registry.
        while self.tools_grid.count():
            item = self.tools_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.tool_entries.clear()

        command_tools = [
            (key, tool)
            for key, tool in self.database.items()
            if tool.get("tab", "COMMAND").upper() == "COMMAND"
        ]

        for index, (key, tool) in enumerate(command_tools):
            entry = ToolEntry(key, tool)
            entry.launchRequested.connect(self.launch_tool)

            self.tool_entries[key] = entry

            row = index // 3
            column = index % 3

            self.tools_grid.addWidget(
                entry,
                row,
                column
            )

        self.rebuild_assigned_tool_pages()
        self.rebuild_custom_page()
        self.update_tool_count()

    # ========================================================
    # FILTER
    # ========================================================

    def filter_tools(
        self,
        text
    ):

        text = text.lower().strip()

        for key, entry in self.tool_entries.items():

            tool = self.database[
                key
            ]

            searchable = " ".join([

                key,

                tool.get(
                    "name",
                    ""
                ),

                tool.get(
                    "description",
                    ""
                ),

                tool.get(
                    "category",
                    ""
                )

            ]).lower()

            entry.setVisible(
                text in searchable
            )

    # ========================================================
    # AUTO DISCOVER NEW EXES
    # ========================================================

    def scan_new_executables(self, show_dialogs=True):
        new_files = [
            exe
            for exe in discover_tool_executables()
            if not tool_already_registered(exe, self.database)
        ]

        if not new_files:
            return []

        self.log_message(
            f"[DISCOVERY] {len(new_files)} NEW EXECUTABLE(S) DETECTED"
        )

        configured = []

        for executable in new_files:
            self.show_terminal(
                f"\n[NEW TOOL DETECTED] {executable.name}\n"
            )

            if not show_dialogs:
                continue

            self.pages.setCurrentIndex(6)

            dialog = CustomToolDialog(
                executable,
                self
            )

            if dialog.exec() != QtWidgets.QDialog.Accepted:
                self.log_message(
                    f"[IGNORED] {executable.name}"
                )
                continue

            result = dialog.get_tool()

            if not result:
                continue

            key, tool = result

            # Avoid collisions with existing keys.
            base_key = key
            counter = 2
            while key in self.database:
                key = f"{base_key}_{counter}"
                counter += 1

            self.database[key] = tool
            configured.append(tool["name"])

            self.log_message(
                f"[AUTO-REGISTER] {tool['name']} :: "
                f"{tool['tab']} :: {executable.name}"
            )

        if configured:
            save_database(self.database)
            self.refresh_tools()

        return configured

    def rescan_tools(self):
        found = self.scan_new_executables(show_dialogs=True)

        if found:
            self.show_terminal(
                "\n[CATALYST] NEW TOOLS REGISTERED:\n"
                + "\n".join(f"  > {name}" for name in found)
                + "\n"
            )
        else:
            self.show_terminal(
                "\n[CATALYST] TOOL DIRECTORY SCAN COMPLETE :: NO NEW TOOLS\n"
            )

    # ========================================================
    # ADD TOOL
    # ========================================================

    def add_tool(
        self
    ):

        dialog = AddToolDialog(
            self
        )

        if (
            dialog.exec()
            != QtWidgets.QDialog.Accepted
        ):

            return

        result = dialog.get_tool()

        if not result:

            QtWidgets.QMessageBox.warning(
                self,
                "CATALYST",
                "Tool name and command required."
            )

            return

        key, tool = result

        self.database[
            key
        ] = tool

        save_database(
            self.database
        )

        self.refresh_tools()

        self.log_message(
            f"[REGISTER] {tool['name']}"
        )

    # ========================================================
    # LAUNCH TOOL
    # ========================================================

    def launch_tool(
        self,
        key
    ):

        tool = self.database.get(
            key
        )

        if not tool:

            return

        command = tool.get(
            "command",
            ""
        ).strip()

        executable = find_executable(
            command
        )

        if not executable:

            self.log_message(
                f"[MISSING] {tool['name']} :: {command}"
            )

            self.show_terminal(
                f"\n[CATALYST] EXECUTABLE NOT FOUND\n"
                f"TOOL: {tool['name']}\n"
                f"COMMAND: {command}\n"
            )

            return

        # ----------------------------------------------------
        # PREVENT DUPLICATE ACTIVE PROCESS
        # ----------------------------------------------------

        if self.active_key:

            active_process = self.processes.get(
                self.active_key
            )

            if active_process:

                if active_process.state() != (
                    QtCore.QProcess.NotRunning
                ):

                    self.show_terminal(
                        "\n[CATALYST] ANOTHER PROCESS IS ALREADY RUNNING.\n"
                    )

                    return

        # ----------------------------------------------------
        # GUI TOOL
        # ----------------------------------------------------

        if key == "WIRESHARK" or tool.get("launch_mode") == "gui":

            self.launch_gui_tool(
                tool,
                executable
            )

            return

        # ----------------------------------------------------
        # SAVED CUSTOM ARGUMENTS
        # ----------------------------------------------------

        if tool.get("custom"):
            saved_args = tool.get("arguments", [])

            if saved_args:
                self.start_process(
                    key,
                    tool,
                    executable,
                    saved_args
                )
                return

        # ----------------------------------------------------
        # OPTIONS
        # ----------------------------------------------------

        dialog = create_options_dialog(
            key,
            self
        )

        if (
            dialog.exec()
            != QtWidgets.QDialog.Accepted
        ):

            return

        args = dialog.get_arguments()

        # ----------------------------------------------------
        # REQUIRE INPUT FOR TOOLS THAT NEED A TARGET
        # ----------------------------------------------------

        if key in [
            "NMAP",
            "PING",
            "TRACERT",
            "NSLOOKUP",
            "CURL"
        ]:

            if not args:

                QtWidgets.QMessageBox.warning(
                    self,
                    "CATALYST",
                    "A target/value is required."
                )

                return

        self.start_process(
            key,
            tool,
            executable,
            args
        )

    # ========================================================
    # GUI TOOL
    # ========================================================

    def launch_gui_tool(
        self,
        tool,
        executable
    ):

        try:

            process = QtCore.QProcess(
                self
            )

            process.setProgram(
                executable
            )

            process.setWorkingDirectory(
                str(
                    Path(executable).parent
                )
            )

            process.setProcessChannelMode(
                QtCore.QProcess.MergedChannels
            )

            process.readyReadStandardOutput.connect(
                lambda p=process:
                self.read_process_output(
                    p
                )
            )

            process.finished.connect(
                lambda code,
                status,
                p=process,
                name=tool["name"]:
                self.process_finished(
                    name,
                    p,
                    code,
                    status
                )
            )

            process.errorOccurred.connect(
                lambda error,
                p=process,
                name=tool["name"]:
                self.process_error(
                    name,
                    p,
                    error
                )
            )

            self.active_key = tool["name"]

            self.processes[
                tool["name"]
            ] = process

            self.show_terminal(
                f"\n"
                f"============================================================\n"
                f" CATALYST // GUI LAUNCH\n"
                f"============================================================\n"
                f" TOOL       : {tool['name']}\n"
                f" EXECUTABLE : {executable}\n"
                f"------------------------------------------------------------\n"
            )

            self.terminal_status.setText(
                f"RUNNING // {tool['name']}"
            )

            self.stop_button.setEnabled(
                True
            )

            self.log_message(
                f"[OPEN] {tool['name']} :: {executable}"
            )

            process.start()

        except Exception as error:

            self.log_message(
                f"[ERROR] {tool['name']} :: {error}"
            )

    # ========================================================
    # START QPROCESS
    # ========================================================

    def start_process(
        self,
        key,
        tool,
        executable,
        args
    ):

        process = QtCore.QProcess(
            self
        )

        process.setProgram(
            executable
        )

        process.setArguments(
            args
        )

        process.setWorkingDirectory(
            str(
                Path(executable).parent
            )
        )

        process.setProcessChannelMode(
            QtCore.QProcess.MergedChannels
        )

        process.readyReadStandardOutput.connect(
            lambda p=process:
            self.read_process_output(
                p
            )
        )

        process.finished.connect(
            lambda code,
            status,
            p=process,
            name=tool["name"]:
            self.process_finished(
                name,
                p,
                code,
                status
            )
        )

        process.errorOccurred.connect(
            lambda error,
            p=process,
            name=tool["name"]:
            self.process_error(
                name,
                p,
                error
            )
        )

        self.active_key = key

        self.processes[
            key
        ] = process

        command_display = (
            executable
            + " "
            + " ".join(
                args
            )
        )

        self.show_terminal(
            f"\n"
            f"============================================================\n"
            f" CATALYST // COMMAND EXECUTION\n"
            f"============================================================\n"
            f" TOOL       : {tool['name']}\n"
            f" EXECUTABLE : {executable}\n"
            f" ARGUMENTS  : {' '.join(args) if args else '(none)'}\n"
            f"------------------------------------------------------------\n"
        )

        self.terminal_status.setText(
            f"RUNNING // {tool['name']}"
        )

        self.stop_button.setEnabled(
            True
        )

        self.log_message(
            f"[EXEC] {command_display}"
        )

        process.start()

    # ========================================================
    # READ OUTPUT
    # ========================================================

    def read_process_output(
        self,
        process
    ):

        data = bytes(
            process.readAllStandardOutput()
        )

        if not data:

            return

        text = data.decode(
            "utf-8",
            errors="replace"
        )

        self.show_terminal(
            text
        )

    # ========================================================
    # PROCESS FINISHED
    # ========================================================

    def process_finished(
        self,
        name,
        process,
        exit_code,
        exit_status
    ):

        if exit_status == (
            QtCore.QProcess.NormalExit
        ):

            status_text = "EXITED"

        else:

            status_text = "CRASHED"

        self.show_terminal(
            f"\n"
            f"\n"
            f"------------------------------------------------------------\n"
            f" PROCESS {status_text}\n"
            f" TOOL      : {name}\n"
            f" EXIT CODE : {exit_code}\n"
            f"------------------------------------------------------------\n"
        )

        self.log_message(
            f"[{status_text}] {name} :: exit code {exit_code}"
        )

        for key, stored in list(
            self.processes.items()
        ):

            if stored is process:

                del self.processes[
                    key
                ]

                if self.active_key == key:

                    self.active_key = None

        self.stop_button.setEnabled(
            False
        )

        self.terminal_status.setText(
            f"IDLE // LAST: {name}"
        )

    # ========================================================
    # PROCESS ERROR
    # ========================================================

    def process_error(
        self,
        name,
        process,
        error
    ):

        error_text = process.errorString()

        self.show_terminal(
            f"\n"
            f"[PROCESS ERROR]\n"
            f"TOOL  : {name}\n"
            f"ERROR : {error_text}\n"
        )

        self.log_message(
            f"[PROCESS ERROR] {name} :: {error_text}"
        )

    # ========================================================
    # STOP PROCESS
    # ========================================================

    def stop_active_process(
        self
    ):

        if not self.active_key:

            return

        process = self.processes.get(
            self.active_key
        )

        if not process:

            return

        if process.state() == (
            QtCore.QProcess.NotRunning
        ):

            return

        name = self.active_key

        self.show_terminal(
            f"\n"
            f"[CATALYST] STOP REQUESTED :: {name}\n"
        )

        self.log_message(
            f"[STOP] {name}"
        )

        process.terminate()

        if not process.waitForFinished(
            1000
        ):

            process.kill()

        self.active_key = None

        self.stop_button.setEnabled(
            False
        )

        self.terminal_status.setText(
            "IDLE // PROCESS STOPPED"
        )

    # ========================================================
    # TERMINAL
    # ========================================================

    def show_terminal(
        self,
        text,
        append=True
    ):

        if not hasattr(
            self,
            "terminal_output"
        ):

            return

        if not append:

            self.terminal_output.clear()

        cursor = self.terminal_output.textCursor()

        cursor.movePosition(
            QtGui.QTextCursor.End
        )

        self.terminal_output.setTextCursor(
            cursor
        )

        self.terminal_output.insertPlainText(
            text
        )

        self.terminal_output.moveCursor(
            QtGui.QTextCursor.End
        )

        self.terminal_output.ensureCursorVisible()

    def clear_terminal(
        self
    ):

        self.terminal_output.clear()

        self.terminal_status.setText(
            "IDLE // STDOUT + STDERR"
        )

    # ========================================================
    # LOG MESSAGE
    # ========================================================

    def log_message(
        self,
        message
    ):

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        line = (
            f"[{timestamp}] "
            f"{message}"
        )

        write_log(
            message
        )

        if hasattr(
            self,
            "log_output"
        ):

            self.log_output.appendPlainText(
                line
            )

        print(
            line
        )

    # ========================================================
    # BOOT
    # ========================================================

    def boot_sequence(
        self
    ):
        boot_lines = [
            "[OK] Initializing totally legitimate software...",
            "[OK] Checking your mom's phone................ FOUND",
            "[OK] Checking your dad's browser history...... CLASSIFIED",
            "[OK] Checking your WiFi......................... PASSWORD: ********",
            "[OK] Checking fridge contents................... 2% MILK REMAINING",
            "[OK] Locating missing socks..................... NO RESULTS",
            "[OK] Downloading more RAM........................ SUCCESS",
            "[OK] Asking NASA for permission.................. DENIED",
            "[OK] Bribing the firewall........................ $0.00 BUDGET",
            "[OK] Scanning for hackers........................ 47 FOUND",
            "[OK] Scanning for actual cybersecurity skills.... NONE",
            "[OK] Increasing hacker level..................... +9000",
            "[OK] Installing Matrix.exe........................ COMPLETE",
            "[OK] Enabling RGB................................ CRITICAL",
            "[OK] Calibrating keyboard......................... TOO MANY SHORTCUTS",
            "[OK] Checking IP address.......................... 127.0.0.1",
            "[OK] Hiding IP address............................ JUST KIDDING",
            "[OK] Contacting anonymous......................... NO RESPONSE",
            "[OK] Checking Discord status....................... ONLINE",
            "[OK] Checking homework............................ IGNORED",
            "[OK] Checking browser tabs........................ 173",
            "[OK] Closing browser tabs......................... FAILED",
            "[OK] Searching for vulnerabilities................ IN THE USER",
            "[OK] Touching grass................................ ERROR 404",
            "[OK] Checking keyboard............................ CRUSTY",
            "[OK] Checking mouse............................... GAMING",
            "[OK] Installing illegal amount of confidence....... DONE",
        ]

        self.show_terminal(
            "\n"
            "============================================================\n"
            " C A T A L Y S T  //  BOOT SEQUENCE\n"
            "============================================================\n"
        )

        for line in boot_lines:
            self.show_terminal(line + "\n")

        self.log_message("CATALYST CORE INITIALIZED")
        self.log_message(
            f"DATABASE // {len(self.database)} SYSTEMS"
        )
        self.log_message("FORERUNNER HUD ONLINE")
        self.log_message("QPROCESS EXECUTION ENGINE READY")
        self.log_message("LOCAL EXECUTION MODE")

        self.show_terminal(
            "\n"
            "[OK] Loading suspicious-looking terminal......... DONE\n"
            "[OK] Generating hacker name...................... xX_D4rkH4x0r_Xx\n"
            "[OK] Checking if name is taken................... YES\n"
            "[OK] Ignoring that................................ DONE\n"
            "\n"
            "[+] Establishing secure connection...\n"
            "[+] Encrypting absolutely nothing...\n"
            "[+] Decrypting absolutely nothing...\n"
            "\n"
        )

        discovered = self.scan_new_executables(show_dialogs=True)

        if discovered:
            self.show_terminal(
                "\n[OK] NEW TOOLS CONFIGURED....................... "
                f"{len(discovered)}\n"
            )
        else:
            self.show_terminal(
                "\n[OK] TOOL DIRECTORY............................. CLEAN\n"
            )

        self.show_terminal(
            "\n"
            "------------------------------------------------------------\n"
            "SYSTEM STATUS: ● TOTALLY LEGIT\n"
            "HACKER LEVEL:  ████████████████████ 100%\n"
            "BRAIN CELLS:   ██░░░░░░░░░░░░░░░░░░ 11%\n"
            "SKILL LEVEL:   █░░░░░░░░░░░░░░░░░░░ 3%\n"
            "RGB POWER:     ████████████████████ MAXIMUM\n"
            "------------------------------------------------------------\n"
            "> CATALYST INITIALIZED\n"
            "> Welcome, elite hacker.\n"
            "\n"
            "[ PRESS ANY KEY TO PRETEND YOU KNOW WHAT YOU'RE DOING ]\n"
        )

        self.system_status.setText("● ONLINE")
        self.core_status.setText("● CORE ONLINE")

    # ========================================================
    # NAVIGATION
    # ========================================================

    def nav_changed(
        self,
        index
    ):

        for i, button in enumerate(
            self.nav_buttons
        ):

            button.setChecked(
                i == index
            )

    # ========================================================
    # TELEMETRY
    # ========================================================

    def update_telemetry(
        self
    ):

        now = datetime.now()

        self.clock.setText(
            now.strftime(
                "%Y.%m.%d // %H:%M:%S"
            )
        )

        uptime = int(
            time.time()
            - self.start_time
        )

        hours = uptime // 3600

        minutes = (
            uptime % 3600
        ) // 60

        seconds = uptime % 60

        uptime_string = (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

        online = 0

        for tool in self.database.values():

            if find_executable(
                tool.get(
                    "command",
                    ""
                )
            ):

                online += 1

        offline = (
            len(self.database)
            - online
        )

        self.stat_labels[
            "TOOLS"
        ].setText(
            str(
                len(
                    self.database
                )
            )
        )

        self.stat_labels[
            "ONLINE"
        ].setText(
            str(
                online
            )
        )

        self.stat_labels[
            "OFFLINE"
        ].setText(
            str(
                offline
            )
        )

        self.stat_labels[
            "UPTIME"
        ].setText(
            uptime_string
        )

        self.tool_count.setText(
            f"{online} / "
            f"{len(self.database)} READY"
        )

        self.telemetry_values[
            "CORE"
        ].setText(
            "ONLINE"
        )

        self.telemetry_values[
            "MODE"
        ].setText(
            "LOCAL"
        )

        self.telemetry_values[
            "DATABASE"
        ].setText(
            "READY"
        )

        self.telemetry_values[
            "EXECUTION"
        ].setText(
            "AUTHORIZED"
        )

    # ========================================================
    # TOOL COUNT
    # ========================================================

    def update_tool_count(
        self
    ):

        if not hasattr(
            self,
            "tool_count"
        ):

            return

        total = len(
            self.database
        )

        online = sum(

            1

            for tool in
            self.database.values()

            if find_executable(
                tool.get(
                    "command",
                    ""
                )
            )

        )

        self.tool_count.setText(
            f"{online} / "
            f"{total} READY"
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def closeEvent(
        self,
        event
    ):

        for process in list(
            self.processes.values()
        ):

            if process.state() != (
                QtCore.QProcess.NotRunning
            ):

                process.terminate()

                if not process.waitForFinished(
                    500
                ):

                    process.kill()

        event.accept()


# ============================================================
# GLOBAL STYLE
# ============================================================

def apply_global_style(
    app
):

    app.setStyleSheet("""

        * {
            font-family: "Segoe UI";
        }

        QMainWindow {
            background: #02070b;
        }

        QWidget {
            color: #79dbe8;
            background: transparent;
        }


        /* ==================================================
           HEADER
           ================================================== */

        #Logo {
            color: #91f4ff;
            font-size: 30px;
            font-weight: 900;
            letter-spacing: 7px;
        }

        #Designation {
            color: #28616d;
            font-size: 8px;
            letter-spacing: 3px;
        }

        #HeaderStatus {
            color: #2e7785;
            font-size: 9px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        #CoreStatus {
            color: #4de0e9;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
        }


        /* ==================================================
           NAVIGATION
           ================================================== */

        #TinyLabel {
            color: #327d8b;
            font-size: 9px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        #NavHint {
            color: #214e5a;
            font-size: 7px;
            letter-spacing: 1px;
        }

        QPushButton {
            background: transparent;
            color: #397887;

            border: none;
            border-left: 2px solid transparent;

            padding: 9px 12px;

            text-align: left;

            font-size: 10px;
            font-weight: bold;

            letter-spacing: 1px;
        }

        QPushButton:hover {
            color: #9bf6ff;

            background: rgba(
                30,
                150,
                170,
                25
            );

            border-left: 2px solid #207a89;
        }

        QPushButton:checked {
            color: #c1fbff;

            background: rgba(
                35,
                180,
                200,
                42
            );

            border-left: 3px solid #49e6f2;
        }


        /* ==================================================
           PAGE
           ================================================== */

        #PageTitle {
            color: #8ceefa;
            font-size: 25px;
            font-weight: 700;
            letter-spacing: 4px;
        }

        #PageSubtitle {
            color: #326c79;
            font-size: 8px;
            letter-spacing: 2px;
        }

        #BigCounter {
            color: #4ed3e1;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
        }


        /* ==================================================
           TELEMETRY
           ================================================== */

        #Telemetry {
            color: #70dce9;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1px;
        }


        /* ==================================================
           TOOL CARDS
           ================================================== */

        #ToolName {
            color: #91edf8;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1px;
        }

        #ToolDescription {
            color: #427582;
            font-size: 8px;
        }

        #ToolCategory {
            color: #2c7180;
            font-size: 7px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        #ToolArrow {
            color: #3bd5e5;
            font-size: 16px;
            font-weight: bold;
        }

        #Online {
            color: #42dbc5;
            font-size: 8px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        #Offline {
            color: #9a5360;
            font-size: 8px;
            font-weight: bold;
            letter-spacing: 1px;
        }


        /* ==================================================
           OPEN BUTTON
           ================================================== */

        #OpenButton {
            color: #61dce9;

            border: 1px solid #1a5a68;

            padding: 5px 12px;

            font-size: 8px;
            letter-spacing: 1px;

            min-width: 54px;
        }

        #OpenButton:hover {
            color: #d0fdff;

            border: 1px solid #45e5f2;

            background: rgba(
                35,
                190,
                210,
                45
            );
        }

        #OpenButton:pressed {
            background: rgba(
                35,
                190,
                210,
                70
            );
        }


        /* ==================================================
           REGISTER
           ================================================== */

        #MinimalButton {
            color: #55d6e5;

            border: none;
            border-bottom: 1px solid #1c6674;

            padding: 5px 10px;

            font-size: 8px;
        }


        /* ==================================================
           SEARCH
           ================================================== */

        QLineEdit {
            background: rgba(
                2,
                10,
                14,
                120
            );

            color: #83e8f5;

            border: none;
            border-bottom: 1px solid #17434e;

            padding: 6px;

            font-size: 9px;

            selection-background-color: #155968;
        }

        QLineEdit:focus {
            border-bottom: 1px solid #3bd5e5;
        }

        QLineEdit::placeholder {
            color: #285562;
        }


        /* ==================================================
           OPTIONS
           ================================================== */

        #OptionLabel {
            color: #397b88;
            font-size: 8px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        QComboBox,
        QSpinBox {
            background: #040d12;
            color: #76dce9;

            border: 1px solid #16434f;

            padding: 7px;

            font-size: 9px;
        }

        QComboBox:hover,
        QSpinBox:hover {
            border: 1px solid #2a8595;
        }

        QComboBox QAbstractItemView {
            background: #040d12;
            color: #76dce9;
            border: 1px solid #1d5966;
            selection-background-color: #124b57;
        }


        /* ==================================================
           TERMINAL
           ================================================== */

        #TerminalOutput {
            background: rgba(
                1,
                8,
                12,
                225
            );

            color: #63dce8;

            border: 1px solid #123b45;
            border-left: 2px solid #236d7b;

            padding: 8px;

            font-family:
                "Consolas",
                "Cascadia Mono",
                monospace;

            font-size: 10px;

            selection-background-color: #164d58;
        }

        #TerminalStatus {
            color: #285e6b;

            font-family:
                "Consolas";

            font-size: 7px;

            letter-spacing: 2px;
        }

        #TerminalButton {
            color: #4fb9c7;

            border: 1px solid #164752;

            padding: 4px 9px;

            font-size: 7px;
        }

        #StopButton {
            color: #d07b86;

            border: 1px solid #713944;

            padding: 4px 9px;

            font-size: 7px;
        }

        #StopButton:disabled {
            color: #3c252b;
            border: 1px solid #25171a;
        }


        /* ==================================================
           COMMAND PREVIEW
           ================================================== */

        #CommandPreview {
            color: #55d6e5;

            background: #020a0e;

            border: 1px solid #16434f;

            font-family:
                "Consolas",
                monospace;

            font-size: 9px;
        }


        /* ==================================================
           SCROLL
           ================================================== */

        QScrollArea {
            background: transparent;
            border: none;
        }

        QScrollBar:vertical {
            background: transparent;
            width: 5px;
        }

        QScrollBar::handle:vertical {
            background: #15505c;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background: #2ba6b9;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
        }


        /* ==================================================
           PAGES
           ================================================== */

        #Pages {
            background: transparent;
            border: none;
        }


        /* ==================================================
           STATS
           ================================================== */

        #HugeNumber {
            color: #6ee9f6;
            font-size: 36px;
            font-weight: 300;
            letter-spacing: 2px;
        }


        /* ==================================================
           MODULES
           ================================================== */

        #ModuleText {
            color: #347b88;
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 4px;
        }

        #ModuleHint {
            color: #1e4d59;
            font-size: 8px;
            letter-spacing: 2px;
        }


        /* ==================================================
           LOG CONSOLE
           ================================================== */

        #Console {
            background: rgba(
                2,
                9,
                13,
                190
            );

            color: #58cbd9;

            border: 1px solid #123b45;

            font-family:
                "Consolas",
                monospace;

            font-size: 10px;

            padding: 8px;
        }


        /* ==================================================
           DIALOG
           ================================================== */

        QDialog {
            background: #030a0f;
        }

        #DialogTitle {
            color: #7eeaf7;
            font-size: 17px;
            font-weight: bold;
            letter-spacing: 3px;
        }

        #DialogSubtitle {
            color: #285d69;
            font-size: 8px;
            letter-spacing: 1px;
        }

        QDialog QLineEdit {
            background: #040c11;

            border: 1px solid #16434f;

            padding: 9px;
        }

        QDialog QLineEdit:focus {
            border: 1px solid #32cddd;
        }

        QDialog QPushButton {
            border: 1px solid #174c59;

            padding: 8px 14px;
        }

        #DialogButton {
            color: #5c9ba7;
        }

        #LaunchButton {
            color: #9cf7ff;

            border: 1px solid #2b9dac;

            background: rgba(
                25,
                120,
                135,
                30
            );
        }

        #LaunchButton:hover {
            border: 1px solid #48e4f0;

            background: rgba(
                30,
                170,
                190,
                50
            );
        }


        /* ==================================================
           CUSTOM REGISTRY
           ================================================== */

        #DetectedTool,
        #CustomPreview {
            color: #57d8e6;
            background: #040c11;
            border: 1px solid #16434f;
            padding: 10px;
            font-family: "Consolas", monospace;
            font-size: 9px;
        }

        #CustomRegistryLine {
            color: #5ed7e4;
            background: rgba(2, 10, 14, 150);
            border-left: 2px solid #277b89;
            padding: 8px;
            font-family: "Consolas", monospace;
            font-size: 9px;
        }

        /* ==================================================
           FOOTER
           ================================================== */

        #FooterText {
            color: #285e6b;
            font-size: 7px;
            letter-spacing: 2px;
        }

        #Clock {
            color: #397b88;
            font-family: "Consolas";
            font-size: 8px;
        }

    """)


# ============================================================
# MAIN
# ============================================================

def main():

    app = QtWidgets.QApplication(
        sys.argv
    )

    app.setApplicationName(
        APP_NAME
    )

    apply_global_style(
        app
    )

    window = CatalystWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
