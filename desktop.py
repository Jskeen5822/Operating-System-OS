#!/usr/bin/env python3
"""
Operating System OS - Full Graphical Desktop Environment
A complete visual desktop with windows, file manager, system monitor, and terminal
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from enum import Enum
import time
import threading
import os
import sys
from datetime import datetime

class ProcessState(Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"

class Process:
    def __init__(self, pid, name, priority=0):
        self.pid = pid
        self.name = name
        self.state = ProcessState.READY
        self.priority = priority
        self.memory_kb = 128 + (pid * 64)
        self.cpu_usage = 5 + (pid % 10)
        self.creation_time = time.time()

class OSDesktop:
    def __init__(self, root):
        self.root = root
        self.root.title("Operating System OS - Desktop")
        self.root.geometry("1280x800")
        
        # Palette and typography for a grounded desktop look
        self.colors = {
            "wallpaper_dark": "#0a1020",
            "wallpaper_light": "#1a2948",
            "wallpaper_mid": "#132b4f",
            "wallpaper_glow": "#3b82f6",
            "taskbar": "#0c1324",
            "taskbar_border": "#111827",
            "text_primary": "#e5e7eb",
            "text_muted": "#94a3b8",
            "accent": "#60a5fa",
            "accent_pink": "#ec4899",
            "accent_green": "#22c55e",
            "accent_yellow": "#fbbf24",
            "window_bg": "#0f172a",
            "window_header": "#0b1224",
            "control_bg": "#0f172a",
            "menu_bg": "#0c1424",
            "menu_item": "#111827"
        }
        self.fonts = {
            "ui": ("Segoe UI", 10),
            "ui_bold": ("Segoe UI", 10, "bold"),
            "title": ("Segoe UI", 16, "bold"),
            "caption": ("Segoe UI", 9),
            "mono": ("Cascadia Code", 10),
        }
        self.root.configure(bg=self.colors["wallpaper_dark"])
        self.wallpaper_photo = None
        self.wallpaper_pil = None
        self._load_wallpaper_image()
        
        # OS State
        self.process_table = []
        self.next_pid = 1
        self.current_process = None
        self.system_ticks = 0
        self.memory_total_kb = 12582912  # 12 GB in KB
        self.memory_allocated_kb = 524288  # 512 MB used
        self.max_processes = 2048
        self.start_time = time.time()
        
        # File system
        self.files = {
            "/": {"type": "directory", "icon": "📁", "size": 0},
            "/Documents": {"type": "directory", "icon": "📂", "size": 0},
            "/Pictures": {"type": "directory", "icon": "📸", "size": 0},
            "/Music": {"type": "directory", "icon": "🎵", "size": 0},
            "/Programs": {"type": "directory", "icon": "⚙️", "size": 0},
            "/readme.txt": {"type": "file", "icon": "📄", "size": 2048},
            "/kernel.bin": {"type": "file", "icon": "💾", "size": 20480},
            "/shell.bin": {"type": "file", "icon": "⌨️", "size": 5120},
        }
        self.current_directory = "/"
        
        # Create idle process
        self.create_process("idle", priority=0)
        self.current_process = self.process_table[0]
        self.current_process.state = ProcessState.RUNNING
        
        # Create UI
        self.setup_ui()
        self.start_update_thread()
        
        # Boot animation
        self.show_boot_screen()
    
    def setup_ui(self):
        """Create the main desktop UI"""
        # Use a calm wallpaper and grounded controls
        try:
            ttk.Style().theme_use("clam")
        except:
            pass
        
        # Top bar (acts as taskbar)
        self.taskbar = tk.Frame(
            self.root,
            bg=self.colors["taskbar"],
            height=52,
            highlightthickness=1,
            highlightbackground=self.colors["taskbar_border"],
        )
        self.taskbar.pack(side=tk.TOP, fill=tk.X)
        self.taskbar.pack_propagate(False)
        
        # Desktop area and wallpaper
        self.desktop = tk.Frame(self.root, bg=self.colors["wallpaper_dark"])
        self.desktop.pack(fill=tk.BOTH, expand=True)
        
        self.wallpaper_canvas = tk.Canvas(
            self.desktop,
            bg=self.colors["wallpaper_dark"],
            highlightthickness=0,
        )
        self.wallpaper_canvas.pack(fill=tk.BOTH, expand=True)
        self.wallpaper_canvas.bind("<Configure>", self.draw_wallpaper)
        
        # Left dock (disabled)
        self.show_left_dock = False
        if self.show_left_dock:
            self.build_left_dock()
        
        # Desktop icons (hidden by default)
        self.show_desktop_icons = False
        if self.show_desktop_icons:
            self.icon_area = tk.Frame(self.desktop, bg=self.colors["wallpaper_dark"], highlightthickness=0)
            self.icon_area.place(x=160, y=120)
            self.icon_area.lift()
            self.build_desktop_icons()
        
        # Small status card on the desktop
        self.build_status_card()
        
        # Top bar controls and start menu
        self.build_taskbar_content()
        self.create_start_menu()
        
        # Bottom dock
        self.build_bottom_dock()
        
        # Hide the start menu when clicking away
        self.root.bind("<Button-1>", self._maybe_close_start_menu)
    
    def draw_wallpaper(self, event):
        """Paint a subtle gradient wallpaper without distracting shapes"""
        self.wallpaper_canvas.delete("grad")
        
        if self.wallpaper_pil and event.width > 0 and event.height > 0:
            img_w, img_h = self.wallpaper_pil.size
            scale = max(event.width / img_w, event.height / img_h)
            new_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
            try:
                from PIL import Image, ImageTk  # type: ignore
                resized = self.wallpaper_pil.resize(new_size, Image.LANCZOS)
                # center-crop to canvas size
                left = max(0, (resized.width - event.width) // 2)
                top = max(0, (resized.height - event.height) // 2)
                cropped = resized.crop((left, top, left + event.width, top + event.height))
                self.wallpaper_render = ImageTk.PhotoImage(cropped)
                self.wallpaper_canvas.create_image(
                    0, 0, image=self.wallpaper_render, anchor="nw", tags="grad"
                )
                return
            except Exception:
                pass
        
        if self.wallpaper_photo:
            # Center the wallpaper image
            self.wallpaper_canvas.create_image(
                event.width // 2,
                event.height // 2,
                image=self.wallpaper_photo,
                anchor="center",
                tags="grad",
            )
            self.wallpaper_canvas.image = self.wallpaper_photo
            return
        
        top = self._hex_to_rgb(self.colors["wallpaper_glow"])
        mid = self._hex_to_rgb(self.colors["wallpaper_mid"])
        bottom = self._hex_to_rgb(self.colors["wallpaper_dark"])
        steps = max(event.height, 1)
        
        for i in range(steps):
            ratio = i / steps
            if ratio < 0.35:
                blend = self._blend(top, mid, ratio / 0.35)
            else:
                blend = self._blend(mid, bottom, (ratio - 0.35) / 0.65)
            color = f"#{blend[0]:02x}{blend[1]:02x}{blend[2]:02x}"
            self.wallpaper_canvas.create_line(0, i, event.width, i, fill=color, tags="grad")
        
        # Glow halo at center
        cx, cy = event.width // 2, event.height // 2
        radius = min(event.width, event.height) // 2
        self.wallpaper_canvas.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius,
            outline="#4f46e5", width=2, tags="grad"
        )
        self.wallpaper_canvas.create_oval(
            cx - radius // 2, cy - radius // 2, cx + radius // 2, cy + radius // 2,
            outline="#22d3ee", width=2, tags="grad"
        )
    
    def _hex_to_rgb(self, value):
        value = value.lstrip("#")
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
    
    def _blend(self, start, end, ratio):
        return tuple(int(start[i] + (end[i] - start[i]) * ratio) for i in range(3))
    
    def _load_wallpaper_image(self):
        """Load a wallpaper image if available (PNG/JPG)"""
        candidates = [
            "wallpaper_tree.png",
            "wallpaper_tree.jpg",
            "wallpaper_tree.jpeg",
        ]
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for name in candidates:
            path = os.path.join(base_dir, name)
            if not os.path.exists(path):
                continue
            # Try Pillow for broader format support and future resizing
            try:
                from PIL import Image  # type: ignore
                self.wallpaper_pil = Image.open(path).convert("RGB")
                return
            except Exception:
                self.wallpaper_pil = None
            # Try Tk native loader as a fallback
            try:
                self.wallpaper_photo = tk.PhotoImage(file=path)
                return
            except Exception:
                self.wallpaper_photo = None
        self.wallpaper_pil = None
        self.wallpaper_photo = None
    
    def draw_icon(self, canvas, icon_name, color):
        """Draw a simple vector-style icon on a Tk canvas"""
        canvas.delete("all")
        bg = "#0f172a"
        stroke = "#111827"
        canvas.create_rectangle(3, 3, 47, 47, outline=stroke, fill=bg, width=1)
        
        if icon_name == "folder":
            canvas.create_rectangle(8, 16, 42, 40, outline="", fill=color)
            canvas.create_rectangle(8, 12, 28, 22, outline="", fill=color)
        elif icon_name == "terminal":
            canvas.create_rectangle(8, 12, 42, 38, outline=stroke, fill="#0b1224", width=1)
            canvas.create_line(12, 20, 20, 24, fill=color, width=2)
            canvas.create_line(20, 24, 12, 28, fill=color, width=2)
            canvas.create_line(24, 30, 36, 30, fill=color, width=2)
        elif icon_name == "monitor":
            canvas.create_rectangle(8, 10, 44, 32, outline=stroke, fill="#0b1224", width=1)
            canvas.create_rectangle(20, 32, 32, 38, outline="", fill=stroke)
            canvas.create_line(14, 26, 20, 20, 28, 22, 36, 14, smooth=True, fill=color, width=2)
        elif icon_name == "mail":
            canvas.create_rectangle(8, 12, 42, 36, outline=stroke, fill=color, width=1)
            canvas.create_line(8, 12, 25, 26, 42, 12, fill=bg, width=2)
            canvas.create_line(8, 36, 24, 24, 42, 36, fill=bg, width=2)
        elif icon_name == "media":
            canvas.create_oval(10, 10, 42, 42, outline="", fill=color)
            canvas.create_polygon(22, 16, 36, 26, 22, 36, outline="", fill=bg)
        elif icon_name == "calendar":
            canvas.create_rectangle(10, 14, 40, 40, outline=stroke, fill=color, width=1)
            canvas.create_rectangle(10, 10, 40, 20, outline="", fill="#0b1224")
            canvas.create_text(25, 30, text="18", fill=bg, font=("Segoe UI", 10, "bold"))
        elif icon_name == "settings":
            canvas.create_oval(12, 12, 38, 38, outline=stroke, fill="#0b1224", width=2)
            canvas.create_oval(18, 18, 32, 32, outline="", fill=color)
            for dx, dy in [(0, -10), (0, 10), (-10, 0), (10, 0)]:
                canvas.create_rectangle(24 + dx - 2, 24 + dy - 6, 24 + dx + 2, 24 + dy + 6, outline="", fill=stroke)
        elif icon_name == "photos":
            canvas.create_rectangle(8, 12, 42, 40, outline=stroke, fill="#0b1224", width=1)
            canvas.create_polygon(10, 38, 20, 26, 28, 34, 34, 24, 40, 36, outline="", fill=color)
            canvas.create_oval(12, 16, 20, 24, outline="", fill=self.colors["accent_yellow"])
        elif icon_name == "about":
            canvas.create_oval(10, 10, 42, 42, outline=stroke, fill=color, width=1)
            canvas.create_text(26, 26, text="i", fill=bg, font=("Segoe UI", 12, "bold"))
        else:
            canvas.create_oval(12, 12, 38, 38, outline="", fill=color)
    
    def build_desktop_icons(self):
        """Lay out desktop icons in a simple grid"""
        for child in self.icon_area.winfo_children():
            child.destroy()
        
        icons = [
            ("File Manager", self.open_file_manager, "#60a5fa", "folder"),
            ("Terminal", self.open_terminal_window, "#34d399", "terminal"),
            ("System Monitor", self.open_system_monitor, "#fbbf24", "monitor"),
            ("Mail", self.open_mail_window, "#a78bfa", "mail"),
            ("Settings", self.open_settings_window, "#38bdf8", "settings"),
            ("Media Player", self.open_media_player_window, "#f472b6", "media"),
            ("Calendar", self.open_calendar_window, "#22c55e", "calendar"),
            ("Photos", self.open_photos_window, "#f59e0b", "photos"),
            ("About", self.show_about, "#9ca3af", "about"),
        ]
        
        panel = tk.Frame(
            self.icon_area,
            bg="#0d1729",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors["taskbar_border"],
        )
        panel.grid(row=0, column=0, sticky="nw")
        
        cols = 3
        for idx, (label, command, color, icon_name) in enumerate(icons):
            row, col = divmod(idx, cols)
            tile = tk.Frame(panel, bg="#0d1729", highlightthickness=0, padx=14, pady=12)
            tile.grid(row=row, column=col, padx=6, pady=4, sticky="w")
            
            icon_canvas = tk.Canvas(
                tile, width=52, height=52, bg="#0d1729",
                highlightthickness=0,
            )
            icon_canvas.pack()
            self.draw_icon(icon_canvas, icon_name, color)
            
            label_widget = tk.Label(
                tile, text=label, font=self.fonts["ui"],
                fg=self.colors["text_primary"], bg="#0d1729"
            )
            label_widget.pack(pady=(6, 0))
            
            def bind_launch(widget, cmd=command):
                widget.bind("<Double-Button-1>", lambda _e: cmd())
                widget.bind("<Button-1>", self._maybe_close_start_menu)
            
            for widget in (tile, icon_canvas, label_widget):
                bind_launch(widget)
    
    def build_left_dock(self):
        """Vertical dock on the left side"""
        dock = tk.Frame(self.desktop, bg="#0c1324", width=180, highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        dock.place(x=20, y=80, relheight=0.8)
        dock.pack_propagate(False)
        
        tk.Label(dock, text="Apps", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg="#0c1324").pack(pady=(12, 8))
        
        buttons = [
            ("Dashboard", self.show_about, "#38bdf8", "about"),
            ("Files", self.open_file_manager, "#60a5fa", "folder"),
            ("Terminal", self.open_terminal_window, "#34d399", "terminal"),
            ("Monitor", self.open_system_monitor, "#fbbf24", "monitor"),
            ("Mail", self.open_mail_window, "#a78bfa", "mail"),
            ("Media", self.open_media_player_window, "#f472b6", "media"),
            ("Calendar", self.open_calendar_window, "#22c55e", "calendar"),
            ("Photos", self.open_photos_window, "#f59e0b", "photos"),
            ("Settings", self.open_settings_window, "#9ca3af", "settings"),
        ]
        
        for label, cmd, color, icon_name in buttons:
            btn = tk.Frame(dock, bg="#0c1324", padx=10, pady=6, highlightthickness=1, highlightbackground=color, cursor="hand2")
            btn.pack(fill=tk.X, padx=12, pady=4)
            btn.pack_propagate(False)
            icon = tk.Canvas(btn, width=32, height=32, bg="#0c1324", highlightthickness=0)
            icon.pack(side=tk.LEFT, padx=(2, 8), pady=4)
            self.draw_icon(icon, icon_name, color)
            label_widget = tk.Label(btn, text=label, font=self.fonts["ui"], fg=self.colors["text_primary"], bg="#0c1324", anchor="w")
            label_widget.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
            btn.bind("<Button-1>", lambda _e, c=cmd: c())
            label_widget.bind("<Button-1>", lambda _e, c=cmd: c())
            icon.bind("<Button-1>", lambda _e, c=cmd: c())
    
    def build_bottom_dock(self):
        """Centered dock icons at the bottom"""
        dock_frame = tk.Frame(self.desktop, bg="", height=80)
        dock_frame.pack(side=tk.BOTTOM, pady=20)
        
        dock = tk.Frame(dock_frame, bg="#0c1324", height=70, highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        dock.pack()
        
        icons = [
            ("Home", self.open_file_manager, "#60a5fa", "folder"),
            ("Terminal", self.open_terminal_window, "#34d399", "terminal"),
            ("Monitor", self.open_system_monitor, "#f59e0b", "monitor"),
            ("Mail", self.open_mail_window, "#a78bfa", "mail"),
            ("Media", self.open_media_player_window, "#f472b6", "media"),
            ("Calendar", self.open_calendar_window, "#22c55e", "calendar"),
            ("Settings", self.open_settings_window, "#9ca3af", "settings"),
        ]
        
        for label, cmd, color, icon_name in icons:
            tile = tk.Frame(dock, bg="#0c1324", padx=12, pady=10)
            tile.pack(side=tk.LEFT)
            icon_canvas = tk.Canvas(tile, width=44, height=44, bg="#0c1324", highlightthickness=0)
            icon_canvas.pack()
            self.draw_icon(icon_canvas, icon_name, color)
            btn = tk.Button(
                tile,
                text=label,
                font=self.fonts["caption"],
                command=cmd,
                bg="#0f172a",
                fg=self.colors["text_primary"],
                activebackground="#1f2937",
                activeforeground=self.colors["text_primary"],
                relief=tk.FLAT,
                padx=10,
                pady=6,
            )
            btn.pack(pady=(6, 0))
            btn.configure(highlightthickness=1, highlightbackground=color, highlightcolor=color)
    
    def build_status_card(self):
        """Small, unobtrusive system card pinned to the desktop"""
        self.status_card = tk.Frame(self.desktop, bg="#0d1729", highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        self.status_card.place(relx=1.0, x=-240, y=40, width=220)
        
        tk.Label(
            self.status_card, text="System", font=self.fonts["ui_bold"],
            fg=self.colors["text_primary"], bg="#0d1729"
        ).pack(anchor=tk.W, padx=12, pady=(10, 2))
        
        self.desktop_status_label = tk.Label(
            self.status_card,
            text=(
                f"Uptime 00:00:00\n"
                f"Processes 1/{self.max_processes}\n"
                f"Memory {self.memory_allocated_kb // 1024} MB of {self.memory_total_kb // 1024} MB"
            ),
            font=self.fonts["caption"],
            justify=tk.LEFT,
            fg=self.colors["text_muted"],
            bg="#0d1729",
        )
        self.desktop_status_label.pack(anchor=tk.W, padx=12, pady=(0, 12))
    
    def build_taskbar_content(self):
        """Taskbar with start button, quick launch, and system tray"""
        left = tk.Frame(self.taskbar, bg=self.colors["taskbar"])
        left.pack(side=tk.LEFT, padx=12)
        
        self.start_button = tk.Button(
            left,
            text="Start",
            font=self.fonts["ui_bold"],
            command=self.toggle_start_menu,
            bg=self.colors["accent"],
            fg="white",
            bd=0,
            padx=14,
            pady=8,
            activebackground=self.colors["accent"],
            activeforeground="white",
        )
        self.start_button.pack(side=tk.LEFT)
        
        center = tk.Frame(self.taskbar, bg=self.colors["taskbar"])
        center.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_placeholder = tk.Entry(
            center,
            font=self.fonts["caption"],
            relief=tk.FLAT,
            bg=self.colors["taskbar_border"],
            fg=self.colors["text_muted"],
            state="readonly",
            readonlybackground=self.colors["taskbar_border"],
            width=80,
        )
        self.search_placeholder.insert(0, "Search...")
        self.search_placeholder.pack(side=tk.LEFT, padx=20, pady=9, ipady=4, fill=tk.X, expand=True)
        
        tray = tk.Frame(self.taskbar, bg=self.colors["taskbar"])
        tray.pack(side=tk.RIGHT, padx=16, pady=6)
        
        self.status_label = tk.Label(
            tray,
            text="Uptime 0:00:00 · 1 running",
            font=self.fonts["caption"],
            bg=self.colors["taskbar"],
            fg=self.colors["text_muted"],
        )
        self.status_label.pack(side=tk.RIGHT, padx=(0, 12))
        
        self.time_label = tk.Label(
            tray,
            text="",
            font=self.fonts["ui_bold"],
            bg=self.colors["taskbar"],
            fg=self.colors["text_primary"],
        )
        self.time_label.pack(side=tk.RIGHT)
    
    def create_start_menu(self):
        """Create a compact start menu listing the key apps"""
        self.start_menu_visible = False
        self.start_menu = tk.Frame(
            self.root,
            bg=self.colors["menu_bg"],
            bd=1,
            relief=tk.SOLID,
            highlightthickness=0,
        )
        self.start_menu.place_forget()
        
        header = tk.Frame(self.start_menu, bg=self.colors["menu_bg"])
        header.pack(fill=tk.X, padx=12, pady=(10, 6))
        tk.Label(
            header,
            text="Operating System OS",
            font=self.fonts["title"],
            fg=self.colors["text_primary"],
            bg=self.colors["menu_bg"],
        ).pack(anchor=tk.W)
        tk.Label(
            header,
            text="Desktop environment",
            font=self.fonts["caption"],
            fg=self.colors["text_muted"],
            bg=self.colors["menu_bg"],
        ).pack(anchor=tk.W, pady=(2, 0))
        
        menu_items = [
            ("File Manager", "Browse files and folders", self.open_file_manager),
            ("Terminal", "Open the shell prompt", self.open_terminal_window),
            ("System Monitor", "Inspect processes and memory", self.open_system_monitor),
            ("Mail", "Check recent messages", self.open_mail_window),
            ("Media Player", "Listen to music", self.open_media_player_window),
            ("Calendar", "View date and weather", self.open_calendar_window),
            ("Settings", "System preferences", self.open_settings_window),
            ("About", "System information", self.show_about),
        ]
        
        for name, desc, cmd in menu_items:
            item = tk.Frame(self.start_menu, bg=self.colors["menu_item"], highlightthickness=0)
            item.pack(fill=tk.X, padx=12, pady=4)
            tk.Label(
                item,
                text=name,
                font=self.fonts["ui_bold"],
                fg=self.colors["text_primary"],
                bg=self.colors["menu_item"],
            ).pack(anchor=tk.W, padx=10, pady=(8, 0))
            tk.Label(
                item,
                text=desc,
                font=self.fonts["caption"],
                fg=self.colors["text_muted"],
                bg=self.colors["menu_item"],
            ).pack(anchor=tk.W, padx=10, pady=(0, 8))
            
            item.bind("<Button-1>", lambda _e, c=cmd: self._launch_from_menu(c))
            for child in item.winfo_children():
                child.bind("<Button-1>", lambda _e, c=cmd: self._launch_from_menu(c))
        
        footer = tk.Frame(self.start_menu, bg=self.colors["menu_bg"])
        footer.pack(fill=tk.X, padx=12, pady=(8, 10))
        tk.Button(
            footer,
            text="Settings",
            command=self.show_about,
            font=self.fonts["caption"],
            bg=self.colors["taskbar_border"],
            fg=self.colors["text_primary"],
            relief=tk.FLAT,
            activebackground=self.colors["taskbar_border"],
        ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(
            footer,
            text="Shut Down",
            command=self.root.destroy,
            font=self.fonts["caption"],
            bg=self.colors["taskbar_border"],
            fg=self.colors["text_primary"],
            relief=tk.FLAT,
            activebackground=self.colors["taskbar_border"],
        ).pack(side=tk.LEFT)
    
    def toggle_start_menu(self):
        if self.start_menu_visible:
            self._hide_start_menu()
        else:
            self._show_start_menu()
    
    def _show_start_menu(self):
        self.start_menu.update_idletasks()
        taskbar_height = max(self.taskbar.winfo_height(), 52)
        self.start_menu.place(
            x=10,
            y=taskbar_height + 6,
            anchor="nw",
            width=320,
        )
        self.start_menu_visible = True
    
    def _hide_start_menu(self):
        self.start_menu.place_forget()
        self.start_menu_visible = False
    
    def _launch_from_menu(self, command):
        self._hide_start_menu()
        command()
    
    def _maybe_close_start_menu(self, event=None):
        if not self.start_menu_visible:
            return
        widget = event.widget if event else None
        if widget and (self._is_child_of(widget, self.start_menu) or self._is_child_of(widget, self.start_button)):
            return
        self._hide_start_menu()
    
    def _is_child_of(self, widget, parent):
        while widget:
            if widget == parent:
                return True
            widget = widget.master
        return False
    
    def show_boot_screen(self):
        """Show boot animation"""
        boot_window = tk.Toplevel(self.root)
        boot_window.geometry("600x400")
        boot_window.configure(bg="#000000")
        boot_window.grab_set()
        
        frame = tk.Frame(boot_window, bg="#000000")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(frame, text="Operating System OS", font=("Courier", 20, "bold"),
                        bg="#000000", fg="#00ff00")
        title.pack(pady=20)
        
        subtitle = tk.Label(frame, text="Bootloader v1.0", font=("Courier", 12),
                           bg="#000000", fg="#00ff00")
        subtitle.pack()
        
        text_frame = tk.Frame(frame, bg="#000000")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, bg="#000000", fg="#00ff00", 
                             font=("Courier", 10), height=15, width=70)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.config(state=tk.DISABLED)
        
        boot_messages = [
            "Starting bootloader...",
            "✓ BIOS initialization complete",
            "✓ Loading kernel from disk",
            "✓ Switching to 32-bit protected mode",
            "✓ Kernel loaded at 0x1000",
            "",
            "Initializing kernel subsystems...",
            "✓ Interrupts initialized",
            "✓ Memory management initialized (12 GB)",
            "✓ File system initialized (512 files, 8192 blocks)",
            "✓ Idle process created (PID=1)",
            "",
            "System ready. Loading desktop environment...",
        ]
        
        def add_message(index=0):
            if index < len(boot_messages):
                text_widget.config(state=tk.NORMAL)
                text_widget.insert(tk.END, boot_messages[index] + "\n")
                text_widget.see(tk.END)
                text_widget.config(state=tk.DISABLED)
                boot_window.after(200, lambda: add_message(index + 1))
            else:
                boot_window.after(1000, boot_window.destroy)
        
        add_message()
    
    def create_process(self, name, priority=0):
        if len(self.process_table) >= self.max_processes:
            return None
        process = Process(self.next_pid, name, priority)
        self.process_table.append(process)
        self.next_pid += 1
        return process
    
    def open_terminal_window(self):
        """Open terminal window"""
        term_window = tk.Toplevel(self.root)
        term_window.title("Terminal - Operating System OS")
        term_window.geometry("900x620")
        term_window.configure(bg=self.colors["window_bg"], highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        
        header = tk.Frame(term_window, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="Terminal",
            font=self.fonts["ui_bold"],
            bg=self.colors["window_header"],
            fg=self.colors["text_primary"],
        ).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(
            header,
            text="jskeen@os-desktop",
            font=self.fonts["caption"],
            bg=self.colors["window_header"],
            fg=self.colors["text_muted"],
        ).pack(side=tk.LEFT, padx=8)
        
        output_frame = tk.Frame(term_window, bg="#0b0f19")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        
        scrollbar = tk.Scrollbar(output_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        output_text = tk.Text(
            output_frame,
            bg="#0b0f19",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            font=self.fonts["mono"],
            yscrollcommand=scrollbar.set,
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=0,
        )
        output_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=output_text.yview)
        
        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, "Operating System OS terminal\n")
        output_text.insert(tk.END, "Type 'help' for commands, 'exit' to close\n\n")
        output_text.config(state=tk.DISABLED)
        
        input_frame = tk.Frame(term_window, bg="#0b0f19")
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        prompt = tk.Label(
            input_frame,
            text=">",
            font=self.fonts["mono"],
            bg="#0b0f19",
            fg="#9ca3af",
        )
        prompt.pack(side=tk.LEFT, padx=(0, 6))
        
        input_entry = tk.Entry(
            input_frame,
            bg="#111827",
            fg="#e5e7eb",
            insertbackground="#e5e7eb",
            font=self.fonts["mono"],
            relief=tk.FLAT,
        )
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        def execute_command(event=None):
            cmd = input_entry.get().strip()
            input_entry.delete(0, tk.END)
            
            output_text.config(state=tk.NORMAL)
            if cmd:
                output_text.insert(tk.END, f"> {cmd}\n")
            
            if cmd == "help":
                output_text.insert(tk.END, "Available commands: help, ps, exec, meminfo, ls, exit, clear\n")
            elif cmd == "ps":
                output_text.insert(tk.END, "Processes:\n")
                for p in self.process_table:
                    if p.state != ProcessState.TERMINATED:
                        output_text.insert(tk.END, f"  PID {p.pid}: {p.name} ({p.state.value})\n")
            elif cmd.startswith("exec"):
                parts = cmd.split()
                if len(parts) > 1:
                    self.create_process(parts[1])
                    output_text.insert(tk.END, f"Process created: {parts[1]}\n")
                else:
                    output_text.insert(tk.END, "Usage: exec <name>\n")
            elif cmd == "meminfo":
                free = self.memory_total_kb - self.memory_allocated_kb
                output_text.insert(tk.END, f"Memory: {self.memory_allocated_kb}/{self.memory_total_kb} KB\n")
                output_text.insert(tk.END, f"Free: {free} KB\n")
            elif cmd == "ls":
                output_text.insert(tk.END, "Files in /:\n")
                for name in sorted(self.files.keys()):
                    if name != "/":
                        info = self.files[name]
                        size = f"{info['size']} bytes" if info["type"] == "file" else "dir"
                        output_text.insert(tk.END, f"  {name:<18} {info['type']:<9} {size}\n")
            elif cmd == "exit":
                term_window.destroy()
                return
            elif cmd == "clear":
                output_text.delete("1.0", tk.END)
                output_text.config(state=tk.DISABLED)
                return
            elif cmd == "":
                pass
            else:
                output_text.insert(tk.END, f"Unknown command: {cmd}\n")
            
            output_text.see(tk.END)
            output_text.config(state=tk.DISABLED)
        
        input_entry.bind("<Return>", execute_command)
        input_entry.focus_set()
    
    def open_file_manager(self):
        """Open file manager window"""
        file_window = tk.Toplevel(self.root)
        file_window.title("Files - Operating System OS")
        file_window.geometry("900x620")
        file_window.configure(bg=self.colors["window_bg"], highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        
        header = tk.Frame(file_window, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="Files",
            font=self.fonts["ui_bold"],
            fg=self.colors["text_primary"],
            bg=self.colors["window_header"],
        ).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(
            header,
            text=f"Location: {self.current_directory}",
            font=self.fonts["caption"],
            fg=self.colors["text_muted"],
            bg=self.colors["window_header"],
        ).pack(side=tk.LEFT, padx=10)
        
        toolbar = tk.Frame(file_window, bg=self.colors["window_bg"])
        toolbar.pack(fill=tk.X, padx=12, pady=(10, 6))
        
        list_frame = tk.Frame(file_window, bg=self.colors["window_bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        
        columns = ("Name", "Type", "Size")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        tree.heading("Name", text="Name")
        tree.heading("Type", text="Type")
        tree.heading("Size", text="Size")
        tree.column("Name", width=420, anchor=tk.W)
        tree.column("Type", width=120, anchor=tk.W)
        tree.column("Size", width=120, anchor=tk.E)
        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        def populate_tree():
            tree.delete(*tree.get_children())
            for fname, info in sorted(self.files.items()):
                if fname == "/":
                    continue
                name = fname.lstrip("/")
                ftype = "Folder" if info["type"] == "directory" else "File"
                size = "-" if info["type"] == "directory" else f"{info['size']} bytes"
                tree.insert("", "end", values=(name, ftype, size))
        
        def new_file():
            name = simpledialog.askstring("New File", "File name:")
            if name:
                self.files[f"/{name}"] = {"type": "file", "icon": "", "size": 0}
                populate_tree()
        
        def new_folder():
            name = simpledialog.askstring("New Folder", "Folder name:")
            if name:
                self.files[f"/{name}"] = {"type": "directory", "icon": "", "size": 0}
                populate_tree()
        
        def delete_item():
            selected = tree.selection()
            if not selected:
                return
            name = tree.item(selected[0], "values")[0]
            path = f"/{name}"
            if path in self.files and messagebox.askyesno("Delete", f"Delete '{name}'?"):
                del self.files[path]
                populate_tree()
        
        def show_properties(event=None):
            selected = tree.selection()
            if not selected:
                return
            name, ftype, size = tree.item(selected[0], "values")
            messagebox.showinfo(
                "Properties",
                f"Name: {name}\nType: {ftype}\nSize: {size}\nLocation: {self.current_directory}",
            )
        
        ttk.Button(toolbar, text="New File", command=new_file).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="New Folder", command=new_folder).pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Delete", command=delete_item).pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Properties", command=show_properties).pack(side=tk.LEFT, padx=6)
        
        populate_tree()
        tree.bind("<Double-Button-1>", show_properties)
    
    def open_system_monitor(self):
        """Open system monitor window"""
        monitor_window = tk.Toplevel(self.root)
        monitor_window.title("System Monitor - Operating System OS")
        monitor_window.geometry("980x720")
        monitor_window.configure(bg=self.colors["window_bg"], highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        
        header = tk.Frame(monitor_window, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="System Monitor",
            font=self.fonts["ui_bold"],
            fg=self.colors["text_primary"],
            bg=self.colors["window_header"],
        ).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(
            header,
            text="Processes, memory, and uptime",
            font=self.fonts["caption"],
            fg=self.colors["text_muted"],
            bg=self.colors["window_header"],
        ).pack(side=tk.LEFT, padx=8)
        
        notebook = ttk.Notebook(monitor_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        # Processes tab
        process_frame = tk.Frame(notebook, bg=self.colors["window_bg"])
        notebook.add(process_frame, text="Processes")
        
        tree = ttk.Treeview(
            process_frame,
            columns=("PID", "Name", "State", "Priority", "Memory", "CPU"),
            show="headings",
        )
        for col, width, anchor in [
            ("PID", 60, tk.W),
            ("Name", 180, tk.W),
            ("State", 120, tk.W),
            ("Priority", 80, tk.CENTER),
            ("Memory", 100, tk.E),
            ("CPU", 80, tk.E),
        ]:
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor=anchor)
        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        proc_scroll = ttk.Scrollbar(process_frame, orient=tk.VERTICAL, command=tree.yview)
        proc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=proc_scroll.set)
        
        def update_processes():
            tree.delete(*tree.get_children())
            for p in self.process_table:
                if p.state != ProcessState.TERMINATED:
                    tree.insert(
                        "",
                        "end",
                        values=(
                            p.pid,
                            p.name,
                            p.state.value,
                            p.priority,
                            f"{p.memory_kb} KB",
                            f"{p.cpu_usage:.1f}",
                        ),
                    )
            monitor_window.after(1000, update_processes)
        
        update_processes()
        
        # Memory tab
        memory_frame = tk.Frame(notebook, bg=self.colors["window_bg"])
        notebook.add(memory_frame, text="Memory")
        
        percent_used = (self.memory_allocated_kb / self.memory_total_kb) * 100
        mem_card = tk.Frame(memory_frame, bg=self.colors["window_bg"])
        mem_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            mem_card,
            text="Memory usage",
            font=self.fonts["ui_bold"],
            bg=self.colors["window_bg"],
            fg="#111827",
        ).pack(anchor=tk.W, pady=(4, 8))
        
        canvas = tk.Canvas(mem_card, height=32, bg=self.colors["control_bg"], highlightthickness=0)
        canvas.pack(fill=tk.X)
        canvas.update_idletasks()
        bar_width = max(canvas.winfo_width(), 760)
        used_width = (percent_used / 100) * bar_width
        canvas.create_rectangle(0, 0, bar_width, 32, fill=self.colors["control_bg"], width=0)
        canvas.create_rectangle(0, 0, used_width, 32, fill=self.colors["accent"], width=0)
        canvas.create_text(
            8,
            16,
            anchor=tk.W,
            text=f"{percent_used:.1f}% used",
            fill="#0f172a",
            font=self.fonts["ui_bold"],
        )
        
        details = tk.Label(
            mem_card,
            text=(
                f"Total: {self.memory_total_kb} KB\n"
                f"Allocated: {self.memory_allocated_kb} KB\n"
                f"Free: {self.memory_total_kb - self.memory_allocated_kb} KB\n"
                "Page size: 4 KB"
            ),
            font=self.fonts["mono"],
            justify=tk.LEFT,
            bg=self.colors["window_bg"],
            fg="#374151",
        )
        details.pack(anchor=tk.W, pady=12)
        
        # System tab
        system_frame = tk.Frame(notebook, bg=self.colors["window_bg"])
        notebook.add(system_frame, text="System")
        
        self.sys_info_label = tk.Label(
            system_frame,
            text="",
            font=self.fonts["mono"],
            justify=tk.LEFT,
            bg=self.colors["window_bg"],
            fg="#111827",
        )
        self.sys_info_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def update_system_info():
            h, m, s = self.get_uptime()
            running = len([p for p in self.process_table if p.state == ProcessState.RUNNING])
            ready = len([p for p in self.process_table if p.state == ProcessState.READY])
            total_mb = self.memory_total_kb // 1024
            used_mb = self.memory_allocated_kb // 1024
            info = (
                "Operating System OS\n"
                "--------------------\n"
                f"Kernel: Operating System OS v1.0\n"
                f"Architecture: x86-64 (64-bit)\n"
                f"Build Date: February 13, 2026\n\n"
                f"System Uptime: {h:02d}:{m:02d}:{s:02d}\n"
                f"Boot Time: {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"Memory: {total_mb} MB total / {used_mb} MB used\n"
                f"Processes: {running} running, {ready} ready, {len(self.process_table)} total (max {self.max_processes})\n"
                f"Files: {len(self.files)} entries\n"
                "Block size: 4 KB"
            )
            self.sys_info_label.config(text=info)
            monitor_window.after(2000, update_system_info)
        
        update_system_info()

    def open_mail_window(self):
        """Open mail client window"""
        mail_window = tk.Toplevel(self.root)
        mail_window.title("Mail - Operating System OS")
        mail_window.geometry("880x600")
        mail_window.configure(bg=self.colors["window_bg"], highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        
        header = tk.Frame(mail_window, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Mail", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text="Inbox preview", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=8)
        
        body = tk.Frame(mail_window, bg=self.colors["window_bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        folders = tk.Frame(body, bg="#0c1324", width=160, highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        folders.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        folders.pack_propagate(False)
        for name in ["Inbox", "Starred", "Sent", "Drafts", "Archive"]:
            tk.Button(
                folders, text=name, font=self.fonts["caption"],
                bg="#0f172a", fg=self.colors["text_primary"],
                activebackground="#1f2937", activeforeground=self.colors["text_primary"],
                relief=tk.FLAT, padx=10, pady=8,
            ).pack(fill=tk.X, padx=8, pady=4)
        
        right = tk.Frame(body, bg=self.colors["window_bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        msg_list = tk.Listbox(
            right, height=12, font=self.fonts["caption"],
            bg="#0f172a", fg=self.colors["text_primary"],
            selectbackground=self.colors["accent"], activestyle="none",
            highlightthickness=1, highlightbackground=self.colors["taskbar_border"],
        )
        msg_list.pack(fill=tk.X, padx=2, pady=(0, 10))
        
        messages = [
            "Design review at 2 PM",
            "Sprint planning notes",
            "Invoice #2024-118 ready",
            "Release checklist",
            "Reminder: team retro Friday",
        ]
        for msg in messages:
            msg_list.insert(tk.END, f"• {msg}")
        
        preview = tk.Frame(right, bg="#0c1324", highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        preview.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        tk.Label(preview, text="Preview", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg="#0c1324").pack(anchor=tk.W, padx=10, pady=8)
        self.mail_preview_body = tk.Label(
            preview,
            text="Select a message to preview.",
            font=self.fonts["caption"],
            fg=self.colors["text_muted"],
            bg="#0c1324",
            justify=tk.LEFT,
        )
        self.mail_preview_body.pack(anchor=tk.W, padx=10, pady=(0, 12))
        
        def on_select(event=None):
            idxs = msg_list.curselection()
            if not idxs:
                return
            msg = msg_list.get(idxs[0]).lstrip("• ").strip()
            self.mail_preview_body.config(text=f"From: team@os.local\nSubject: {msg}\n\nHi there,\nThis is a sample preview for \"{msg}\".")
        msg_list.bind("<<ListboxSelect>>", on_select)

    def open_media_player_window(self):
        """Open media player window"""
        media_window = tk.Toplevel(self.root)
        media_window.title("Media Player - Operating System OS")
        media_window.geometry("760x380")
        media_window.configure(bg=self.colors["window_bg"], highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        
        header = tk.Frame(media_window, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Media Player", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text="Now playing", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=8)
        
        body = tk.Frame(media_window, bg=self.colors["window_bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        top = tk.Frame(body, bg=self.colors["window_bg"])
        top.pack(fill=tk.X, pady=(0, 14))
        
        art = tk.Canvas(top, width=140, height=140, bg="#0c1324", highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        art.create_rectangle(10, 10, 130, 130, fill=self.colors["accent_pink"], outline="")
        art.pack(side=tk.LEFT)
        
        meta = tk.Frame(top, bg=self.colors["window_bg"])
        meta.pack(side=tk.LEFT, padx=16)
        tk.Label(meta, text="Neon Dreams", font=("Segoe UI", 16, "bold"), fg=self.colors["text_primary"], bg=self.colors["window_bg"]).pack(anchor=tk.W, pady=(4, 2))
        tk.Label(meta, text="Pulse / Theey", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_bg"]).pack(anchor=tk.W)
        
        progress = tk.Canvas(meta, width=360, height=10, bg="#0c1324", highlightthickness=0)
        progress.pack(anchor=tk.W, pady=12)
        progress.create_rectangle(0, 0, 360, 10, fill="#111827", width=0)
        progress.create_rectangle(0, 0, 220, 10, fill=self.colors["accent"], width=0)
        
        controls = tk.Frame(body, bg=self.colors["window_bg"])
        controls.pack(pady=6)
        for label in ["⏮", "⏯", "⏭"]:
            tk.Button(
                controls, text=label, font=("Segoe UI", 12, "bold"),
                bg="#0c1324", fg=self.colors["text_primary"],
                activebackground="#1f2937", activeforeground=self.colors["text_primary"],
                relief=tk.FLAT, padx=12, pady=8,
            ).pack(side=tk.LEFT, padx=6)
    
    def open_calendar_window(self):
        """Open calendar and weather widget window"""
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Calendar & Weather - Operating System OS")
        cal_window.geometry("520x420")
        cal_window.configure(bg=self.colors["window_bg"], highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        
        header = tk.Frame(cal_window, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Calendar & Weather", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        
        body = tk.Frame(cal_window, bg=self.colors["window_bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        now = datetime.now()
        tk.Label(body, text=now.strftime("%A, %B %d"), font=("Segoe UI", 16, "bold"), fg=self.colors["text_primary"], bg=self.colors["window_bg"]).pack(anchor=tk.W)
        tk.Label(body, text=now.strftime("%H:%M"), font=("Segoe UI", 24, "bold"), fg=self.colors["text_primary"], bg=self.colors["window_bg"]).pack(anchor=tk.W, pady=(4, 10))
        tk.Label(body, text="Partly Cloudy · 22°C", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_bg"]).pack(anchor=tk.W)
        
        forecast_frame = tk.Frame(body, bg=self.colors["window_bg"])
        forecast_frame.pack(fill=tk.X, pady=16)
        sample = [
            ("Mon", "☀️", "24° / 18°"),
            ("Tue", "⛅", "23° / 17°"),
            ("Wed", "☁️", "21° / 16°"),
            ("Thu", "🌧", "19° / 14°"),
            ("Fri", "☀️", "25° / 19°"),
        ]
        for day, icon, temp in sample:
            card = tk.Frame(forecast_frame, bg="#0c1324", padx=10, pady=8, highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
            card.pack(side=tk.LEFT, padx=6)
            tk.Label(card, text=day, font=self.fonts["caption"], fg=self.colors["text_primary"], bg="#0c1324").pack()
            tk.Label(card, text=icon, font=("Segoe UI", 14), fg=self.colors["text_primary"], bg="#0c1324").pack()
            tk.Label(card, text=temp, font=self.fonts["caption"], fg=self.colors["text_muted"], bg="#0c1324").pack()

    def open_settings_window(self):
        """Open settings window"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings - Operating System OS")
        settings_window.geometry("880x600")
        settings_window.configure(bg=self.colors["window_bg"], highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        
        header = tk.Frame(settings_window, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Settings", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text="System preferences", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=8)
        
        body = tk.Frame(settings_window, bg=self.colors["window_bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        nav = tk.Frame(body, bg="#0c1324", width=180, highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        nav.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        nav.pack_propagate(False)
        for section in ["Display", "Network", "Sound", "Privacy", "Updates"]:
            tk.Button(
                nav, text=section, font=self.fonts["caption"],
                bg="#0f172a", fg=self.colors["text_primary"],
                activebackground="#1f2937", activeforeground=self.colors["text_primary"],
                relief=tk.FLAT, padx=10, pady=8,
            ).pack(fill=tk.X, padx=8, pady=4)
        
        content = tk.Frame(body, bg=self.colors["window_bg"])
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        cards = [
            ("Display", "Brightness 75%\nNight light: On"),
            ("Network", "Wi‑Fi: Connected\nVPN: Off"),
            ("Sound", "Output: Speakers\nVolume: 60%"),
            ("Privacy", "Location: Off\nTelemetry: Basic"),
            ("Updates", "Last check: Today\nStatus: Up to date"),
        ]
        for title, desc in cards:
            card = tk.Frame(content, bg="#0c1324", highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
            card.pack(fill=tk.X, pady=6)
            tk.Label(card, text=title, font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg="#0c1324").pack(anchor=tk.W, padx=10, pady=(8, 2))
            tk.Label(card, text=desc, font=self.fonts["caption"], fg=self.colors["text_muted"], bg="#0c1324", justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(0, 8))

    def open_photos_window(self):
        """Open photos/gallery window"""
        photos_window = tk.Toplevel(self.root)
        photos_window.title("Photos - Operating System OS")
        photos_window.geometry("860x560")
        photos_window.configure(bg=self.colors["window_bg"], highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
        
        header = tk.Frame(photos_window, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Photos", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text="Library", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=8)
        
        grid = tk.Frame(photos_window, bg=self.colors["window_bg"])
        grid.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        for i in range(2):
            grid.columnconfigure(i, weight=1)
        for r in range(3):
            grid.rowconfigure(r, weight=1)
        
        for idx in range(6):
            r, c = divmod(idx, 2)
            frame = tk.Frame(grid, bg="#0c1324", highlightthickness=1, highlightbackground=self.colors["taskbar_border"])
            frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            canvas = tk.Canvas(frame, width=360, height=140, bg="#0f172a", highlightthickness=0)
            canvas.create_rectangle(10, 10, 340, 130, fill=self.colors["accent"], outline="")
            canvas.pack(fill=tk.BOTH, expand=True)
    
    def get_uptime(self):
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return hours, minutes, seconds
    
    def show_about(self):
        messagebox.showinfo(
            "About Operating System OS",
            "Operating System OS v1.0\nDesktop preview\n\n"
            "Built with Tkinter to mirror a familiar desktop layout. "
            "Includes a simple shell, file viewer, and system monitor on top of the simulated kernel.\n\n"
            "Specs: 12 GB simulated memory, up to 2048 processes, 4 KB blocks.\n"
            "Created February 13, 2026\n"
            "GitHub: github.com/Jskeen5822/Operating-System-OS",
        )
    
    def start_update_thread(self):
        """Update clock and status in taskbar"""
        def update():
            while True:
                try:
                    now = datetime.now().strftime("%H:%M")
                    h, m, s = self.get_uptime()
                    running = len([p for p in self.process_table if p.state == ProcessState.RUNNING])
                    status = f"Uptime {h:02d}:{m:02d}:{s:02d} · {running} running"
                    
                    self.time_label.config(text=now)
                    self.status_label.config(text=status)
                    if hasattr(self, "desktop_status_label"):
                        used_mb = self.memory_allocated_kb // 1024
                        total_mb = self.memory_total_kb // 1024
                        self.desktop_status_label.config(
                            text=(
                                f"Uptime {h:02d}:{m:02d}:{s:02d}\n"
                                f"Processes {len(self.process_table)}/{self.max_processes}\n"
                                f"Memory {used_mb} MB of {total_mb} MB"
                            )
                        )
                    time.sleep(1)
                except tk.TclError:
                    break
        
        thread = threading.Thread(target=update, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = OSDesktop(root)
    root.mainloop()

if __name__ == "__main__":
    main()
