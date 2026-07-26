"""
Shutdown Scheduler v4.0 (Hand-Drawn UI & Bilingual Edition)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A cozy hand-drawn sketchy Windows desktop app with TH/EN language support.
Built with Python + CustomTkinter + PyStray.

Features:
  • Hand-Drawn / Sketchy Aesthetic (Strokes, Ink & Handwritten Fonts)
  • Bilingual Live Switcher (🇹🇭 ไทย / 🇬🇧 English)
  • Left Navigation Drawer (Timer / Schedule / Settings)
  • Dual Modes: Countdown Timer & Specific Clock Schedule
  • System Tray Integration (Runs in background under "Show hidden icons")
"""

import sys
import platform
import subprocess
import threading
from datetime import datetime, timedelta
import customtkinter as ctk
from tkinter import messagebox

import pystray
from PIL import Image, ImageDraw


# ─── Font Selection (Safe System Default - No Copyright Issues) ─────────────

HAND_FONT = None  
BODY_FONT = None  


# ─── Color Palette (Hand-Drawn Pencil & Chalkboard) ───────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_MAIN          = "#161618"  # Slate Chalkboard Dark
SIDEBAR_BG       = "#1e1e22"  # Sketched Drawer Background
CARD_BG          = "#242428"  # Sketched Paper Card
CARD_INNER       = "#2c2c32"  # Inner Pen Surface
BORDER_CLR       = "#48484a"  # Hand-drawn Pen Stroke Border
BORDER_ACTIVE    = "#636366"

TEXT_PRIMARY     = "#f2f2f7"  # Clean Chalk White
TEXT_SECONDARY   = "#aeaeb2"  # Pencil Slate Gray
TEXT_MUTED       = "#7c7c80"  # Muted Graphite

BTN_WHITE_BG     = "#f2f2f7"  # Solid Chalk White Button
BTN_WHITE_TEXT   = "#1c1c1e"  # Dark Ink Text
BTN_WHITE_HOVER  = "#e5e5ea"

BTN_DARK_BG      = "#2c2c30"  # Dark Paper Button
BTN_DARK_HOVER   = "#3a3a40"

BTN_DANGER_BG    = "#3d2022"  # Sketched Terracotta Red Tint
BTN_DANGER_TEXT  = "#ff6b6b"  # Terracotta Red Text
BTN_DANGER_HOVER = "#522629"


# ─── Bilingual Dictionary System (TH ↔ EN) ─────────────────────────────────────

TRANSLATIONS = {
    "TH": {
        "title": "SHUTDOWN",
        "subtitle": "SCHEDULER ✎",
        "nav_timer": "✎ นับถอยหลัง",
        "nav_schedule": "📅 ตั้งเวลาเฉพาะ",
        "nav_settings": "⚙ ตั้งค่าระบบ",
        "status_ready": "● พร้อมใช้งาน",
        "status_running": "● กำลังทำงาน",
        "timer_title": "✏️ นับถอยหลังปิดเครื่อง",
        "timer_desc": "เลือกจำนวนชั่วโมง นาที และวินาทีสำหรับนับถอยหลัง",
        "spinner_hours": "ชั่วโมง",
        "spinner_minutes": "นาที",
        "spinner_seconds": "วินาที",
        "preset_15m": "15 นาที",
        "preset_30m": "30 นาที",
        "preset_1h": "1 ชม.",
        "preset_2h": "2 ชม.",
        "btn_start": "▶ เริ่มนับถอยหลัง",
        "btn_cancel": "✕ ยกเลิก",
        "btn_hide": "📌 ซ่อนลง TRAY",
        "sched_title": "📅 ตั้งเวลาตามนาฬิกา",
        "sched_desc": "ระบุเวลาเป้าหมาย (เช่น 23:30 น.) ระบบจะนับถอยหลังให้อัตโนมัติ",
        "target_hr": "ชั่วโมง (0-23)",
        "target_min": "นาที (0-59)",
        "sched_info": "💡 ระบบจะคำนวณเวลาคงเหลือให้อัตโนมัติ",
        "sched_target_banner": "⏰ ตั้งเวลาแล้ว: จะปิดเครื่องเวลา {time}",
        "daily_repeat": "🔁 ทำงานซ้ำทุกวัน (Daily Schedule)",
        "btn_set_sched": "⏰ ตั้งเวลาปิดเครื่อง",
        "settings_title": "⚙ ตั้งค่าระบบ & ถาดซ่อน",
        "settings_desc": "ปรับแต่งการทำงานเบื้องหลังและการแจ้งเตือน",
        "sw_close_tray": "📌 ย่อลง System Tray เมื่อกดปิดหน้าต่าง (X)",
        "sw_warning": "🔔 แสดงป๊อปอัปแจ้งเตือนก่อนปิดเครื่อง 5 นาที",
        "tray_guide_title": "✏️ คำแนะนำการทำงานเบื้องหลัง:",
        "tray_guide_body": "• แอปจะรันเบื้องหลังใต้ 'Show hidden icons' (ขวาล่าง)\n• คลิกขวาที่ไอคอนถาดระบบเพื่อดูเวลาคงเหลือ หรือดึงหน้าต่างกลับมาได้ตลอดเวลา\n• หากต้องการปิดแอปถาวร ให้คลิกขวาแล้วเลือก 'Exit / ออกจากโปรแกรม'",
        "warning_dialog_title": "⚠️ แจ้งเตือนปิดเครื่อง",
        "warning_dialog_msg": "คอมพิวเตอร์จะปิดตัวลงในอีก 5 นาที!\nกรุณาบันทึกงานของคุณให้เรียบร้อย ✏️",
        "warning_btn_cancel": "🛑 ยกเลิกปิดเครื่อง",
        "warning_btn_ok": "👍 ตกลง, รับทราบ",
        "tray_open": "🌸 เปิดหน้าต่างหลัก",
        "tray_time": "⏱ เวลาคงเหลือ",
        "tray_cancel": "🛑 ยกเลิกการปิดเครื่อง",
        "tray_exit": "❌ ออกจากโปรแกรม",
        "invalid_time_msg": "กรุณาเลือกเวลาปิดเครื่องอย่างน้อย 1 วินาทีขึ้นไป",
    },
    "EN": {
        "title": "SHUTDOWN",
        "subtitle": "SCHEDULER ✎",
        "nav_timer": "✎ Timer",
        "nav_schedule": "📅 Schedule",
        "nav_settings": "⚙ Settings",
        "status_ready": "● READY",
        "status_running": "● RUNNING",
        "timer_title": "✏️ Countdown Timer",
        "timer_desc": "Set hours, minutes and seconds to schedule system shutdown.",
        "spinner_hours": "HOURS",
        "spinner_minutes": "MINUTES",
        "spinner_seconds": "SECONDS",
        "preset_15m": "15M",
        "preset_30m": "30M",
        "preset_1h": "1H",
        "preset_2h": "2H",
        "btn_start": "▶ START",
        "btn_cancel": "✕ CANCEL",
        "btn_hide": "📌 HIDE TO TRAY",
        "sched_title": "📅 Clock Schedule",
        "sched_desc": "Specify exact clock time to trigger automatic system shutdown.",
        "target_hr": "TARGET HOUR (24H)",
        "target_min": "TARGET MINUTE",
        "sched_info": "💡 Target countdown will calculate automatically.",
        "sched_target_banner": "⏰ Schedule set for {time}",
        "daily_repeat": "🔁 Daily Repeat Schedule",
        "btn_set_sched": "⏰ SET SCHEDULE",
        "settings_title": "⚙ System Settings",
        "settings_desc": "Configure background behavior and warning popups.",
        "sw_close_tray": "📌 Minimize to System Tray on window close (X)",
        "sw_warning": "🔔 Show 5-minute pre-shutdown warning popup",
        "tray_guide_title": "✏️ System Tray Guide:",
        "tray_guide_body": "• App stays active under 'Show hidden icons' in the taskbar.\n• Right-click tray icon to check remaining time or cancel pending shutdown.\n• To exit completely, choose 'Exit' from the tray menu.",
        "warning_dialog_title": "⚠️ Shutdown Warning",
        "warning_dialog_msg": "The computer will shut down in 5 minutes.\nPlease save your work ✏️",
        "warning_btn_cancel": "🛑 CANCEL SHUTDOWN",
        "warning_btn_ok": "👍 OK",
        "tray_open": "🌸 Open Main Window",
        "tray_time": "⏱ Remaining Time",
        "tray_cancel": "🛑 Cancel Shutdown",
        "tray_exit": "❌ Exit",
        "invalid_time_msg": "Please select a duration of at least 1 second.",
    }
}


# ─── Helper: Hand-Drawn Sketched System Tray Icon ─────────────────────────────

def create_handdrawn_tray_image(width=64, height=64) -> Image.Image:
    """Generate a hand-drawn sketched icon for the System Tray."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Sketched circle background with pen strokes
    draw.ellipse((4, 4, width - 4, height - 4), fill=(30, 30, 34, 255), outline=(242, 242, 247, 255), width=3)

    # Inner sketched clock/power symbol
    draw.ellipse((20, 20, 44, 44), outline=(242, 242, 247, 255), width=2)
    draw.line((32, 14, 32, 28), fill=(242, 242, 247, 255), width=3)

    return img


# ─── Time Spinner Widget (Hand-Drawn Sketched Style) ──────────────────────────

class TimeSpinner(ctk.CTkFrame):
    """A hand-drawn sketched time spinner widget."""

    def __init__(
        self,
        master,
        label_key: str,
        min_val: int = 0,
        max_val: int = 59,
        initial: int = 0,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._min = min_val
        self._max = max_val
        self._value = initial
        self._label_key = label_key

        # Header Label
        self._title_label = ctk.CTkLabel(
            self,
            text=label_key,
            font=ctk.CTkFont(family=BODY_FONT, size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
        )
        self._title_label.pack(pady=(0, 4))

        # Container sketched card with 2px stroke border
        card = ctk.CTkFrame(
            self,
            fg_color=CARD_INNER,
            corner_radius=10,
            border_width=2,
            border_color=BORDER_CLR,
        )
        card.pack()

        # ▲ Up Button
        self._up_btn = ctk.CTkButton(
            card,
            text="▲",
            width=72,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            fg_color=BTN_DARK_BG,
            hover_color=BTN_DARK_HOVER,
            border_width=1,
            border_color=BORDER_CLR,
            text_color=TEXT_PRIMARY,
            command=self._increment,
        )
        self._up_btn.pack(padx=6, pady=(6, 2))

        # Value Display
        self._display = ctk.CTkLabel(
            card,
            text=f"{self._value:02d}",
            font=ctk.CTkFont(family="Consolas", size=36, weight="bold"),
            text_color=TEXT_PRIMARY,
            width=72,
        )
        self._display.pack(padx=6, pady=(2, 2))

        # ▼ Down Button
        self._down_btn = ctk.CTkButton(
            card,
            text="▼",
            width=72,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            fg_color=BTN_DARK_BG,
            hover_color=BTN_DARK_HOVER,
            border_width=1,
            border_color=BORDER_CLR,
            text_color=TEXT_PRIMARY,
            command=self._decrement,
        )
        self._down_btn.pack(padx=6, pady=(2, 6))

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
        dim = TEXT_MUTED if state == "disabled" else TEXT_PRIMARY
        self._display.configure(text_color=dim)

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


# ─── Main Application (Hand-Drawn & Bilingual) ────────────────────────────────

class ShutdownSchedulerApp(ctk.CTk):
    """Hand-Drawn Sketched Desktop App with TH/EN Language Support."""

    WIDTH  = 700
    HEIGHT = 500

    def __init__(self) -> None:
        super().__init__()

        # Window Setup
        self.title("Shutdown Scheduler ✎")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)

        # Internal State
        self._lang = "TH"  # Default Language: TH (Thai)
        self._remaining: int = 0
        self._timer_id: str | None = None
        self._is_running: bool = False
        self._warning_shown: bool = False
        self._schedule_target_dt: datetime | None = None
        self._active_page: str = "timer"

        # Settings variables
        self._close_to_tray_var = ctk.BooleanVar(value=True)
        self._enable_warning_var = ctk.BooleanVar(value=True)
        self._daily_repeat_var = ctk.BooleanVar(value=False)

        # Window Protocol for Tray
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Build Layout (Left Drawer + Right Content Panel)
        self._build_drawer_layout()

        # Setup System Tray Icon
        self._setup_tray_icon()

        # Apply Initial Language Texts
        self._apply_language_texts()

    # ── Language Helper ──────────────────────────────────────────────────────

    def t(self, key: str, **kwargs) -> str:
        """Get translated text string by key."""
        lang_dict = TRANSLATIONS.get(self._lang, TRANSLATIONS["EN"])
        val = lang_dict.get(key, key)
        if kwargs:
            val = val.format(**kwargs)
        return val

    def _toggle_language(self) -> None:
        """Toggle between Thai (TH) and English (EN)."""
        self._lang = "EN" if self._lang == "TH" else "TH"
        self._apply_language_texts()

    def _apply_language_texts(self) -> None:
        """Dynamically refresh all UI texts to the selected language."""
        # Drawer Status
        status_key = "status_running" if self._is_running else "status_ready"
        self._drawer_status_label.configure(text=self.t(status_key))
        self._lang_btn.configure(text=f"🌐 {self._lang}")

        # Navigation drawer buttons
        self._nav_buttons["timer"].configure(text=self.t("nav_timer"))
        self._nav_buttons["schedule"].configure(text=self.t("nav_schedule"))
        self._nav_buttons["settings"].configure(text=self.t("nav_settings"))

        # Timer View
        self._timer_title_label.configure(text=self.t("timer_title"))
        self._timer_desc_label.configure(text=self.t("timer_desc"))
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
        self._daily_repeat_switch.configure(text=self.t("daily_repeat"))
        self._sched_start_btn.configure(text=self.t("btn_set_sched"))

        if not self._is_running:
            self._sched_info_label.configure(text=self.t("sched_info"))

        # Settings View
        self._settings_title_label.configure(text=self.t("settings_title"))
        self._settings_desc_label.configure(text=self.t("settings_desc"))
        self._sw_close_tray.configure(text=self.t("sw_close_tray"))
        self._sw_warning.configure(text=self.t("sw_warning"))
        self._tray_guide_title_label.configure(text=self.t("tray_guide_title"))
        self._tray_guide_body_label.configure(text=self.t("tray_guide_body"))

    # ── Drawer & Layout Construction ──────────────────────────────────────────

    def _build_drawer_layout(self) -> None:
        # Left Drawer Sidebar with Hand-drawn 2px border
        self._drawer = ctk.CTkFrame(
            self,
            width=190,
            fg_color=SIDEBAR_BG,
            corner_radius=0,
            border_width=2,
            border_color=BORDER_CLR,
        )
        self._drawer.pack(side="left", fill="y")
        self._drawer.pack_propagate(False)

        # Right Main Content Area
        self._content_area = ctk.CTkFrame(
            self,
            fg_color=BG_MAIN,
            corner_radius=0,
        )
        self._content_area.pack(side="right", fill="both", expand=True)

        # Drawer Title Frame
        title_frame = ctk.CTkFrame(self._drawer, fg_color="transparent")
        title_frame.pack(pady=(20, 20), padx=16, anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="SHUTDOWN",
            font=ctk.CTkFont(family=HAND_FONT, size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text="SCHEDULER ✎",
            font=ctk.CTkFont(family=BODY_FONT, size=11, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        # Navigation Drawer Buttons
        self._nav_buttons = {}
        nav_items = [
            ("timer", "nav_timer"),
            ("schedule", "nav_schedule"),
            ("settings", "nav_settings"),
        ]

        for key, text_key in nav_items:
            btn = ctk.CTkButton(
                self._drawer,
                text=self.t(text_key),
                anchor="w",
                width=158,
                height=38,
                font=ctk.CTkFont(family=BODY_FONT, size=12, weight="bold"),
                corner_radius=8,
                fg_color="transparent",
                hover_color=CARD_BG,
                text_color=TEXT_SECONDARY,
                command=lambda k=key: self._switch_page(k),
            )
            btn.pack(pady=4, padx=16)
            self._nav_buttons[key] = btn

        # Drawer Bottom Container (Language Switcher + Status)
        bottom_box = ctk.CTkFrame(
            self._drawer,
            fg_color="transparent",
        )
        bottom_box.pack(side="bottom", fill="x", padx=14, pady=16)

        # Language Switcher Button
        self._lang_btn = ctk.CTkButton(
            bottom_box,
            text="🌐 TH",
            width=160,
            height=32,
            font=ctk.CTkFont(family=BODY_FONT, size=12, weight="bold"),
            corner_radius=8,
            fg_color=CARD_BG,
            hover_color=BTN_DARK_HOVER,
            border_width=1,
            border_color=BORDER_CLR,
            text_color=TEXT_PRIMARY,
            command=self._toggle_language,
        )
        self._lang_btn.pack(pady=(0, 8))

        # Status badge box
        status_box = ctk.CTkFrame(
            bottom_box,
            fg_color=CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_CLR,
        )
        status_box.pack(fill="x")

        self._drawer_status_label = ctk.CTkLabel(
            status_box,
            text="● Ready",
            font=ctk.CTkFont(family=BODY_FONT, size=11, weight="bold"),
            text_color=TEXT_SECONDARY,
            pady=6,
        )
        self._drawer_status_label.pack()

        # Build Content Views
        self._views = {}
        self._views["timer"] = self._create_timer_view()
        self._views["schedule"] = self._create_schedule_view()
        self._views["settings"] = self._create_settings_view()

        self._switch_page("timer")

    def _switch_page(self, page_key: str) -> None:
        self._active_page = page_key
        for key, view in self._views.items():
            if key == page_key:
                view.pack(fill="both", expand=True, padx=22, pady=20)
            else:
                view.pack_forget()

        for key, btn in self._nav_buttons.items():
            if key == page_key:
                btn.configure(fg_color=BTN_WHITE_BG, text_color=BTN_WHITE_TEXT, hover_color=BTN_WHITE_HOVER)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY, hover_color=CARD_BG)

    # ── Page 1: Timer View ────────────────────────────────────────────────────

    def _create_timer_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self._content_area, fg_color="transparent")

        self._timer_title_label = ctk.CTkLabel(
            view,
            text=self.t("timer_title"),
            font=ctk.CTkFont(family=HAND_FONT, size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._timer_title_label.pack(anchor="w", pady=(0, 2))

        self._timer_desc_label = ctk.CTkLabel(
            view,
            text=self.t("timer_desc"),
            font=ctk.CTkFont(family=BODY_FONT, size=11),
            text_color=TEXT_SECONDARY,
        )
        self._timer_desc_label.pack(anchor="w", pady=(0, 14))

        # Countdown Header Display
        self._countdown_label = ctk.CTkLabel(
            view,
            text="00 : 00 : 00",
            font=ctk.CTkFont(family="Consolas", size=44, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._countdown_label.pack(pady=(0, 14))

        # Spinners Card
        spinner_card = ctk.CTkFrame(
            view,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=2,
            border_color=BORDER_CLR,
        )
        spinner_card.pack(fill="x", pady=(0, 14))

        spinner_inner = ctk.CTkFrame(spinner_card, fg_color="transparent")
        spinner_inner.pack(pady=10)

        self._hr_spinner = TimeSpinner(spinner_inner, label_key=self.t("spinner_hours"), min_val=0, max_val=23, initial=0)
        self._hr_spinner.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            spinner_inner,
            text=":",
            font=ctk.CTkFont(family="Consolas", size=26, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=2, pady=(18, 0))

        self._min_spinner = TimeSpinner(spinner_inner, label_key=self.t("spinner_minutes"), min_val=0, max_val=59, initial=0)
        self._min_spinner.pack(side="left", padx=(8, 8))

        ctk.CTkLabel(
            spinner_inner,
            text=":",
            font=ctk.CTkFont(family="Consolas", size=26, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=2, pady=(18, 0))

        self._sec_spinner = TimeSpinner(spinner_inner, label_key=self.t("spinner_seconds"), min_val=0, max_val=59, initial=0)
        self._sec_spinner.pack(side="left", padx=(8, 0))

        # Presets Bar
        preset_frame = ctk.CTkFrame(view, fg_color="transparent")
        preset_frame.pack(pady=(0, 16), anchor="w")

        presets = [
            ("15M", 0, 15, 0),
            ("30M", 0, 30, 0),
            ("1H",  1,  0, 0),
            ("2H",  2,  0, 0),
        ]

        self._preset_btns = []
        for label, h, m, s in presets:
            btn = ctk.CTkButton(
                preset_frame,
                text=label,
                width=80,
                height=32,
                font=ctk.CTkFont(family=BODY_FONT, size=11, weight="bold"),
                corner_radius=8,
                fg_color=CARD_BG,
                hover_color=BTN_DARK_HOVER,
                border_width=1,
                border_color=BORDER_CLR,
                text_color=TEXT_PRIMARY,
                command=lambda hh=h, mm=m, ss=s: self._apply_preset(hh, mm, ss),
            )
            btn.pack(side="left", padx=(0, 8))
            self._preset_btns.append(btn)

        # Action Buttons Row
        btn_row = ctk.CTkFrame(view, fg_color="transparent")
        btn_row.pack(anchor="w")

        self._start_btn = ctk.CTkButton(
            btn_row,
            text=self.t("btn_start"),
            width=150,
            height=40,
            font=ctk.CTkFont(family=BODY_FONT, size=13, weight="bold"),
            corner_radius=10,
            fg_color=BTN_WHITE_BG,
            hover_color=BTN_WHITE_HOVER,
            text_color=BTN_WHITE_TEXT,
            command=self._on_start_timer,
        )
        self._start_btn.pack(side="left", padx=(0, 10))

        self._cancel_btn = ctk.CTkButton(
            btn_row,
            text=self.t("btn_cancel"),
            width=110,
            height=40,
            font=ctk.CTkFont(family=BODY_FONT, size=13, weight="bold"),
            corner_radius=10,
            fg_color=BTN_DANGER_BG,
            hover_color=BTN_DANGER_HOVER,
            text_color=BTN_DANGER_TEXT,
            state="disabled",
            command=self._on_cancel,
        )
        self._cancel_btn.pack(side="left", padx=(0, 10))

        return view

    # ── Page 2: Schedule View ─────────────────────────────────────────────────

    def _create_schedule_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self._content_area, fg_color="transparent")

        self._sched_title_label = ctk.CTkLabel(
            view,
            text=self.t("sched_title"),
            font=ctk.CTkFont(family=HAND_FONT, size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._sched_title_label.pack(anchor="w", pady=(0, 2))

        self._sched_desc_label = ctk.CTkLabel(
            view,
            text=self.t("sched_desc"),
            font=ctk.CTkFont(family=BODY_FONT, size=11),
            text_color=TEXT_SECONDARY,
        )
        self._sched_desc_label.pack(anchor="w", pady=(0, 16))

        # Clock Picker Card
        clock_card = ctk.CTkFrame(
            view,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=2,
            border_color=BORDER_CLR,
        )
        clock_card.pack(fill="x", pady=(0, 16))

        clock_inner = ctk.CTkFrame(clock_card, fg_color="transparent")
        clock_inner.pack(pady=14)

        now = datetime.now()

        self._sched_hr_spinner = TimeSpinner(clock_inner, label_key=self.t("target_hr"), min_val=0, max_val=23, initial=now.hour)
        self._sched_hr_spinner.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            clock_inner,
            text=":",
            font=ctk.CTkFont(family="Consolas", size=26, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=2, pady=(18, 0))

        self._sched_min_spinner = TimeSpinner(clock_inner, label_key=self.t("target_min"), min_val=0, max_val=59, initial=now.minute)
        self._sched_min_spinner.pack(side="left", padx=(12, 0))

        # Schedule Info Banner
        self._sched_info_card = ctk.CTkFrame(
            view,
            fg_color=CARD_INNER,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_CLR,
        )
        self._sched_info_card.pack(fill="x", pady=(0, 16))

        self._sched_info_label = ctk.CTkLabel(
            self._sched_info_card,
            text=self.t("sched_info"),
            font=ctk.CTkFont(family=BODY_FONT, size=12),
            text_color=TEXT_SECONDARY,
            pady=10,
        )
        self._sched_info_label.pack()

        # Daily Repeat Switch
        self._daily_repeat_switch = ctk.CTkSwitch(
            view,
            text=self.t("daily_repeat"),
            font=ctk.CTkFont(family=BODY_FONT, size=12),
            progress_color=TEXT_PRIMARY,
            button_color=TEXT_PRIMARY,
            variable=self._daily_repeat_var,
        )
        self._daily_repeat_switch.pack(anchor="w", pady=(0, 16))

        # Start Schedule Button
        self._sched_start_btn = ctk.CTkButton(
            view,
            text=self.t("btn_set_sched"),
            width=220,
            height=40,
            font=ctk.CTkFont(family=BODY_FONT, size=13, weight="bold"),
            corner_radius=10,
            fg_color=BTN_WHITE_BG,
            hover_color=BTN_WHITE_HOVER,
            text_color=BTN_WHITE_TEXT,
            command=self._on_start_schedule,
        )
        self._sched_start_btn.pack(anchor="w")

        return view

    # ── Page 3: Settings View ─────────────────────────────────────────────────

    def _create_settings_view(self) -> ctk.CTkFrame:
        view = ctk.CTkFrame(self._content_area, fg_color="transparent")

        self._settings_title_label = ctk.CTkLabel(
            view,
            text=self.t("settings_title"),
            font=ctk.CTkFont(family=HAND_FONT, size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._settings_title_label.pack(anchor="w", pady=(0, 2))

        self._settings_desc_label = ctk.CTkLabel(
            view,
            text=self.t("settings_desc"),
            font=ctk.CTkFont(family=BODY_FONT, size=11),
            text_color=TEXT_SECONDARY,
        )
        self._settings_desc_label.pack(anchor="w", pady=(0, 16))

        # Settings Switches Card
        settings_card = ctk.CTkFrame(
            view,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=2,
            border_color=BORDER_CLR,
        )
        settings_card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(settings_card, fg_color="transparent")
        inner.pack(padx=16, pady=14, fill="x")

        self._sw_close_tray = ctk.CTkSwitch(
            inner,
            text=self.t("sw_close_tray"),
            font=ctk.CTkFont(family=BODY_FONT, size=12),
            progress_color=TEXT_PRIMARY,
            button_color=TEXT_PRIMARY,
            variable=self._close_to_tray_var,
        )
        self._sw_close_tray.pack(anchor="w", pady=(0, 12))

        self._sw_warning = ctk.CTkSwitch(
            inner,
            text=self.t("sw_warning"),
            font=ctk.CTkFont(family=BODY_FONT, size=12),
            progress_color=TEXT_PRIMARY,
            button_color=TEXT_PRIMARY,
            variable=self._enable_warning_var,
        )
        self._sw_warning.pack(anchor="w")

        # Tray Guide Card
        info_box = ctk.CTkFrame(
            view,
            fg_color=CARD_INNER,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_CLR,
        )
        info_box.pack(fill="x")

        self._tray_guide_title_label = ctk.CTkLabel(
            info_box,
            text=self.t("tray_guide_title"),
            font=ctk.CTkFont(family=BODY_FONT, size=12, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        self._tray_guide_title_label.pack(anchor="w", padx=14, pady=(12, 2))

        self._tray_guide_body_label = ctk.CTkLabel(
            info_box,
            text=self.t("tray_guide_body"),
            font=ctk.CTkFont(family=BODY_FONT, size=11),
            text_color=TEXT_SECONDARY,
            justify="left",
        )
        self._tray_guide_body_label.pack(anchor="w", padx=14, pady=(0, 12))

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

        self._tray_image = create_handdrawn_tray_image()
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
            msg = "No timer running."

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

    # ── Actions ───────────────────────────────────────────────────────────────

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
            messagebox.showwarning("Warning", self.t("invalid_time_msg"))
            return

        self._start_countdown(total, mode_text="Timer")

    def _on_start_schedule(self) -> None:
        target_h = self._sched_hr_spinner.value
        target_m = self._sched_min_spinner.value

        now = datetime.now()
        target_dt = now.replace(hour=target_h, minute=target_m, second=0, microsecond=0)

        if target_dt <= now:
            target_dt += timedelta(days=1)

        diff_seconds = int((target_dt - now).total_seconds())

        if diff_seconds <= 0:
            messagebox.showwarning("Warning", self.t("invalid_time_msg"))
            return

        self._schedule_target_dt = target_dt
        dt_str = target_dt.strftime("%H:%M (%d/%m)")
        self._sched_info_label.configure(
            text=self.t("sched_target_banner", time=dt_str),
            text_color=TEXT_PRIMARY,
        )

        self._start_countdown(diff_seconds, mode_text=f"Schedule ({target_h:02d}:{target_m:02d})")

    def _start_countdown(self, seconds: int, mode_text: str = "") -> None:
        self._remaining = seconds
        self._is_running = True
        self._warning_shown = False

        self._start_btn.configure(state="disabled")
        self._sched_start_btn.configure(state="disabled")
        self._cancel_btn.configure(state="normal")
        self._hr_spinner.set_state("disabled")
        self._min_spinner.set_state("disabled")
        self._sec_spinner.set_state("disabled")
        self._sched_hr_spinner.set_state("disabled")
        self._sched_min_spinner.set_state("disabled")

        self._drawer_status_label.configure(text=self.t("status_running"), text_color=TEXT_PRIMARY)

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
        self._cancel_btn.configure(state="disabled")

        self._hr_spinner.set_state("normal")
        self._min_spinner.set_state("normal")
        self._sec_spinner.set_state("normal")
        self._sched_hr_spinner.set_state("normal")
        self._sched_min_spinner.set_state("normal")

        self._drawer_status_label.configure(text=self.t("status_ready"), text_color=TEXT_SECONDARY)
        self._sched_info_label.configure(text=self.t("sched_info"), text_color=TEXT_SECONDARY)

        if hasattr(self, "_tray_icon") and self._tray_icon:
            self._tray_icon.title = "Shutdown Scheduler"

    # ── Countdown Logic ───────────────────────────────────────────────────────

    def _tick(self) -> None:
        if not self._is_running:
            return

        h, rem = divmod(self._remaining, 3600)
        m, s = divmod(rem, 60)
        display = f"{h:02d} : {m:02d} : {s:02d}"

        self._countdown_label.configure(text=display, text_color=TEXT_PRIMARY)

        if hasattr(self, "_tray_icon") and self._tray_icon:
            self._tray_icon.title = f"Shutdown in {h:02d}:{m:02d}:{s:02d}"

        if self._remaining == 300 and not self._warning_shown and self._enable_warning_var.get():
            self._warning_shown = True
            self._show_warning_dialog()

        if self._remaining <= 0:
            self._trigger_shutdown()
            return

        self._remaining -= 1
        self._timer_id = self.after(1000, self._tick)

    def _show_warning_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(self.t("warning_dialog_title"))
        dialog.geometry("440x230")
        dialog.resizable(False, False)
        dialog.configure(fg_color=BG_MAIN)
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_x() + (self.WIDTH - 440) // 2
        y = self.winfo_y() + (self.HEIGHT - 230) // 2
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text=self.t("warning_dialog_title"),
            font=ctk.CTkFont(family=HAND_FONT, size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(pady=(24, 6))

        ctk.CTkLabel(
            dialog,
            text=self.t("warning_dialog_msg"),
            font=ctk.CTkFont(family=BODY_FONT, size=12),
            text_color=TEXT_SECONDARY,
            justify="center",
        ).pack(pady=(0, 20))

        def cancel_from_warning():
            dialog.destroy()
            self._on_cancel()

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(
            btn_row,
            text=self.t("warning_btn_cancel"),
            width=160,
            height=38,
            font=ctk.CTkFont(family=BODY_FONT, size=12, weight="bold"),
            corner_radius=8,
            fg_color=BTN_DANGER_BG,
            hover_color=BTN_DANGER_HOVER,
            text_color=BTN_DANGER_TEXT,
            command=cancel_from_warning,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_row,
            text=self.t("warning_btn_ok"),
            width=100,
            height=38,
            font=ctk.CTkFont(family=BODY_FONT, size=12, weight="bold"),
            corner_radius=8,
            fg_color=CARD_BG,
            hover_color=BTN_DARK_HOVER,
            border_width=1,
            border_color=BORDER_CLR,
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


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ShutdownSchedulerApp()
    app.mainloop()
