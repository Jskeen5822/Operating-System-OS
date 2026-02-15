#!/usr/bin/env python3
"""
Operating System OS - Full Graphical Desktop Environment
A complete visual desktop with windows, file manager, system monitor, and terminal
"""


import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from enum import Enum
import time
import os
import random
from datetime import datetime

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class ProcessState(Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    TERMINATED = "TERMINATED"

class Process:
    def __init__(self, pid, name, priority=0) -> None:
        self.pid: Any = pid
        self.name: Any = name
        self.state: ProcessState = ProcessState.READY
        self.priority: int = priority
        self.memory_kb = 128 + (pid * 64)
        self.cpu_usage = 5 + (pid % 10)
        self.creation_time: float = time.time()

class OSDesktop:
    def __init__(self, root) -> None:
        self.root: Any = root
        self.root.title("Operating System OS - Desktop")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Make window fullscreen (compatible approach)
        self.root.attributes('-fullscreen', True)
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Don't use overrideredirect as it can cause X connection issues
        # The fullscreen attribute should be sufficient
        
        self.colors: dict[str, str] = {
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
        self.root.configure(bg=self.colors["wallpaper_dark"])
        self.fonts = {
            "ui": ("Segoe UI", 10),
            "ui_bold": ("Segoe UI", 10, "bold"),
            "title": ("Segoe UI", 16, "bold"),
            "caption": ("Segoe UI", 9),
            "mono": ("Cascadia Code", 10),
        }
        self.root.configure(bg=self.colors["wallpaper_dark"])
        
        # Add key bindings for exit (since we removed window decorations)
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Alt-F4>', lambda e: self.root.quit())
        self.root.bind('<Escape>', lambda e: self.root.quit())  # Escape to exit
        
        self.wallpaper_photo = None
        self.wallpaper_pil = None
        self.wallpaper_render = None
        self.wallpaper_source: str = ""
        self.app_icon_cache = {}
        self.task_manager_views = []  # Changed back to list
        self.cursor_styles = {}
        self.open_windows = {}  # Track open application windows
        self.window_z_order = []  # Track z-order for window stacking
        self._drag_data = {"x": 0, "y": 0, "window": None}  # Drag state
        self._create_custom_cursors()
        self._load_wallpaper_image()
        
                  
        self.process_table = []
        self.next_pid = 1
        self.current_process = None
        self.system_ticks = 0
        self.memory_total_kb = 12582912               
        self.memory_allocated_kb = 524288               
        self.max_processes = 2048
        self.start_time: float = time.time()
        
                     
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
        
                             
        self.create_process("idle", priority=0)
        self.current_process = self.process_table[0]
        self.current_process.state = ProcessState.RUNNING
        
                   
        self.setup_ui()
        self.start_update_thread()
        
                        
        self.show_boot_screen()
    
    def setup_ui(self) -> None:
        try:
            ttk.Style().theme_use("clam")
        except:
            pass

        self.desktop = tk.Frame(self.root, bg=self.colors["wallpaper_dark"], cursor=self.cursor_styles['default'])
        self.desktop.pack(fill=tk.BOTH, expand=True)

        self.wallpaper_canvas = tk.Canvas(
            self.desktop,
            bg=self.colors["wallpaper_dark"],
            highlightthickness=0,
        )
        self.wallpaper_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.wallpaper_canvas.bind("<Configure>", self.draw_wallpaper)

        self.build_top_info_bar()
        self.build_bottom_dock()
        self.build_start_button()
        self.create_start_menu()

        self.root.bind("<Button-1>", self._maybe_close_start_menu)

    def build_top_info_bar(self) -> None:
        self.topbar_shell, self.topbar = self._create_rounded_panel(
            self.desktop,
            bg=self.colors["taskbar"],
            border=self.colors["taskbar_border"],
            radius=18,
            inner_pad=10,
        )
        self.topbar_shell.place(relx=0.5, y=10, anchor="n", relwidth=0.98, height=54)

        left = tk.Frame(self.topbar, bg=self.colors["taskbar"])
        left.pack(side=tk.LEFT)
        tk.Label(
            left,
            text="Operating System OS",
            font=self.fonts["ui_bold"],
            bg=self.colors["taskbar"],
            fg=self.colors["text_primary"],
        ).pack(side=tk.LEFT, padx=(4, 10))

        center = tk.Frame(self.topbar, bg=self.colors["taskbar"])
        center.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.status_label = tk.Label(
            center,
            text="Uptime 0:00:00 · 1 running",
            font=self.fonts["caption"],
            bg=self.colors["taskbar"],
            fg=self.colors["text_muted"],
        )
        self.status_label.pack(side=tk.RIGHT, padx=(0, 10))

        self.time_label = tk.Label(
            center,
            text="",
            font=self.fonts["ui_bold"],
            bg=self.colors["taskbar"],
            fg=self.colors["text_primary"],
        )
        self.time_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def draw_wallpaper(self, event) -> None:
        """Paint the desktop wallpaper."""
        self.wallpaper_canvas.delete("wallpaper")


        if self.wallpaper_pil and PIL_AVAILABLE and event.width > 0 and event.height > 0:
            img_w, img_h = self.wallpaper_pil.size
            scale = max(event.width / img_w, event.height / img_h)
            new_size: tuple[int, int] = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
            if PIL_AVAILABLE:
                try:
                    from PIL import Image, ImageTk                
                    # Use high-quality resampling for better image quality
                    resized = self.wallpaper_pil.resize(new_size, Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.BICUBIC)
                                                
                    left = max(0, (resized.width - event.width) // 2)
                    top = max(0, (resized.height - event.height) // 2)
                    cropped = resized.crop((left, top, left + event.width, top + event.height))
                    
                    # Apply slight sharpening to improve clarity
                    if hasattr(ImageFilter, 'SHARPEN'):
                        from PIL import ImageFilter
                        cropped = cropped.filter(ImageFilter.SHARPEN)
                    
                    self.wallpaper_render = ImageTk.PhotoImage(cropped)
                    self.wallpaper_canvas.create_image(0, 0, image=self.wallpaper_render, anchor="nw", tags="wallpaper")
                    return
                except Exception:
                    pass

        if self.wallpaper_photo:
            self.wallpaper_canvas.create_image(
                event.width // 2,
                event.height // 2,
                image=self.wallpaper_photo,
                anchor="center",
                tags="wallpaper",
            )
            return

        top: tuple[int, ...] = self._hex_to_rgb(self.colors["wallpaper_glow"])
        mid: tuple[int, ...] = self._hex_to_rgb(self.colors["wallpaper_mid"])
        bottom: tuple[int, ...] = self._hex_to_rgb(self.colors["wallpaper_dark"])
        steps: int = max(event.height, 1)

        for i in range(steps):
            ratio = i / steps
            if ratio < 0.35:
                blend = self._blend(top, mid, ratio / 0.35)
            else:
                blend = self._blend(mid, bottom, (ratio - 0.35) / 0.65)
            color = f"#{blend[0]:02x}{blend[1]:02x}{blend[2]:02x}"
            self.wallpaper_canvas.create_line(0, i, event.width, i, fill=color, tags="wallpaper")
    
    def _hex_to_rgb(self, value) -> tuple[int, ...]:
        value = value.lstrip("#")
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))
    
    def _blend(self, start, end, ratio) -> tuple[int, ...]:
        return tuple(int(start[i] + (end[i] - start[i]) * ratio) for i in range(3))
    
    def _create_custom_cursors(self) -> None:
        """Set up enhanced cursor styling"""
        # Use enhanced system cursors with better visual appeal
        self.cursor_styles = {
            'default': 'arrow',
            'clickable': 'hand2',
            'text': 'xterm',
            'resize': 'sizing'
        }
    
    def create_app_window(self, app_name, title, width, height):
        """Create an embedded application window within the desktop"""
        # Close existing window if it's already open
        if app_name in self.open_windows:
            self.close_app_window(app_name)
            return None
        
        # Create main window frame with title bar
        window_frame = tk.Frame(self.desktop, bg=self.colors["window_header"], relief=tk.RAISED, bd=1)
        
        # Title bar
        title_bar = tk.Frame(window_frame, bg=self.colors["window_header"], height=30, relief=tk.FLAT, bd=0)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        
        # Title label
        title_label = tk.Label(title_bar, text=title, font=self.fonts["ui_bold"], 
                              fg=self.colors["text_primary"], bg=self.colors["window_header"])
        title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Window controls
        controls_frame = tk.Frame(title_bar, bg=self.colors["window_header"])
        controls_frame.pack(side=tk.RIGHT, padx=5)
        
        # Minimize button
        minimize_btn = tk.Button(controls_frame, text="−", font=("Arial", 10, "bold"),
                                bg="#fbbf24", fg="white", width=3, height=1,
                                relief=tk.FLAT, bd=0,
                                command=lambda: self.minimize_app_window(app_name))
        minimize_btn.pack(side=tk.LEFT, padx=2)
        
        # Close button
        close_btn = tk.Button(controls_frame, text="×", font=("Arial", 10, "bold"),
                             bg="#ef4444", fg="white", width=3, height=1,
                             relief=tk.FLAT, bd=0,
                             command=lambda: self.close_app_window(app_name))
        close_btn.pack(side=tk.LEFT, padx=2)
        
        # Content area
        content_frame = tk.Frame(window_frame, bg=self.colors["window_bg"], relief=tk.FLAT, bd=0)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Store window reference
        self.open_windows[app_name] = {
            'frame': window_frame,
            'title_bar': title_bar,
            'content': content_frame,
            'title_label': title_label,
            'minimized': False
        }
        
        # Make window draggable with proper reference
        self._make_window_draggable(window_frame, title_bar, app_name)
        
        # Add to z-order
        self.window_z_order.append(app_name)
        
        # Position window (cascade style)
        x_offset = 50 + (len(self.open_windows) * 30)
        y_offset = 50 + (len(self.open_windows) * 30)
        window_frame.place(x=x_offset, y=y_offset, width=width, height=height)
        
        return content_frame
    
    def _make_window_draggable(self, window_frame, title_bar, app_name):
        """Make window draggable by title bar with improved performance"""
        
        def start_drag(event):
            # Store initial position and window reference
            self._drag_data["x"] = event.x_root - window_frame.winfo_x()
            self._drag_data["y"] = event.y_root - window_frame.winfo_y()
            self._drag_data["window"] = window_frame
            
        def drag(event):
            if self._drag_data["window"]:
                # Calculate new position
                new_x = event.x_root - self._drag_data["x"]
                new_y = event.y_root - self._drag_data["y"]
                
                # Get desktop boundaries
                desktop_width = self.desktop.winfo_width()
                desktop_height = self.desktop.winfo_height()
                window_width = window_frame.winfo_width()
                window_height = window_frame.winfo_height()
                
                # Constrain to desktop bounds
                new_x = max(0, min(new_x, desktop_width - window_width))
                new_y = max(0, min(new_y, desktop_height - window_height))
                
                # Update position
                window_frame.place(x=new_x, y=new_y)
                
        def stop_drag(event):
            self._drag_data["window"] = None
            
        title_bar.bind("<Button-1>", start_drag)
        title_bar.bind("<B1-Motion>", drag)
        title_bar.bind("<ButtonRelease-1>", stop_drag)
        
        # Also bind to the title label for better drag coverage
        if app_name in self.open_windows:
            title_label = self.open_windows[app_name]['title_label']
            title_label.bind("<Button-1>", start_drag)
            title_label.bind("<B1-Motion>", drag)
            title_label.bind("<ButtonRelease-1>", stop_drag)
    
    def bring_to_front(self, app_name):
        """Bring window to front"""
        if app_name in self.open_windows:
            # Remove from current position and add to end
            if app_name in self.window_z_order:
                self.window_z_order.remove(app_name)
            self.window_z_order.append(app_name)
            
            # Raise the window
            self.open_windows[app_name]['frame'].lift()
    
    def minimize_app_window(self, app_name):
        """Minimize application window"""
        if app_name in self.open_windows:
            self.open_windows[app_name]['minimized'] = True
            self.open_windows[app_name]['frame'].place_forget()
    
    def close_app_window(self, app_name):
        """Close application window"""
        if app_name in self.open_windows:
            self.open_windows[app_name]['frame'].destroy()
            del self.open_windows[app_name]
            if app_name in self.window_z_order:
                self.window_z_order.remove(app_name)
    
    def _load_wallpaper_image(self) -> None:
        candidates: list[str] = [
            "wallpaper_tree.png",
            "wallpaper_tree.jpg",
            "wallpaper_tree.jpeg",
            "wallpaper_tree.ppm",
            "wallpaper_tree.pgm",
            "wallpaper_tree.gif",
        ]
        base_dir: str = os.path.dirname(os.path.abspath(__file__))
        search_dirs: list[str] = [
            os.path.join(base_dir, "assets", "wallpaper"),
            os.path.join(base_dir, "assets"),
            base_dir,
        ]
        self.wallpaper_pil = None
        self.wallpaper_photo = None
        self.wallpaper_source: str = ""
        pil_image = None
        if PIL_AVAILABLE:
            pil_image = Image
        for folder in search_dirs:
            for name in candidates:
                path = os.path.join(folder, name)
                if not os.path.exists(path):
                    continue
                if pil_image is not None:
                    try:
                        self.wallpaper_pil = pil_image.open(path).convert("RGB")
                        self.wallpaper_source = path
                        return
                    except Exception:
                        self.wallpaper_pil = None
                if os.path.splitext(name)[1].lower() not in {".png", ".gif", ".ppm", ".pgm"}:
                    continue
                try:
                    self.wallpaper_photo = tk.PhotoImage(file=path)
                    self.wallpaper_source = path
                    return
                except Exception:
                    self.wallpaper_photo = None
        fallback_path: str = os.path.join(base_dir, "assets", "wallpaper", "wallpaper_fallback.ppm")
        os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
        if not os.path.exists(fallback_path):
            self._generate_fallback_wallpaper(fallback_path)
        try:
            self.wallpaper_photo = tk.PhotoImage(file=fallback_path)
            self.wallpaper_source = fallback_path
        except Exception:
            self.wallpaper_photo = None

    def _generate_fallback_wallpaper(self, path) -> None:
        """Generate a static PPM wallpaper that Tk can load without Pillow."""
        width, height = 1920, 1200

        top: tuple[int, ...] = self._hex_to_rgb(self.colors["wallpaper_light"])
        mid: tuple[int, ...] = self._hex_to_rgb(self.colors["wallpaper_mid"])
        bottom: tuple[int, ...] = self._hex_to_rgb(self.colors["wallpaper_dark"])
        try:
            with open(path, "wb") as f:
                f.write(f"P6\n{width} {height}\n255\n".encode("ascii"))
                for y in range(height):
                    ratio = y / max(1, height - 1)
                    if ratio < 0.45:
                        base = self._blend(top, mid, ratio / 0.45)
                    else:
                        base = self._blend(mid, bottom, (ratio - 0.45) / 0.55)
                    row = bytearray()
                    for x in range(width):
                        xr = x / max(1, width - 1)
                        glow = int(30 * (1 - abs(0.5 - xr) * 2))
                        r: int = max(0, min(255, base[0] + glow // 3))
                        g: int = max(0, min(255, base[1] + glow // 2))
                        b: int = max(0, min(255, base[2] + glow))
                        row.extend((r, g, b))
                    f.write(row)
        except Exception:
            pass

    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        radius: int = max(1, int(radius))
        radius: int = min(radius, int((x2 - x1) / 2), int((y2 - y1) / 2))
        points = [
            x1 + radius, y1, x1 + radius, y1,
            x2 - radius, y1, x2 - radius, y1,
            x2, y1, x2, y1 + radius,
            x2, y1 + radius, x2, y2 - radius,
            x2, y2 - radius, x2, y2,
            x2 - radius, y2, x2 - radius, y2,
            x1 + radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius,
            x1, y2 - radius, x1, y1 + radius,
            x1, y1 + radius, x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, splinesteps=24, **kwargs)

    def _create_rounded_panel(self, parent, bg, border, radius=16, inner_pad=10) -> tuple[tk.Canvas, tk.Frame]:
        parent_bg = parent.cget("bg")
        shell = tk.Canvas(parent, bg=parent_bg, highlightthickness=0, bd=0)
        body = tk.Frame(shell, bg=bg, highlightthickness=0, bd=0)
        body_id: int = shell.create_window(inner_pad, inner_pad, anchor="nw", window=body)

        def redraw(event=None) -> None:
            w: int = max(shell.winfo_width(), 2)
            h: int = max(shell.winfo_height(), 2)
            shell.delete("panel")
            self._draw_rounded_rect(
                shell,
                1,
                1,
                w - 1,
                h - 1,
                radius=min(radius, (w - 2) // 2, (h - 2) // 2),
                fill=bg,
                outline=border,
                width=1,
                tags="panel",
            )
            shell.coords(body_id, inner_pad, inner_pad)
            shell.itemconfigure(
                body_id,
                width=max(1, w - (inner_pad * 2)),
                height=max(1, h - (inner_pad * 2)),
            )
            shell.tag_lower("panel")

        shell.bind("<Configure>", redraw)
        shell.after(1, redraw)
        return shell, body

    def _load_app_icon_image(self, icon_name, max_size=52):
        cache_key: str = f"{icon_name}:{max_size}"
        if cache_key in self.app_icon_cache:
            return self.app_icon_cache[cache_key]

        base_dir: str = os.path.dirname(os.path.abspath(__file__))
        candidates: list[str] = [
            os.path.join(base_dir, "app_icons", f"{icon_name}.png"),
            os.path.join(base_dir, "app_icons", f"{icon_name}.gif"),
            os.path.join(base_dir, "assets", "app_icons", f"{icon_name}.png"),
            os.path.join(base_dir, "assets", "app_icons", f"{icon_name}.gif"),
        ]

        for path in candidates:
            if not os.path.exists(path):
                continue
            try:
                image = tk.PhotoImage(file=path)
                scale: int = max(1, image.width() // max_size, image.height() // max_size)
                if scale > 1:
                    image: tk.PhotoImage = image.subsample(scale, scale)
                self.app_icon_cache[cache_key] = image
                return image
            except Exception:
                continue
        self.app_icon_cache[cache_key] = None
        return None
    
    def draw_icon(self, canvas, icon_name, color) -> None:
        """Draw a simple vector-style icon on a Tk canvas"""
        canvas.delete("all")
        bg = "#0f172a"
        stroke = "#111827"
        self._draw_rounded_rect(canvas, 3, 3, 47, 47, radius=10, outline=stroke, fill=bg, width=1)
        
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
        elif icon_name == "tasks":
            canvas.create_rectangle(9, 10, 41, 38, outline=stroke, fill="#0b1224", width=1)
            canvas.create_rectangle(13, 28, 17, 34, outline="", fill=color)
            canvas.create_rectangle(21, 22, 25, 34, outline="", fill=color)
            canvas.create_rectangle(29, 16, 33, 34, outline="", fill=color)
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
    
    def build_desktop_icons(self) -> None:
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
            
            def bind_launch(widget, cmd=command) -> None:
                widget.bind("<Double-Button-1>", lambda _e: cmd())
                widget.bind("<Button-1>", self._maybe_close_start_menu)
            
            for widget in (tile, icon_canvas, label_widget):
                bind_launch(widget)
    
    def build_left_dock(self) -> None:
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
            btn = tk.Frame(dock, bg="#0c1324", padx=10, pady=6, highlightthickness=1, highlightbackground=color, cursor=self.cursor_styles['clickable'])
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
    
    def build_bottom_dock(self) -> None:
        """Centered dock with icon-first launch targets."""
        icons = [
            ("Home", self.open_file_manager, "#60a5fa", "folder"),
            ("Terminal", self.open_terminal_window, "#34d399", "terminal"),
            ("Monitor", self.open_system_monitor, "#f59e0b", "monitor"),
            ("Tasks", self.open_task_manager_window, "#38bdf8", "tasks"),
            ("Mail", self.open_mail_window, "#a78bfa", "mail"),
            ("Media", self.open_media_player_window, "#f472b6", "media"),
            ("Calendar", self.open_calendar_window, "#22c55e", "calendar"),
            ("Settings", self.open_settings_window, "#9ca3af", "settings"),
        ]

        dock_width: int = (len(icons) * 84) + 24
        self.dock_shell, dock = self._create_rounded_panel(
            self.desktop,
            bg="#0c1324",
            border=self.colors["taskbar_border"],
            radius=24,
            inner_pad=8,
        )
        self.dock_shell.place(relx=0.5, rely=1.0, anchor="s", y=-18, width=dock_width, height=108)

        for label, cmd, color, icon_name in icons:
            tile = tk.Frame(dock, bg="#0c1324", padx=6, pady=5, cursor=self.cursor_styles['clickable'])
            tile.pack(side=tk.LEFT, padx=2)

            app_img = self._load_app_icon_image(icon_name, max_size=48)
            if app_img is not None:
                icon_widget = tk.Label(tile, image=app_img, bg="#0c1324", cursor=self.cursor_styles['clickable'])
                icon_widget.image = app_img
            else:
                icon_widget = tk.Canvas(tile, width=48, height=48, bg="#0c1324", highlightthickness=0, cursor=self.cursor_styles['clickable'])
                self.draw_icon(icon_widget, icon_name, color)
            icon_widget.pack()

            label_widget = tk.Label(
                tile,
                text=label,
                font=self.fonts["caption"],
                fg=self.colors["text_primary"],
                bg="#0c1324",
                cursor=self.cursor_styles['clickable'],
            )
            label_widget.pack(pady=(4, 0))

            for widget in (tile, icon_widget, label_widget):
                widget.bind("<Button-1>", lambda _e, c=cmd: self._launch_from_menu(c))

    # build_taskbar_content removed; replaced by build_top_info_bar

    def build_start_button(self) -> None:
        self.start_shell, holder = self._create_rounded_panel(
            self.desktop,
            bg=self.colors["taskbar"],
            border=self.colors["taskbar_border"],
            radius=18,
            inner_pad=5,
        )
        self.start_shell.place(x=16, rely=1.0, anchor="sw", y=-16, width=102, height=46)
        self.start_button = tk.Button(
            holder,
            text="Start",
            font=self.fonts["ui_bold"],
            command=self.toggle_start_menu,
            bg=self.colors["accent"],
            fg="white",
            bd=0,
            relief=tk.FLAT,
            activebackground=self.colors["accent"],
            activeforeground="white",
            cursor=self.cursor_styles['clickable'],
            padx=12,
            pady=6,
        )
        self.start_button.pack(fill=tk.BOTH, expand=True)
    
    def create_start_menu(self) -> None:
        """Create a compact start menu listing the key apps"""
        self.start_menu_visible = False
        self.start_menu_shell, self.start_menu = self._create_rounded_panel(
            self.desktop,
            bg=self.colors["menu_bg"],
            border=self.colors["taskbar_border"],
            radius=20,
            inner_pad=12,
        )
        self.start_menu_shell.place_forget()

        header = tk.Frame(self.start_menu, bg=self.colors["menu_bg"])
        header.pack(fill=tk.X, pady=(2, 6))
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
            ("Task Manager", "View live processes and memory", self.open_task_manager_window),
            ("System Monitor", "Inspect processes and memory", self.open_system_monitor),
            ("Mail", "Check recent messages", self.open_mail_window),
            ("Media Player", "Listen to music", self.open_media_player_window),
            ("Calendar", "View date and weather", self.open_calendar_window),
            ("Settings", "System preferences", self.open_settings_window),
            ("About", "System information", self.show_about),
        ]
        
        for name, desc, cmd in menu_items:
            item = tk.Frame(self.start_menu, bg=self.colors["menu_item"], highlightthickness=0, cursor=self.cursor_styles['clickable'])
            item.pack(fill=tk.X, pady=3)
            tk.Label(
                item,
                text=name,
                font=self.fonts["ui_bold"],
                fg=self.colors["text_primary"],
                bg=self.colors["menu_item"],
                cursor=self.cursor_styles['clickable'],
            ).pack(anchor=tk.W, padx=10, pady=(8, 0))
            tk.Label(
                item,
                text=desc,
                font=self.fonts["caption"],
                fg=self.colors["text_muted"],
                bg=self.colors["menu_item"],
                cursor=self.cursor_styles['clickable'],
            ).pack(anchor=tk.W, padx=10, pady=(0, 8))
            
            item.bind("<Button-1>", lambda _e, c=cmd: self._launch_from_menu(c))
            for child in item.winfo_children():
                child.bind("<Button-1>", lambda _e, c=cmd: self._launch_from_menu(c))
        
        footer = tk.Frame(self.start_menu, bg=self.colors["menu_bg"])
        footer.pack(fill=tk.X, pady=(8, 0))
        tk.Button(
            footer,
            text="Settings",
            command=self.open_settings_window,
            font=self.fonts["caption"],
            bg=self.colors["taskbar_border"],
            fg=self.colors["text_primary"],
            relief=tk.FLAT,
            activebackground=self.colors["taskbar_border"],
            activeforeground=self.colors["text_primary"],
            cursor=self.cursor_styles['clickable'],
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
            activeforeground=self.colors["text_primary"],
            cursor=self.cursor_styles['clickable'],
        ).pack(side=tk.LEFT)
    
    def toggle_start_menu(self) -> None:
        if self.start_menu_visible:
            self._hide_start_menu()
        else:
            self._show_start_menu()
    
    def _show_start_menu(self) -> None:
        self.start_menu_shell.update_idletasks()
        self.start_menu_shell.place(x=16, y=70)
        self.start_menu_visible = True
    
    def _hide_start_menu(self) -> None:
        self.start_menu_shell.place_forget()
        self.start_menu_visible = False
    
    def _launch_from_menu(self, command) -> None:
        self._hide_start_menu()
        command()
    
    def _maybe_close_start_menu(self, event=None) -> None:
        if not self.start_menu_visible:
            return
        widget = event.widget if event else None
        if widget and (self._is_child_of(widget, self.start_menu_shell) or self._is_child_of(widget, self.start_button)):
            return
        self._hide_start_menu()
    
    def _is_child_of(self, widget, parent) -> bool:
        while widget:
            if widget == parent:
                return True
            widget = widget.master
        return False
    
    def show_boot_screen(self) -> None:
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
        
        boot_messages: list[str] = [
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
        
        def add_message(index=0) -> None:
            if index < len(boot_messages):
                text_widget.config(state=tk.NORMAL)
                text_widget.insert(tk.END, boot_messages[index] + "\n")
                text_widget.see(tk.END)
                text_widget.config(state=tk.DISABLED)
                boot_window.after(200, lambda: add_message(index + 1))
            else:
                boot_window.after(1000, boot_window.destroy)
        
        add_message()
    
    def create_process(self, name, priority=0) -> None | Process:
        if len(self.process_table) >= self.max_processes:
            return None
        process: Process = Process(self.next_pid, name, priority)
        self.process_table.append(process)
        self.next_pid += 1
        return process

    
    def open_file_manager(self) -> None:
        """Open file manager window"""
        content_frame = self.create_app_window("file_manager", "File Manager", 800, 600)
        if content_frame is None:
            return
        
        # Header
        header = tk.Frame(content_frame, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="File Manager", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text=f"/{self.current_directory}", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=8)
        
        # File list
        list_frame = tk.Frame(content_frame, bg=self.colors["window_bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        file_list = tk.Listbox(
            list_frame,
            font=self.fonts["ui"],
            bg="#0c1324",
            fg=self.colors["text_primary"],
            selectbackground=self.colors["accent"],
            selectforeground="white",
            yscrollcommand=scrollbar.set,
            highlightthickness=1,
            highlightbackground=self.colors["taskbar_border"]
        )
        file_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=file_list.yview)
        
        # Populate file list
        for name, info in sorted(self.files.items()):
            if name != "/":
                display_name = name.lstrip("/")
                file_list.insert(tk.END, f"{info['icon']} {display_name}")
        
        # Bring to front when clicked
        content_frame.bind("<Button-1>", lambda e: self.bring_to_front("file_manager"))
    
    def open_terminal_window(self) -> None:
        content_frame = self.create_app_window("terminal", "Terminal", 900, 620)
        if content_frame is None:
            return
        
        # Header
        header = tk.Frame(content_frame, bg=self.colors["window_header"])
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
        
        # Terminal content
        terminal_frame = tk.Frame(content_frame, bg="#0b0f19")
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        output_text = tk.Text(
            terminal_frame,
            bg="#0b0f19",
            fg="#22c55e",
            font=self.fonts["mono"],
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD,
            state=tk.DISABLED,
            insertbackground=self.colors["accent"]
        )
        output_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))
        
        # Input frame
        input_frame = tk.Frame(terminal_frame, bg="#0b0f19")
        input_frame.pack(fill=tk.X, padx=8, pady=(4, 8))
        
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
            insertbackground=self.colors["accent"],
            font=self.fonts["mono"],
            relief=tk.FLAT,
            cursor=self.cursor_styles['text'],
        )
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        def execute_command(event=None) -> None:
            cmd: str = input_entry.get().strip()
            input_entry.delete(0, tk.END)
            output_text.config(state=tk.NORMAL)
            if cmd:
                output_text.insert(tk.END, f"> {cmd}\n")
                if cmd == "help":
                    output_text.insert(tk.END, "Available commands: help, ps, exec, meminfo, ls, exit, clear\n")
                elif cmd == "ps":
                    output_text.insert(tk.END, "PID\tNAME\t\tSTATE\t\tCPU\tMEM\n")
                    for proc in self.process_table[:10]:  # Show first 10 processes
                        output_text.insert(tk.END, f"{proc.pid}\t{proc.name}\t\t{proc.state.value}\t{proc.cpu_usage}%\t{proc.memory_kb}KB\n")
                elif cmd.startswith("exec "):
                    parts = cmd.split(" ", 1)
                    if len(parts) > 1:
                        self.create_process(parts[1])
                        output_text.insert(tk.END, f"Process created: {parts[1]}\n")
                    else:
                        output_text.insert(tk.END, "Usage: exec <name>\n")
                elif cmd == "meminfo":
                    free: int = self.memory_total_kb - self.memory_allocated_kb
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
                    self.close_app_window("terminal")
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
        
        # Bring to front when clicked
        content_frame.bind("<Button-1>", lambda e: self.bring_to_front("terminal"))
    
    def open_system_monitor(self) -> None:
        content_frame = self.create_app_window("system_monitor", "System Monitor", 980, 720)
        if content_frame is None:
            return
        
        # Header
        header = tk.Frame(content_frame, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="System Monitor", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        
        # Content area
        monitor_frame = tk.Frame(content_frame, bg=self.colors["window_bg"])
        monitor_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # Process list
        tree_frame = tk.Frame(monitor_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=("PID", "Name", "State", "CPU", "Memory"), show="headings", height=15)
        tree.heading("PID", text="PID")
        tree.heading("Name", text="Process Name")
        tree.heading("State", text="State")
        tree.heading("CPU", text="CPU %")
        tree.heading("Memory", text="Memory (KB)")
        
        tree.column("PID", width=80)
        tree.column("Name", width=200)
        tree.column("State", width=100)
        tree.column("CPU", width=80)
        tree.column("Memory", width=120)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        def populate_tree():
            for item in tree.get_children():
                tree.delete(item)
            for proc in self.process_table:
                tree.insert("", "end", values=(proc.pid, proc.name, proc.state.value, f"{proc.cpu_usage}%", proc.memory_kb))
        
        populate_tree()
        
        # Bring to front when clicked
        content_frame.bind("<Button-1>", lambda e: self.bring_to_front("system_monitor"))
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
        notebook = ttk.Notebook(holder)
        notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        # ...existing code...
        toolbar = tk.Frame(holder, bg=self.colors["window_bg"])
        toolbar.pack(fill=tk.X, padx=12, pady=(10, 6))
        list_frame = tk.Frame(holder, bg=self.colors["window_bg"])
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
        def populate_tree() -> None:
            tree.delete(*tree.get_children())
            for fname, info in sorted(self.files.items()):
                if fname == "/":
                    continue
                name: str = fname.lstrip("/")
                ftype: str = "Folder" if info["type"] == "directory" else "File"
                size: str = "-" if info["type"] == "directory" else f"{info['size']} bytes"
                tree.insert("", "end", values=(name, ftype, size))
        def new_file() -> None:
            name: str | None = simpledialog.askstring("New File", "File name:")
            if name:
                self.files[f"/{name}"] = {"type": "file", "icon": "", "size": 0}
                populate_tree()
        def new_folder() -> None:
            name: str | None = simpledialog.askstring("New Folder", "Folder name:")
            if name:
                self.files[f"/{name}"] = {"type": "directory", "icon": "", "size": 0}
                populate_tree()
        def delete_item() -> None:
            selected: tuple[str, ...] = tree.selection()
            if not selected:
                return
            name: tk.Any | str = tree.item(selected[0], "values")[0]
            path: str = f"/{name}"
            if path in self.files and messagebox.askyesno("Delete", f"Delete '{name}'?"):
                del self.files[path]
                populate_tree()
        def show_properties(event=None) -> None:
            selected: tuple[str, ...] = tree.selection()
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
    
    def open_system_monitor(self) -> None:
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
        
        def update_processes() -> None:
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
        
                    
        memory_frame = tk.Frame(notebook, bg=self.colors["window_bg"])
        notebook.add(memory_frame, text="Memory")
        
        percent_used: float = (self.memory_allocated_kb / self.memory_total_kb) * 100
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
        bar_width: int = max(canvas.winfo_width(), 760)
        used_width: float = (percent_used / 100) * bar_width
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
        
        def update_system_info() -> None:
            h, m, s = self.get_uptime()
            running: int = len([p for p in self.process_table if p.state == ProcessState.RUNNING])
            ready: int = len([p for p in self.process_table if p.state == ProcessState.READY])
            total_mb: int = self.memory_total_kb // 1024
            used_mb: int = self.memory_allocated_kb // 1024
            info: str = (
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

    def open_task_manager_window(self) -> None:
        content_frame = self.create_app_window("task_manager", "Task Manager", 760, 460)
        if content_frame is None:
            return
        
        # Header
        header = tk.Frame(content_frame, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="Task Manager",
            font=self.fonts["ui_bold"],
            fg=self.colors["text_primary"],
            bg=self.colors["window_header"],
        ).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(
            header,
            text="Live processes and utilization",
            font=self.fonts["caption"],
            fg=self.colors["text_muted"],
            bg=self.colors["window_header"],
        ).pack(side=tk.LEFT, padx=8)
        
        # Content area
        body = tk.Frame(content_frame, bg=self.colors["window_bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        
        summary = tk.Label(
            body,
            text="Uptime 00:00:00 · 1 process",
            font=self.fonts["caption"],
            fg=self.colors["text_muted"],
            bg=self.colors["window_bg"],
        )
        summary.pack(anchor=tk.W, pady=(0, 8))
        
        columns = ("PID", "Name", "State", "Priority", "Memory", "CPU")
        tree = ttk.Treeview(body, columns=columns, show="headings")
        for col, width, anchor in [
            ("PID", 80, tk.W),
            ("Name", 180, tk.W),
            ("State", 120, tk.W),
            ("Priority", 90, tk.CENTER),
            ("Memory", 120, tk.E),
            ("CPU", 90, tk.E),
        ]:
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor=anchor)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(body, orient=tk.VERTICAL, command=tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scroll.set)
        
        footer = tk.Label(
            content_frame,
            text="Memory 512 MB / 12288 MB",
            font=self.fonts["caption"],
            fg=self.colors["text_muted"],
            bg=self.colors["window_bg"],
        )
        footer.pack(anchor=tk.W, padx=12, pady=(0, 10))
        
        view = {
            "summary": summary,
            "tree": tree,
            "footer": footer,
        }
        self.task_manager_views.append(view)
        
        def refresh() -> None:
            if "task_manager" in self.open_windows:
                # Update tree with current processes
                for item in tree.get_children():
                    tree.delete(item)
                for proc in self.process_table:
                    tree.insert("", "end", values=(
                        proc.pid, proc.name, proc.state.value, 
                        proc.priority, f"{proc.memory_kb}KB", f"{proc.cpu_usage}%"
                    ))
                
                # Update summary
                uptime = self.get_uptime()
                summary.config(text=f"Uptime {uptime[0]}:{uptime[1]:02d}:{uptime[2]:02d} · {len(self.process_table)} processes")
                
                # Update footer
                footer.config(text=f"Memory {self.memory_allocated_kb // 1024} MB / {self.memory_total_kb // 1024} MB")
                
                # Schedule next refresh
                self.root.after(2000, refresh)
        
        refresh()
        
        # Bring to front when clicked
        content_frame.bind("<Button-1>", lambda e: self.bring_to_front("task_manager"))

    def _remove_task_manager_view(self, view) -> None:
        if view in self.task_manager_views:
            self.task_manager_views.remove(view)

    def _refresh_task_manager_view(self, view) -> None:
        window = view.get("window")
        if not window or not window.winfo_exists():
            self._remove_task_manager_view(view)
            return

        h, m, s = self.get_uptime()
        active = [p for p in self.process_table if p.state != ProcessState.TERMINATED]
        summary = view["summary"]
        summary.config(text=f"Uptime {h:02d}:{m:02d}:{s:02d} · {len(active)} processes")

        tree = view["tree"]
        tree.delete(*tree.get_children())
        for p in active:
            tree.insert(
                "",
                tk.END,
                values=(
                    p.pid,
                    p.name,
                    p.state.value,
                    p.priority,
                    f"{p.memory_kb} KB",
                    f"{p.cpu_usage:.1f}%",
                ),
            )

        view["footer"].config(
            text=f"Memory {self.memory_allocated_kb // 1024} MB / {self.memory_total_kb // 1024} MB"
        )

    def open_mail_window(self) -> None:
        mail_window = tk.Toplevel(self.root)
        mail_window.title("Mail - Operating System OS")
        mail_window.geometry("880x600")
        shell, holder = self._create_rounded_panel(
            mail_window,
            bg=self.colors["window_bg"],
            border=self.colors["taskbar_border"],
            radius=18,
            inner_pad=0,
        )
        shell.pack(fill=tk.BOTH, expand=True)
        header = tk.Frame(holder, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Mail", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text="Inbox preview", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=8)
        body = tk.Frame(holder, bg=self.colors["window_bg"])
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
        messages: list[str] = [
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
        def on_select(event=None) -> None:
            idxs = msg_list.curselection()
            if not idxs:
                return
            msg = msg_list.get(idxs[0]).lstrip("• ").strip()
            self.mail_preview_body.config(text=f"From: team@os.local\nSubject: {msg}\n\nHi there,\nThis is a sample preview for \"{msg}\".")
        msg_list.bind("<<ListboxSelect>>", on_select)

    def open_media_player_window(self) -> None:
        media_window = tk.Toplevel(self.root)
        media_window.title("Media Player - Operating System OS")
        media_window.geometry("760x380")
        shell, holder = self._create_rounded_panel(
            media_window,
            bg=self.colors["window_bg"],
            border=self.colors["taskbar_border"],
            radius=18,
            inner_pad=0,
        )
        shell.pack(fill=tk.BOTH, expand=True)
        header = tk.Frame(holder, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Media Player", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text="Now playing", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=8)
        body = tk.Frame(holder, bg=self.colors["window_bg"])
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
    
    def open_calendar_window(self) -> None:
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Calendar & Weather - Operating System OS")
        cal_window.geometry("520x420")
        shell, holder = self._create_rounded_panel(
            cal_window,
            bg=self.colors["window_bg"],
            border=self.colors["taskbar_border"],
            radius=18,
            inner_pad=0,
        )
        shell.pack(fill=tk.BOTH, expand=True)
        header = tk.Frame(holder, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Calendar & Weather", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        body = tk.Frame(holder, bg=self.colors["window_bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        now: datetime = datetime.now()
        tk.Label(body, text=now.strftime("%A, %B %d"), font=("Segoe UI", 16, "bold"), fg=self.colors["text_primary"], bg=self.colors["window_bg"]).pack(anchor=tk.W)
        tk.Label(body, text=now.strftime("%H:%M"), font=("Segoe UI", 24, "bold"), fg=self.colors["text_primary"], bg=self.colors["window_bg"]).pack(anchor=tk.W, pady=(4, 10))
        tk.Label(body, text="Partly Cloudy · 22°C", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_bg"]).pack(anchor=tk.W)
        forecast_frame = tk.Frame(body, bg=self.colors["window_bg"])
        forecast_frame.pack(fill=tk.X, pady=16)
        sample: list[tuple[str, str, str]] = [
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

    def open_settings_window(self) -> None:
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings - Operating System OS")
        settings_window.geometry("880x600")
        shell, holder = self._create_rounded_panel(
            settings_window,
            bg=self.colors["window_bg"],
            border=self.colors["taskbar_border"],
            radius=18,
            inner_pad=0,
        )
        shell.pack(fill=tk.BOTH, expand=True)
        header = tk.Frame(holder, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Settings", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text="System preferences", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=8)
        body = tk.Frame(holder, bg=self.colors["window_bg"])
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
        cards: list[tuple[str, str]] = [
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

    def open_photos_window(self) -> None:
        photos_window = tk.Toplevel(self.root)
        photos_window.title("Photos - Operating System OS")
        photos_window.geometry("860x560")
        shell, holder = self._create_rounded_panel(
            photos_window,
            bg=self.colors["window_bg"],
            border=self.colors["taskbar_border"],
            radius=18,
            inner_pad=0,
        )
        shell.pack(fill=tk.BOTH, expand=True)
        header = tk.Frame(holder, bg=self.colors["window_header"])
        header.pack(fill=tk.X)
        tk.Label(header, text="Photos", font=self.fonts["ui_bold"], fg=self.colors["text_primary"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=12, pady=8)
        tk.Label(header, text="Library", font=self.fonts["caption"], fg=self.colors["text_muted"], bg=self.colors["window_header"]).pack(side=tk.LEFT, padx=8)
        grid = tk.Frame(holder, bg=self.colors["window_bg"])
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
    
    def get_uptime(self) -> tuple[int, int, int]:
        elapsed: float = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return hours, minutes, seconds
    
    def show_about(self) -> None:
        messagebox.showinfo(
            "About Operating System OS",
            "Operating System OS v1.0\nDesktop preview\n\n"
            "Built with Tkinter to mirror a familiar desktop layout. "
            "Includes a simple shell, file viewer, and system monitor on top of the simulated kernel.\n\n"
            "Specs: 12 GB simulated memory, up to 2048 processes, 4 KB blocks.\n"
            "Created February 13, 2026\n"
            "GitHub: github.com/Jskeen5822/Operating-System-OS",
        )

    def _simulate_system_activity(self) -> None:
        active = [p for p in self.process_table if p.state != ProcessState.TERMINATED]
        if not active:
            return

        non_idle = [p for p in active if p.name != "idle"]
        for p in active:
            drift: float = random.uniform(-1.6, 1.8)
            base: float = 0.8 if p.name == "idle" else 6.0
            p.cpu_usage = max(base, min(98.0, p.cpu_usage + drift))

        if non_idle:
            running_idx: int = int(time.time()) % len(non_idle)
            running_pid = non_idle[running_idx].pid
            for p in non_idle:
                p.state = ProcessState.RUNNING if p.pid == running_pid else ProcessState.READY
            self.process_table[0].state = ProcessState.READY
        else:
            self.process_table[0].state = ProcessState.RUNNING

        base_mem = 420000
        workload_mem: int = sum(p.memory_kb for p in non_idle)
        self.memory_allocated_kb: int = min(self.memory_total_kb, base_mem + workload_mem)

        self.current_process = next((p for p in active if p.state == ProcessState.RUNNING), self.process_table[0])
    
    def start_update_thread(self) -> None:
        """Update top bar and live task-manager windows once per second."""
        def update() -> None:
            self._simulate_system_activity()
            now: str = datetime.now().strftime("%H:%M")
            h, m, s = self.get_uptime()
            active = [p for p in self.process_table if p.state != ProcessState.TERMINATED]
            running: int = len([p for p in active if p.state == ProcessState.RUNNING])

            self.time_label.config(text=now)
            self.status_label.config(text=f"Uptime {h:02d}:{m:02d}:{s:02d} · {running} running")

            for view in list(self.task_manager_views):
                self._refresh_task_manager_view(view)

            self.root.after(1000, update)

        update()

def main() -> None:
    root = tk.Tk()
    app: OSDesktop = OSDesktop(root)
    root.mainloop()

if __name__ == "__main__":
    main()
