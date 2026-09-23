"""
Shutdown Scheduler v4.1 (Windows 11 Fluent Design Edition)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A modern, native-feeling Windows 11 utility desktop application with TH/EN support.
Built with Python, CustomTkinter, and PyStray adhering to WinUI 3 / Fluent Design guidelines.

Features:
  • Windows 11 Fluent Design Dark Theme & Mica Palette
  • Native DWM Dark Title Bar and Rounded Window Corners
  • Clean WinUI 3 Navigation View with Active Indicator Strip
  • Hero Countdown Timer Display & Modern Steppers
  • Clock Schedule with Daily Repeat Settings Card
  • Windows 11 Settings-Style Cards with Right-Aligned Toggles
  • Professional Bilingual System (🇹🇭 ภาษาไทย / 🇬🇧 English)
  • System Tray Background Operation with Fluent Tray Icon
  • 5-Minute Pre-Shutdown Warning Alert Dialog
"""

import os
import sys
import platform
import subprocess
import threading
from datetime import datetime, timedelta
import customtkinter as ctk
from tkinter import messagebox

import pystray
from PIL import Image, ImageDraw


# ─── Windows 11 Native DWM Integration ────────────────────────────────────────

def apply_windows_11_styling(window: ctk.CTk | ctk.CTkToplevel) -> None:
    """Apply native Windows 11 rounded corners and dark title bar via DWM API."""
    if platform.system() != "Windows":
        return
    try:
        import ctypes
        from ctypes import wintypes
        window.update_idletasks()
        hwnd = window.winfo_id()
        # Ensure we target the top-level root window
        GA_ROOT = 2
        root_hwnd = ctypes.windll.user32.GetAncestor(hwnd, GA_ROOT)
        if not root_hwnd:
            root_hwnd = hwnd

        # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        dark_mode = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            root_hwnd,
            ctypes.wintypes.DWORD(20),
            ctypes.byref(dark_mode),
            ctypes.sizeof(dark_mode),
        )

        # DWMWA_WINDOW_CORNER_PREFERENCE = 33 (2 = DWMWCP_ROUND)
        corner_pref = ctypes.c_int(2)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            root_hwnd,
            ctypes.wintypes.DWORD(33),
            ctypes.byref(corner_pref),
            ctypes.sizeof(corner_pref),
        )
    except Exception:
        pass


# ─── Windows 11 Fluent Color Palette (WinUI 3 Dark Tokens) ────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FONT_FAMILY      = "Segoe UI"
FONT_MONO        = "Consolas"

# Backgrounds & Surfaces
BG_APP           = "#202020"  # Windows 11 Mica Base Window
BG_SIDEBAR       = "#1b1b1b"  # Navigation View Rail
BORDER_DIVIDER   = "#2d2d2d"  # 1px Subtle Rail Divider
CARD_BG          = "#2b2b2b"  # WinUI 3 Layer Surface
CARD_ALT_BG      = "#242424"  # WinUI 3 Inset / Control Surface
CARD_BORDER      = "#363636"  # WinUI 3 1px Stroke
CARD_BORDER_HOV  = "#484848"  # Hovered Stroke

# Windows 11 Accent Blue
ACCENT_BLUE      = "#0078d4"  # Primary Accent Fill
ACCENT_HOVER     = "#1084d9"  # Accent Hover Fill
ACCENT_PRESSED   = "#006cc1"  # Accent Pressed Fill
ACCENT_SELECTION = "#2a3542"  # Selected Nav Item Background
TEXT_ACCENT      = "#60cdff"  # Accent Text in Dark Theme

# Text Colors
TEXT_PRIMARY     = "#ffffff"  # High-contrast primary text
TEXT_SECONDARY   = "#a0a0a0"  # Secondary label text
TEXT_MUTED       = "#737373"  # Muted caption / disabled text

# Buttons & Controls
BTN_SEC_BG       = "#303030"  # Secondary button fill
BTN_SEC_HOVER    = "#3c3c3c"
BTN_SEC_BORDER   = "#3d3d3d"
BTN_SEC_TEXT     = "#ffffff"

BTN_DANGER_BG    = "#c42b1c"  # Windows 11 Critical Red
BTN_DANGER_HOVER = "#d13426"
BTN_DANGER_TEXT  = "#ffffff"

BTN_CANCEL_BG    = "#382224"  # Subdued danger button
BTN_CANCEL_HOVER = "#492b2e"
BTN_CANCEL_BORDER= "#5c2e33"
BTN_CANCEL_TEXT  = "#ff99a4"

STATUS_READY     = "#6ccb5f"  # Success green
STATUS_BUSY      = "#60cdff"  # Fluent cyan / running blue


# ─── Bilingual Dictionary (Authentic Microsoft Windows Phrasing) ──────────────

TRANSLATIONS = {
    "TH": {
        "app_title": "Shutdown Scheduler",
        "app_badge": "Windows 11 Edition",
        "nav_timer": "ตัวนับเวลา",
        "nav_schedule": "กำหนดเวลา",
        "nav_settings": "การตั้งค่า",
        "status_ready": "พร้อมทำงาน",
        "status_running": "กำลังทำงาน",
        "timer_title": "ตัวนับเวลาถอยหลัง",
        "timer_desc": "กำหนดระยะเวลานับถอยหลังก่อนที่คอมพิวเตอร์จะปิดเครื่องอัตโนมัติ",
        "time_labels": "ชั่วโมง             นาที             วินาที",
        "spinner_hours": "ชั่วโมง",
        "spinner_minutes": "นาที",
        "spinner_seconds": "วินาที",
        "preset_15m": "15 นาที",
        "preset_30m": "30 นาที",
        "preset_1h": "1 ชั่วโมง",
        "preset_2h": "2 ชั่วโมง",
        "btn_start": "เริ่มนับถอยหลัง",
        "btn_cancel": "ยกเลิก",
        "sched_title": "กำหนดเวลาปิดเครื่อง",
        "sched_desc": "ระบุเวลาตามนาฬิกาที่ต้องการปิดเครื่อง ระบบจะคำนวณและเริ่มนับถอยหลังอัตโนมัติ",
        "target_hr": "ชั่วโมง (0-23)",
        "target_min": "นาที (0-59)",
        "sched_info": "ระบบจะคำนวณเวลาคงเหลือและเริ่มนับถอยหลังอัตโนมัติ",
        "sched_target_banner": "กำหนดเวลาแล้ว: ระบบจะปิดเครื่องเวลา {time}",
        "daily_repeat": "ทำงานซ้ำทุกวัน",
        "daily_repeat_desc": "สั่งปิดเครื่องตามเวลานี้ซ้ำทุกวันอัตโนมัติ (Daily Repeat)",
        "btn_set_sched": "กำหนดเวลาปิดเครื่อง",
        "settings_title": "การตั้งค่าระบบ",
        "settings_desc": "ปรับแต่งการทำงานของโปรแกรมและการแจ้งเตือนในระบบปฏิบัติการ",
        "sw_close_tray": "ย่อลง System Tray เมื่อปิดหน้าต่าง",
        "sw_close_tray_desc": "ให้โปรแกรมทำงานเบื้องหลังต่อไปในถาดระบบเมื่อกดปุ่มปิดหน้าต่าง (X)",
        "sw_warning": "แจ้งเตือนก่อนปิดเครื่อง 5 นาที",
        "sw_warning_desc": "แสดงหน้าต่างแจ้งเตือนล่วงหน้า 5 นาทีก่อนระบบจะดำเนินการปิดเครื่อง",
        "tray_guide_title": "การทำงานในถาดระบบ (System Tray)",
        "tray_guide_body": (
            "• โปรแกรมจะทำงานเบื้องหลังใน System Tray มุมขวาล่างของแถบงาน (Taskbar)\n"
            "• คลิกขวาที่ไอคอนเพื่อตรวจสอบเวลาคงเหลือ หรือเปิดหน้าต่างหลักขึ้นมาใหม่\n"
            "• หากต้องการออกจากโปรแกรมอย่างสมบูรณ์ ให้คลิกขวาแล้วเลือก 'ออกจากโปรแกรม'"
        ),
        "about_title": "เกี่ยวกับโปรแกรม",
        "about_body": "Shutdown Scheduler v4.1 · ออกแบบตามแนวทาง Windows 11 Fluent Design System",
        "warning_dialog_title": "แจ้งเตือนการปิดเครื่อง",
        "warning_dialog_msg": (
            "ระบบจะปิดเครื่องคอมพิวเตอร์ในอีก 5 นาที\n"
            "กรุณาบันทึกข้อมูลและปิดโปรแกรมที่กำลังทำงานอยู่ให้เรียบร้อย"
        ),
        "warning_btn_cancel": "ยกเลิกการปิดเครื่อง",
        "warning_btn_ok": "รับทราบ",
        "tray_open": "เปิด Shutdown Scheduler",
        "tray_time": "เวลาคงเหลือ",
        "tray_cancel": "ยกเลิกการปิดเครื่อง",
        "tray_exit": "ออกจากโปรแกรม",
        "invalid_time_msg": "กรุณากำหนดระยะเวลาอย่างน้อย 1 วินาทีขึ้นไป",
    },
    "EN": {
        "app_title": "Shutdown Scheduler",
        "app_badge": "Windows 11 Edition",
        "nav_timer": "Timer",
        "nav_schedule": "Schedule",
        "nav_settings": "Settings",
        "status_ready": "Ready",
        "status_running": "Running",
        "timer_title": "Countdown Timer",
        "timer_desc": "Set a duration before the computer shuts down automatically.",
        "time_labels": "HOURS             MINUTES             SECONDS",
        "spinner_hours": "Hours",
        "spinner_minutes": "Minutes",
        "spinner_seconds": "Seconds",
        "preset_15m": "15 min",
        "preset_30m": "30 min",
        "preset_1h": "1 hour",
        "preset_2h": "2 hours",
        "btn_start": "Start Countdown",
        "btn_cancel": "Cancel",
        "sched_title": "Clock Schedule",
        "sched_desc": "Specify exact clock time to trigger automatic system shutdown.",
        "target_hr": "Hour (0-23)",
        "target_min": "Minute (0-59)",
        "sched_info": "Target countdown will be calculated and scheduled automatically.",
        "sched_target_banner": "Schedule set: System will shut down at {time}",
        "daily_repeat": "Daily repeat",
        "daily_repeat_desc": "Automatically repeat this shutdown schedule every day.",
        "btn_set_sched": "Set Schedule",
        "settings_title": "Settings",
        "settings_desc": "Configure background application behavior and notification alerts.",
        "sw_close_tray": "Minimize to System Tray on close",
        "sw_close_tray_desc": "Keep application running in background tray when closing the window (X).",
        "sw_warning": "5-minute pre-shutdown warning",
        "sw_warning_desc": "Display a reminder dialog 5 minutes prior to scheduled shutdown.",
        "tray_guide_title": "System Tray Behavior",
        "tray_guide_body": (
            "• Application remains active in the System Tray in the Windows taskbar.\n"
            "• Right-click the tray icon to inspect remaining time or restore the window.\n"
            "• To close the application completely, right-click and choose 'Exit'."
        ),
        "about_title": "About Application",
        "about_body": "Shutdown Scheduler v4.1 · Designed with Windows 11 Fluent Design System",
        "warning_dialog_title": "Shutdown Warning",
        "warning_dialog_msg": (
            "The computer will shut down in 5 minutes.\n"
            "Please save any unsaved work before the system turns off."
        ),
        "warning_btn_cancel": "Cancel Shutdown",
        "warning_btn_ok": "Acknowledge",
        "tray_open": "Open Shutdown Scheduler",
        "tray_time": "Remaining Time",
        "tray_cancel": "Cancel Shutdown",
        "tray_exit": "Exit",
        "invalid_time_msg": "Please select a duration of at least 1 second.",
    }
}


# ─── Fluent System Tray Icon Generator ────────────────────────────────────────

def create_fluent_tray_image(width: int = 64, height: int = 64) -> Image.Image:
    """Generate a clean Windows 11 Fluent Design power/clock icon for System Tray."""
    scale = 4
    w, h = width * scale, height * scale
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = int(w * 0.08)
    cx, cy = w / 2, h / 2

    # Fluent blue disc
    draw.ellipse([pad, pad, w - pad, h - pad], fill=(24, 108, 192, 255))
    # Subtle inner highlight ring
    rim_w = max(scale, int(w * 0.03))
    draw.ellipse([pad + rim_w, pad + rim_w, w - pad - rim_w, h - pad - rim_w], outline=(96, 205, 255, 120), width=rim_w)

    # Power Arc
    arc_inset = int(w * 0.24)
    stroke_w = max(scale * 2, int(w * 0.08))
    draw.arc([arc_inset, arc_inset, w - arc_inset, h - arc_inset], start=305, end=235, fill=(255, 255, 255, 255), width=stroke_w)

    # Vertical Pin
    pin_top = int(w * 0.18)
    pin_bot = int(cy + stroke_w * 0.2)
    half_pin = stroke_w // 2
    draw.rounded_rectangle([cx - half_pin, pin_top, cx + half_pin, pin_bot], radius=half_pin, fill=(255, 255, 255, 255))

    return img.resize((width, height), Image.Resampling.LANCZOS)


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# ─── Windows 11 Fluent Stepper (NumberBox Widget) ─────────────────────────────

class FluentTimeSpinner(ctk.CTkFrame):
    """A clean, professional Windows 11 Fluent Design time stepper widget."""

    def __init__(
        self,
        master,
        label_text: str,
        min_val: int = 0,
        max_val: int = 59,
        initial: int = 0,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._min = min_val
        self._max = max_val
        self._value = initial

        # Header Title
        self._title_label = ctk.CTkLabel(
            self,
            text=label_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
        )
        self._title_label.pack(pady=(0, 4))

        # Control Container Box (WinUI 3 Inset style)
        self._card = ctk.CTkFrame(
            self,
            fg_color=CARD_ALT_BG,
            corner_radius=6,
            border_width=1,
            border_color=CARD_BORDER,
        )
        self._card.pack()

        # ▲ Up Button
        self._up_btn = ctk.CTkButton(
            self._card,
            text="▲",
            width=76,
            height=26,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            corner_radius=4,
            fg_color=CARD_BG,
            hover_color=BTN_SEC_HOVER,
            text_color=TEXT_PRIMARY,
            command=self._increment,
        )
        self._up_btn.pack(padx=5, pady=(5, 1))

        # Centered Digital Display
        self._display = ctk.CTkLabel(
            self._card,
            text=f"{self._value:02d}",
            font=ctk.CTkFont(family=FONT_MONO, size=30, weight="bold"),
            text_color=TEXT_PRIMARY,
            width=76,
        )
        self._display.pack(padx=5, pady=(1, 1))

        # ▼ Down Button
        self._down_btn = ctk.CTkButton(
            self._card,
            text="▼",
            width=76,
            height=26,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            corner_radius=4,
            fg_color=CARD_BG,
            hover_color=BTN_SEC_HOVER,
            text_color=TEXT_PRIMARY,
            command=self._decrement,
        )
        self._down_btn.pack(padx=5, pady=(1, 5))

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v: int) -> None:
        self._value = max(self._min, min(self._max, v))
        self._display.configure(text=f"{self._value:02d}")

    def update_label(self, text: str) -> None:
        self._title_label.configure(text=text)

    def set_state(self, state: str) -> None:
        self._up_btn.configure(state=state)
        self._down_btn.configure(state=state)
        color = TEXT_MUTED if state == "disabled" else TEXT_PRIMARY
        self._display.configure(text_color=color)

    def _increment(self) -> None:
        if self._value >= self._max:
            self.value = self._min
        else:
            self.value = self._value + 1

    def _decrement(self) -> None:
        if self._value <= self._min:
            self.value = self._max
        else:
            self.value = self._value - 1


# ─── Main Application Window ──────────────────────────────────────────────────

class ShutdownSchedulerApp(ctk.CTk):
    """Windows 11 Fluent Design Desktop Application for Automatic Shutdown."""

    WIDTH  = 760
    HEIGHT = 530

    def __init__(self) -> None:
        super().__init__()

        # Window Setup
        self.title("Shutdown Scheduler")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=BG_APP)

        # Set App Window Icon if exists
        icon_path = get_resource_path("app_icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Apply Windows 11 DWM rounded corners and dark title bar
        apply_windows_11_styling(self)

        # Internal State
        self._lang: str = "TH"  # Default Language: Thai
        self._remaining: int = 0
        self._timer_id: str | None = None
        self._is_running: bool = False
        self._warning_shown: bool = False
        self._schedule_target_dt: datetime | None = None
        self._active_page: str = "timer"

        # Settings
        self._close_to_tray_var = ctk.BooleanVar(value=True)
        self._enable_warning_var = ctk.BooleanVar(value=True)
        self._daily_repeat_var = ctk.BooleanVar(value=False)

        # Window Close Protocol
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Build WinUI 3 Navigation View Layout
        self._build_fluent_layout()

        # Initialize System Tray
        self._setup_tray_icon()

        # Apply Initial Translations
        self._apply_language_texts()

    # ── Localization Helper ───────────────────────────────────────────────────

    def t(self, key: str, **kwargs) -> str:
        """Fetch localized text string by key."""
        lang_dict = TRANSLATIONS.get(self._lang, TRANSLATIONS["EN"])
        val = lang_dict.get(key, key)
        if kwargs:
            val = val.format(**kwargs)
        return val

    def _set_language(self, lang: str) -> None:
        """Switch language (TH / EN) and refresh UI text."""
        if self._lang != lang:
            self._lang = lang
            self._apply_language_texts()

    def _apply_language_texts(self) -> None:
        """Refresh all labels and buttons with the active language."""
        # Navigation Items
        self._nav_btn_timer.configure(text=self.t("nav_timer"))
        self._nav_btn_sched.configure(text=self.t("nav_schedule"))
        self._nav_btn_settings.configure(text=self.t("nav_settings"))

        # Language Switcher Pill Highlight
        if self._lang == "TH":
            self._lang_btn_th.configure(fg_color=BTN_SEC_BG, text_color=TEXT_PRIMARY)
            self._lang_btn_en.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
        else:
            self._lang_btn_th.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
            self._lang_btn_en.configure(fg_color=BTN_SEC_BG, text_color=TEXT_PRIMARY)

        # Status Label
        status_key = "status_running" if self._is_running else "status_ready"
        self._drawer_status_label.configure(text=self.t(status_key))

        # Timer View
        self._timer_title_label.configure(text=self.t("timer_title"))
        self._timer_desc_label.configure(text=self.t("timer_desc"))
        self._timer_units_label.configure(text=self.t("time_labels"))
        self._hr_spinner.update_label(self.t("spinner_hours"))
        self._min_spinner.update_label(self.t("spinner_minutes"))
        self._sec_spinner.update_label(self.t("spinner_seconds"))
        self._preset_btns[0].configure(text=self.t("preset_15m"))
        self._preset_btns[1].configure(text=self.t("preset_30m"))
        self._preset_btns[2].configure(text=self.t("preset_1h"))
        self._preset_btns[3].configure(text=self.t("preset_2h"))
        self._start_btn.configure(text=self.t("btn_start"))
        self._cancel_btn.configure(text=self.t("btn_cancel"))

        # Schedule View
        self._sched_title_label.configure(text=self.t("sched_title"))
        self._sched_desc_label.configure(text=self.t("sched_desc"))
        self._sched_hr_spinner.update_label(self.t("target_hr"))
        self._sched_min_spinner.update_label(self.t("target_min"))
        self._daily_repeat_title.configure(text=self.t("daily_repeat"))
        self._daily_repeat_desc.configure(text=self.t("daily_repeat_desc"))
        self._sched_start_btn.configure(text=self.t("btn_set_sched"))
        self._sched_cancel_btn.configure(text=self.t("btn_cancel"))

        if not self._is_running:
            self._sched_info_label.configure(text=self.t("sched_info"))

        # Settings View
        self._settings_title_label.configure(text=self.t("settings_title"))
        self._settings_desc_label.configure(text=self.t("settings_desc"))
        self._sw_close_tray_title.configure(text=self.t("sw_close_tray"))
        self._sw_close_tray_desc.configure(text=self.t("sw_close_tray_desc"))
        self._sw_warning_title.configure(text=self.t("sw_warning"))
        self._sw_warning_desc.configure(text=self.t("sw_warning_desc"))
        self._tray_guide_title_label.configure(text=self.t("tray_guide_title"))
        self._tray_guide_body_label.configure(text=self.t("tray_guide_body"))
        self._about_title_label.configure(text=self.t("about_title"))
        self._about_body_label.configure(text=self.t("about_body"))

    # ── UI Construction (NavigationView & Views) ──────────────────────────────

    def _build_fluent_layout(self) -> None:
        # Left Navigation Rail (WinUI 3 NavigationView)
        self._sidebar = ctk.CTkFrame(
            self,
            width=210,
            fg_color=BG_SIDEBAR,
            corner_radius=0,
            border_width=1,
            border_color=BORDER_DIVIDER,
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Right Content Canvas
        self._content_area = ctk.CTkFrame(
            self,
            fg_color=BG_APP,
            corner_radius=0,
        )
        self._content_area.pack(side="right", fill="both", expand=True)

        # Sidebar Header (App Name + Windows 11 Badge)
        header_box = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        header_box.pack(pady=(22, 24), padx=16, anchor="w", fill="x")

        # Subtle Accent Header Bar
        ctk.CTkLabel(
            header_box,
            text="Shutdown Scheduler",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_box,
            text="Windows 11 Edition",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(1, 0))

        # Navigation Menu Items
        self._nav_items = {}
        self._build_nav_item("timer", "nav_timer", icon_char="⏱")
        self._build_nav_item("schedule", "nav_schedule", icon_char="📅")
        self._build_nav_item("settings", "nav_settings", icon_char="⚙")

        # Sidebar Bottom Panel (Language Pill + Status Pill)
        bottom_box = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        bottom_box.pack(side="bottom", fill="x", padx=14, pady=16)

        # Segmented Language Toggle Pill [ TH | EN ]
        lang_card = ctk.CTkFrame(
            bottom_box,
            fg_color=CARD_ALT_BG,
            corner_radius=6,
            border_width=1,
            border_color=CARD_BORDER,
            height=32,
        )
        lang_card.pack(fill="x", pady=(0, 10))
        lang_card.pack_propagate(False)

        self._lang_btn_th = ctk.CTkButton(
            lang_card,
            text="ไทย (TH)",
            height=26,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            corner_radius=4,
            fg_color=BTN_SEC_BG,
            hover_color=BTN_SEC_HOVER,
            text_color=TEXT_PRIMARY,
            command=lambda: self._set_language("TH"),
        )
        self._lang_btn_th.pack(side="left", fill="both", expand=True, padx=(3, 1), pady=3)

        self._lang_btn_en = ctk.CTkButton(
            lang_card,
            text="English",
            height=26,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            corner_radius=4,
            fg_color="transparent",
            hover_color=BTN_SEC_HOVER,
            text_color=TEXT_SECONDARY,
            command=lambda: self._set_language("EN"),
        )
        self._lang_btn_en.pack(side="right", fill="both", expand=True, padx=(1, 3), pady=3)

        # Status Badge Pill
        status_box = ctk.CTkFrame(
            bottom_box,
            fg_color=CARD_ALT_BG,
            corner_radius=6,
            border_width=1,
            border_color=CARD_BORDER,
            height=32,
        )
        status_box.pack(fill="x")
        status_box.pack_propagate(False)

        status_inner = ctk.CTkFrame(status_box, fg_color="transparent")
        status_inner.pack(expand=True)

        self._status_dot = ctk.CTkLabel(
            status_inner,
            text="●",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=STATUS_READY,
        )
        self._status_dot.pack(side="left", padx=(0, 6))

        self._drawer_status_label = ctk.CTkLabel(
            status_inner,
            text="Ready",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
        )
        self._drawer_status_label.pack(side="left")

        # Build View Pages
        self._views = {
            "timer": self._create_timer_view(),
            "schedule": self._create_schedule_view(),
            "settings": self._create_settings_view(),
        }

        # Select initial page
        self._switch_page("timer")

    def _build_nav_item(self, key: str, text_key: str, icon_char: str) -> None:
        """Create a WinUI 3 Navigation View button with an active indicator strip."""
        item_frame = ctk.CTkFrame(
            self._sidebar,
            fg_color="transparent",
            corner_radius=6,
            height=38,
        )
        item_frame.pack(fill="x", padx=10, pady=2)
        item_frame.pack_propagate(False)

        # 3px Active Indicator Strip (WinUI 3 standard)
        indicator = ctk.CTkFrame(
            item_frame,
            width=3,
            corner_radius=2,
            fg_color="transparent",
        )
        indicator.pack(side="left", fill="y", padx=(2, 6), pady=6)

        # Navigation Button
        btn = ctk.CTkButton(
            item_frame,
            text=self.t(text_key),
            anchor="w",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            corner_radius=6,
            fg_color="transparent",
            hover_color=CARD_BG,
            text_color=TEXT_SECONDARY,
            command=lambda k=key: self._switch_page(k),
        )
        btn.pack(side="right", fill="both", expand=True)

        self._nav_items[key] = {
            "frame": item_frame,
            "indicator": indicator,
            "button": btn,
        }

        if key == "timer":
            self._nav_btn_timer = btn
        elif key == "schedule":
            self._nav_btn_sched = btn
        elif key == "settings":
            self._nav_btn_settings = btn

    def _switch_page(self, page_key: str) -> None:
        """Switch active page and update WinUI active indicator."""
        self._active_page = page_key

        # Switch Views
        for key, view in self._views.items():
            if key == page_key:
                view.pack(fill="both", expand=True, padx=26, pady=22)
            else:
                view.pack_forget()

        # Update Navigation Item Highlight
        for key, item in self._nav_items.items():
            if key == page_key:
                item["indicator"].configure(fg_color=ACCENT_BLUE)
                item["button"].configure(fg_color=CARD_BG, text_color=TEXT_PRIMARY)
            else:
                item["indicator"].configure(fg_color="transparent")
                item["button"].configure(fg_color="transparent", text_color=TEXT_SECONDARY)

    # ── Page 1: Timer View ────────────────────────────────────────────────────

    def _create_timer_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self._content_area, fg_color="transparent")

        # Header Section
        self._timer_title_label = ctk.CTkLabel(
            view,
            text=self.t("timer_title"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._timer_title_label.pack(anchor="w", pady=(0, 2))

        self._timer_desc_label = ctk.CTkLabel(
            view,
            text=self.t("timer_desc"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_SECONDARY,
        )
        self._timer_desc_label.pack(anchor="w", pady=(0, 16))

        # Hero Countdown Card (Digital Display)
        hero_card = ctk.CTkFrame(
            view,
            fg_color=CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=CARD_BORDER,
        )
        hero_card.pack(fill="x", pady=(0, 14))

        hero_inner = ctk.CTkFrame(hero_card, fg_color="transparent")
        hero_inner.pack(pady=16)

        self._countdown_label = ctk.CTkLabel(
            hero_inner,
            text="00 : 00 : 00",
            font=ctk.CTkFont(family=FONT_MONO, size=40, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._countdown_label.pack()

        self._timer_units_label = ctk.CTkLabel(
            hero_inner,
            text=self.t("time_labels"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=TEXT_MUTED,
        )
        self._timer_units_label.pack(pady=(4, 0))

        # Duration Stepper Card
        stepper_card = ctk.CTkFrame(
            view,
            fg_color=CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=CARD_BORDER,
        )
        stepper_card.pack(fill="x", pady=(0, 14))

        stepper_inner = ctk.CTkFrame(stepper_card, fg_color="transparent")
        stepper_inner.pack(pady=12)

        self._hr_spinner = FluentTimeSpinner(stepper_inner, label_text=self.t("spinner_hours"), min_val=0, max_val=23, initial=0)
        self._hr_spinner.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            stepper_inner,
            text=":",
            font=ctk.CTkFont(family=FONT_MONO, size=24, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=2, pady=(16, 0))

        self._min_spinner = FluentTimeSpinner(stepper_inner, label_text=self.t("spinner_minutes"), min_val=0, max_val=59, initial=0)
        self._min_spinner.pack(side="left", padx=(10, 10))

        ctk.CTkLabel(
            stepper_inner,
            text=":",
            font=ctk.CTkFont(family=FONT_MONO, size=24, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=2, pady=(16, 0))

        self._sec_spinner = FluentTimeSpinner(stepper_inner, label_text=self.t("spinner_seconds"), min_val=0, max_val=59, initial=0)
        self._sec_spinner.pack(side="left", padx=(10, 0))

        # Quick Preset Chips
        preset_frame = ctk.CTkFrame(view, fg_color="transparent")
        preset_frame.pack(fill="x", pady=(0, 16), anchor="w")

        presets = [
            ("15 min", 0, 15, 0),
            ("30 min", 0, 30, 0),
            ("1 hour", 1, 0, 0),
            ("2 hours", 2, 0, 0),
        ]

        self._preset_btns = []
        for label, h, m, s in presets:
            btn = ctk.CTkButton(
                preset_frame,
                text=label,
                width=84,
                height=30,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                corner_radius=6,
                fg_color=CARD_BG,
                hover_color=BTN_SEC_HOVER,
                border_width=1,
                border_color=CARD_BORDER,
                text_color=TEXT_PRIMARY,
                command=lambda hh=h, mm=m, ss=s: self._apply_preset(hh, mm, ss),
            )
            btn.pack(side="left", padx=(0, 8))
            self._preset_btns.append(btn)

        # Action Buttons Row
        action_row = ctk.CTkFrame(view, fg_color="transparent")
        action_row.pack(anchor="w")

        # WinUI 3 Primary Accent Button
        self._start_btn = ctk.CTkButton(
            action_row,
            text=self.t("btn_start"),
            width=160,
            height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            corner_radius=6,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_HOVER,
            text_color="#ffffff",
            command=self._on_start_timer,
        )
        self._start_btn.pack(side="left", padx=(0, 10))

        # Secondary / Cancel Button
        self._cancel_btn = ctk.CTkButton(
            action_row,
            text=self.t("btn_cancel"),
            width=100,
            height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            corner_radius=6,
            fg_color=CARD_BG,
            hover_color=BTN_SEC_HOVER,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=TEXT_MUTED,
            state="disabled",
            command=self._on_cancel,
        )
        self._cancel_btn.pack(side="left")

        return view

    # ── Page 2: Schedule View ─────────────────────────────────────────────────

    def _create_schedule_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self._content_area, fg_color="transparent")

        # Header Section
        self._sched_title_label = ctk.CTkLabel(
            view,
            text=self.t("sched_title"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._sched_title_label.pack(anchor="w", pady=(0, 2))

        self._sched_desc_label = ctk.CTkLabel(
            view,
            text=self.t("sched_desc"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_SECONDARY,
        )
        self._sched_desc_label.pack(anchor="w", pady=(0, 16))

        # Clock Target Picker Card
        clock_card = ctk.CTkFrame(
            view,
            fg_color=CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=CARD_BORDER,
        )
        clock_card.pack(fill="x", pady=(0, 14))

        clock_inner = ctk.CTkFrame(clock_card, fg_color="transparent")
        clock_inner.pack(pady=12)

        now = datetime.now()

        self._sched_hr_spinner = FluentTimeSpinner(
            clock_inner,
            label_text=self.t("target_hr"),
            min_val=0,
            max_val=23,
            initial=now.hour,
        )
        self._sched_hr_spinner.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            clock_inner,
            text=":",
            font=ctk.CTkFont(family=FONT_MONO, size=24, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=2, pady=(16, 0))

        self._sched_min_spinner = FluentTimeSpinner(
            clock_inner,
            label_text=self.t("target_min"),
            min_val=0,
            max_val=59,
            initial=now.minute,
        )
        self._sched_min_spinner.pack(side="left", padx=(12, 0))

        # Windows 11 Settings-Style Card: Daily Repeat
        daily_card = ctk.CTkFrame(
            view,
            fg_color=CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=CARD_BORDER,
        )
        daily_card.pack(fill="x", pady=(0, 14))

        daily_inner = ctk.CTkFrame(daily_card, fg_color="transparent")
        daily_inner.pack(fill="x", padx=16, pady=12)

        daily_text_col = ctk.CTkFrame(daily_inner, fg_color="transparent")
        daily_text_col.pack(side="left", fill="both", expand=True)

        self._daily_repeat_title = ctk.CTkLabel(
            daily_text_col,
            text=self.t("daily_repeat"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._daily_repeat_title.pack(anchor="w")

        self._daily_repeat_desc = ctk.CTkLabel(
            daily_text_col,
            text=self.t("daily_repeat_desc"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_SECONDARY,
        )
        self._daily_repeat_desc.pack(anchor="w")

        self._daily_repeat_switch = ctk.CTkSwitch(
            daily_inner,
            text="",
            width=46,
            progress_color=ACCENT_BLUE,
            button_color="#ffffff",
            button_hover_color="#f0f0f0",
            variable=self._daily_repeat_var,
        )
        self._daily_repeat_switch.pack(side="right")

        # InfoBar / Schedule Status Card
        self._sched_info_card = ctk.CTkFrame(
            view,
            fg_color=CARD_ALT_BG,
            corner_radius=6,
            border_width=1,
            border_color=CARD_BORDER,
        )
        self._sched_info_card.pack(fill="x", pady=(0, 16))

        self._sched_info_label = ctk.CTkLabel(
            self._sched_info_card,
            text=self.t("sched_info"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_SECONDARY,
            pady=10,
            padx=14,
        )
        self._sched_info_label.pack(anchor="w")

        # Action Buttons Row
        action_row = ctk.CTkFrame(view, fg_color="transparent")
        action_row.pack(anchor="w")

        self._sched_start_btn = ctk.CTkButton(
            action_row,
            text=self.t("btn_set_sched"),
            width=180,
            height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            corner_radius=6,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_HOVER,
            text_color="#ffffff",
            command=self._on_start_schedule,
        )
        self._sched_start_btn.pack(side="left", padx=(0, 10))

        self._sched_cancel_btn = ctk.CTkButton(
            action_row,
            text=self.t("btn_cancel"),
            width=100,
            height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            corner_radius=6,
            fg_color=CARD_BG,
            hover_color=BTN_SEC_HOVER,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=TEXT_MUTED,
            state="disabled",
            command=self._on_cancel,
        )
        self._sched_cancel_btn.pack(side="left")

        return view

    # ── Page 3: Settings View ─────────────────────────────────────────────────

    def _create_settings_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self._content_area, fg_color="transparent")

        # Header Section
        self._settings_title_label = ctk.CTkLabel(
            view,
            text=self.t("settings_title"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._settings_title_label.pack(anchor="w", pady=(0, 2))

        self._settings_desc_label = ctk.CTkLabel(
            view,
            text=self.t("settings_desc"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_SECONDARY,
        )
        self._settings_desc_label.pack(anchor="w", pady=(0, 16))

        # Settings Card 1: Close to System Tray
        card1 = ctk.CTkFrame(
            view,
            fg_color=CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=CARD_BORDER,
        )
        card1.pack(fill="x", pady=(0, 10))

        inner1 = ctk.CTkFrame(card1, fg_color="transparent")
        inner1.pack(fill="x", padx=16, pady=12)

        c1_text = ctk.CTkFrame(inner1, fg_color="transparent")
        c1_text.pack(side="left", fill="both", expand=True)

        self._sw_close_tray_title = ctk.CTkLabel(
            c1_text,
            text=self.t("sw_close_tray"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._sw_close_tray_title.pack(anchor="w")

        self._sw_close_tray_desc = ctk.CTkLabel(
            c1_text,
            text=self.t("sw_close_tray_desc"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_SECONDARY,
        )
        self._sw_close_tray_desc.pack(anchor="w")

        self._sw_close_tray = ctk.CTkSwitch(
            inner1,
            text="",
            width=46,
            progress_color=ACCENT_BLUE,
            button_color="#ffffff",
            button_hover_color="#f0f0f0",
            variable=self._close_to_tray_var,
        )
        self._sw_close_tray.pack(side="right")

        # Settings Card 2: 5-minute Warning Alert
        card2 = ctk.CTkFrame(
            view,
            fg_color=CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=CARD_BORDER,
        )
        card2.pack(fill="x", pady=(0, 14))

        inner2 = ctk.CTkFrame(card2, fg_color="transparent")
        inner2.pack(fill="x", padx=16, pady=12)

        c2_text = ctk.CTkFrame(inner2, fg_color="transparent")
        c2_text.pack(side="left", fill="both", expand=True)

        self._sw_warning_title = ctk.CTkLabel(
            c2_text,
            text=self.t("sw_warning"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._sw_warning_title.pack(anchor="w")

        self._sw_warning_desc = ctk.CTkLabel(
            c2_text,
            text=self.t("sw_warning_desc"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_SECONDARY,
        )
        self._sw_warning_desc.pack(anchor="w")

        self._sw_warning = ctk.CTkSwitch(
            inner2,
            text="",
            width=46,
            progress_color=ACCENT_BLUE,
            button_color="#ffffff",
            button_hover_color="#f0f0f0",
            variable=self._enable_warning_var,
        )
        self._sw_warning.pack(side="right")

        # Tray Guide Card
        info_card = ctk.CTkFrame(
            view,
            fg_color=CARD_ALT_BG,
            corner_radius=8,
            border_width=1,
            border_color=CARD_BORDER,
        )
        info_card.pack(fill="x", pady=(0, 10))

        self._tray_guide_title_label = ctk.CTkLabel(
            info_card,
            text=self.t("tray_guide_title"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._tray_guide_title_label.pack(anchor="w", padx=14, pady=(12, 2))

        self._tray_guide_body_label = ctk.CTkLabel(
            info_card,
            text=self.t("tray_guide_body"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_SECONDARY,
            justify="left",
        )
        self._tray_guide_body_label.pack(anchor="w", padx=14, pady=(0, 12))

        # About Card
        about_card = ctk.CTkFrame(
            view,
            fg_color=CARD_ALT_BG,
            corner_radius=6,
            border_width=1,
            border_color=CARD_BORDER,
        )
        about_card.pack(fill="x")

        self._about_title_label = ctk.CTkLabel(
            about_card,
            text=self.t("about_title"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._about_title_label.pack(anchor="w", padx=14, pady=(8, 1))

        self._about_body_label = ctk.CTkLabel(
            about_card,
            text=self.t("about_body"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=TEXT_MUTED,
        )
        self._about_body_label.pack(anchor="w", padx=14, pady=(0, 8))

        return view

    # ── System Tray ───────────────────────────────────────────────────────────

    def _setup_tray_icon(self) -> None:
        menu = pystray.Menu(
            pystray.MenuItem(self.t("tray_open"), self._restore_window_from_tray, default=True),
            pystray.MenuItem(self.t("tray_time"), self._tray_show_status),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(self.t("tray_cancel"), self._tray_cancel_shutdown),
            pystray.MenuItem(self.t("tray_exit"), self._quit_app),
        )

        self._tray_image = create_fluent_tray_image()
        self._tray_icon = pystray.Icon(
            "ShutdownScheduler",
            self._tray_image,
            "Shutdown Scheduler",
            menu,
        )

        self._tray_thread = threading.Thread(target=self._tray_icon.run, daemon=True)
        self._tray_thread.start()

    def _restore_window_from_tray(self, icon=None, item=None) -> None:
        self.after(0, self._do_restore_window)

    def _do_restore_window(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()

    def _hide_to_tray(self) -> None:
        self.withdraw()

    def _on_window_close(self) -> None:
        if self._close_to_tray_var.get() or self._is_running:
            self._hide_to_tray()
        else:
            self._quit_app()

    def _tray_show_status(self, icon=None, item=None) -> None:
        if self._is_running:
            h, rem = divmod(self._remaining, 3600)
            m, s = divmod(rem, 60)
            msg = f"Remaining time: {h:02d}:{m:02d}:{s:02d}"
        else:
            msg = "No shutdown timer running."

        try:
            self._tray_icon.notify(msg, "Shutdown Scheduler")
        except Exception:
            pass

    def _tray_cancel_shutdown(self, icon=None, item=None) -> None:
        self.after(0, self._on_cancel)

    def _quit_app(self, icon=None, item=None) -> None:
        self.after(0, self._do_quit_app)

    def _do_quit_app(self) -> None:
        self._abort_shutdown()
        try:
            if hasattr(self, "_tray_icon") and self._tray_icon:
                self._tray_icon.stop()
        except Exception:
            pass
        self.destroy()
        sys.exit(0)

    # ── Actions & Countdown Handlers ──────────────────────────────────────────

    def _apply_preset(self, h: int, m: int, s: int) -> None:
        if self._is_running:
            return
        self._hr_spinner.value = h
        self._min_spinner.value = m
        self._sec_spinner.value = s

    def _on_start_timer(self) -> None:
        h = self._hr_spinner.value
        m = self._min_spinner.value
        s = self._sec_spinner.value
        total = h * 3600 + m * 60 + s

        if total <= 0:
            messagebox.showwarning("Shutdown Scheduler", self.t("invalid_time_msg"))
            return

        self._start_countdown(total)

    def _on_start_schedule(self) -> None:
        target_h = self._sched_hr_spinner.value
        target_m = self._sched_min_spinner.value

        now = datetime.now()
        target_dt = now.replace(hour=target_h, minute=target_m, second=0, microsecond=0)

        if target_dt <= now:
            target_dt += timedelta(days=1)

        diff_seconds = int((target_dt - now).total_seconds())

        if diff_seconds <= 0:
            messagebox.showwarning("Shutdown Scheduler", self.t("invalid_time_msg"))
            return

        self._schedule_target_dt = target_dt
        dt_str = target_dt.strftime("%H:%M (%d/%m)")
        self._sched_info_label.configure(
            text=self.t("sched_target_banner", time=dt_str),
            text_color=TEXT_PRIMARY,
        )

        self._start_countdown(diff_seconds)

    def _start_countdown(self, seconds: int) -> None:
        self._remaining = seconds
        self._is_running = True
        self._warning_shown = False

        self._start_btn.configure(state="disabled")
        self._sched_start_btn.configure(state="disabled")

        # Enable Cancel Buttons with Subdued Danger Styling
        self._cancel_btn.configure(
            state="normal",
            fg_color=BTN_CANCEL_BG,
            hover_color=BTN_CANCEL_HOVER,
            border_color=BTN_CANCEL_BORDER,
            text_color=BTN_CANCEL_TEXT,
        )
        self._sched_cancel_btn.configure(
            state="normal",
            fg_color=BTN_CANCEL_BG,
            hover_color=BTN_CANCEL_HOVER,
            border_color=BTN_CANCEL_BORDER,
            text_color=BTN_CANCEL_TEXT,
        )

        self._hr_spinner.set_state("disabled")
        self._min_spinner.set_state("disabled")
        self._sec_spinner.set_state("disabled")
        self._sched_hr_spinner.set_state("disabled")
        self._sched_min_spinner.set_state("disabled")

        self._status_dot.configure(text_color=STATUS_BUSY)
        self._drawer_status_label.configure(text=self.t("status_running"), text_color=TEXT_PRIMARY)
        self._countdown_label.configure(text_color=TEXT_ACCENT)

        self._tick()

    def _on_cancel(self) -> None:
        self._abort_shutdown()
        self._reset_ui()

    def _abort_shutdown(self) -> None:
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None

        self._is_running = False

        os_name = platform.system()
        try:
            if os_name == "Windows":
                subprocess.run(["shutdown", "/a"], creationflags=subprocess.CREATE_NO_WINDOW, check=False)
            elif os_name == "Darwin":
                subprocess.run(["sudo", "killall", "shutdown"], check=False)
            else:
                subprocess.run(["shutdown", "-c"], check=False)
        except Exception:
            pass

    def _reset_ui(self) -> None:
        self._countdown_label.configure(text="00 : 00 : 00", text_color=TEXT_PRIMARY)
        self._start_btn.configure(state="normal")
        self._sched_start_btn.configure(state="normal")

        # Disable Cancel Buttons
        self._cancel_btn.configure(
            state="disabled",
            fg_color=CARD_BG,
            hover_color=BTN_SEC_HOVER,
            border_color=CARD_BORDER,
            text_color=TEXT_MUTED,
        )
        self._sched_cancel_btn.configure(
            state="disabled",
            fg_color=CARD_BG,
            hover_color=BTN_SEC_HOVER,
            border_color=CARD_BORDER,
            text_color=TEXT_MUTED,
        )

        self._hr_spinner.set_state("normal")
        self._min_spinner.set_state("normal")
        self._sec_spinner.set_state("normal")
        self._sched_hr_spinner.set_state("normal")
        self._sched_min_spinner.set_state("normal")

        self._status_dot.configure(text_color=STATUS_READY)
        self._drawer_status_label.configure(text=self.t("status_ready"), text_color=TEXT_SECONDARY)
        self._sched_info_label.configure(text=self.t("sched_info"), text_color=TEXT_SECONDARY)

        if hasattr(self, "_tray_icon") and self._tray_icon:
            self._tray_icon.title = "Shutdown Scheduler"

    # ── Countdown Tick ────────────────────────────────────────────────────────

    def _tick(self) -> None:
        if not self._is_running:
            return

        h, rem = divmod(self._remaining, 3600)
        m, s = divmod(rem, 60)
        display = f"{h:02d} : {m:02d} : {s:02d}"

        self._countdown_label.configure(text=display, text_color=TEXT_ACCENT)

        if hasattr(self, "_tray_icon") and self._tray_icon:
            self._tray_icon.title = f"Shutdown in {h:02d}:{m:02d}:{s:02d}"

        # 5-minute pre-shutdown alert
        if self._remaining == 300 and not self._warning_shown and self._enable_warning_var.get():
            self._warning_shown = True
            self._show_warning_dialog()

        if self._remaining <= 0:
            self._trigger_shutdown()
            return

        self._remaining -= 1
        self._timer_id = self.after(1000, self._tick)

    # ── Pre-Shutdown Warning Dialog (Windows 11 Native Modal) ─────────────────

    def _show_warning_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.t("warning_dialog_title"))
        dialog.geometry("450x220")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG_APP)
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        # Apply Windows 11 DWM Styling to Dialog
        apply_windows_11_styling(dialog)

        dialog.update_idletasks()
        x = self.winfo_x() + (self.WIDTH - 450) // 2
        y = self.winfo_y() + (self.HEIGHT - 220) // 2
        dialog.geometry(f"+{x}+{y}")

        content_box = ctk.CTkFrame(dialog, fg_color="transparent")
        content_box.pack(padx=24, pady=24, fill="both", expand=True)

        ctk.CTkLabel(
            content_box,
            text=self.t("warning_dialog_title"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(0, 8), anchor="w")

        ctk.CTkLabel(
            content_box,
            text=self.t("warning_dialog_msg"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_SECONDARY,
            justify="left",
        ).pack(pady=(0, 20), anchor="w")

        def cancel_from_dialog():
            dialog.destroy()
            self._on_cancel()

        btn_row = ctk.CTkFrame(content_box, fg_color="transparent")
        btn_row.pack(anchor="e")

        ctk.CTkButton(
            btn_row,
            text=self.t("warning_btn_cancel"),
            width=160,
            height=34,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            corner_radius=6,
            fg_color=BTN_DANGER_BG,
            hover_color=BTN_DANGER_HOVER,
            text_color=BTN_DANGER_TEXT,
            command=cancel_from_dialog,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row,
            text=self.t("warning_btn_ok"),
            width=100,
            height=34,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            corner_radius=6,
            fg_color=CARD_BG,
            hover_color=BTN_SEC_HOVER,
            border_width=1,
            border_color=CARD_BORDER,
            text_color=TEXT_PRIMARY,
            command=dialog.destroy,
        ).pack(side="left")

    def _trigger_shutdown(self) -> None:
        self._is_running = False

        if self._daily_repeat_var.get() and self._schedule_target_dt:
            self._schedule_target_dt += timedelta(days=1)

        os_name = platform.system()
        try:
            if os_name == "Windows":
                subprocess.Popen(["shutdown", "/s", "/t", "0"], creationflags=subprocess.CREATE_NO_WINDOW)
            elif os_name == "Darwin":
                subprocess.Popen(["sudo", "shutdown", "-h", "now"])
            else:
                subprocess.Popen(["shutdown", "-h", "now"])
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to execute shutdown command:\n{exc}")
            self._reset_ui()


# ─── Program Entry Point ──────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ShutdownSchedulerApp()
    app.mainloop()
