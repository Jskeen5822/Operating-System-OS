#!/usr/bin/env python3
"""
Operating System OS - Full Graphical Desktop Environment
A complete visual desktop with windows, file manager, system monitor, and terminal
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkFont
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
        self.root.configure(bg="#2c3e50")
        
        # OS State
        self.process_table = []
        self.next_pid = 1
        self.current_process = None
        self.system_ticks = 0
        self.memory_total_kb = 262144
        self.memory_allocated_kb = 256 * 4
        self.max_processes = 256
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
        # Taskbar at bottom
        self.taskbar = tk.Frame(self.root, bg="#1a252f", height=50)
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Taskbar content
        tk.Label(self.taskbar, text="🖥️ Operating System OS", 
                font=("Arial", 11, "bold"), bg="#1a252f", fg="#ecf0f1").pack(side=tk.LEFT, padx=10, pady=5)
        
        # Taskbar buttons
        button_frame = tk.Frame(self.taskbar, bg="#1a252f")
        button_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        tk.Button(button_frame, text="Terminal", bg="#3498db", fg="white", 
                 command=self.open_terminal_window, width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="File Manager", bg="#e74c3c", fg="white",
                 command=self.open_file_manager, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="System Monitor", bg="#f39c12", fg="white",
                 command=self.open_system_monitor, width=14).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="About", bg="#9b59b6", fg="white",
                 command=self.show_about, width=10).pack(side=tk.LEFT, padx=2)
        
        # Right side - clock and status
        time_frame = tk.Frame(self.taskbar, bg="#1a252f")
        time_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.time_label = tk.Label(time_frame, text="", font=("Arial", 10, "bold"), 
                                   bg="#1a252f", fg="#2ecc71")
        self.time_label.pack()
        
        self.status_label = tk.Label(time_frame, text="", font=("Arial", 9),
                                    bg="#1a252f", fg="#95a5a6")
        self.status_label.pack()
        
        # Main desktop area
        self.desktop = tk.Frame(self.root, bg="#2c3e50")
        self.desktop.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Desktop welcome message
        welcome_frame = tk.Frame(self.desktop, bg="#34495e", relief=tk.RAISED, bd=2)
        welcome_frame.pack(fill=tk.BOTH, expand=True)
        
        title_font = tkFont.Font(family="Arial", size=24, weight="bold")
        subtitle_font = tkFont.Font(family="Arial", size=12)
        
        tk.Label(welcome_frame, text="Operating System OS", font=title_font,
                bg="#34495e", fg="#ecf0f1").pack(pady=20)
        
        tk.Label(welcome_frame, text="Complete Desktop Environment v1.0",
                font=subtitle_font, bg="#34495e", fg="#bdc3c7").pack(pady=5)
        
        info_text = """
🎯 Welcome to your custom operating system!

📋 Quick Start:
  • Click "Terminal" to open the shell
  • Click "File Manager" to browse files
  • Click "System Monitor" to view processes

💾 System Info:
  • 256 MB RAM (256 pages × 4KB)
  • Up to 256 processes
  • Interactive file system
  • Round-robin scheduling
        """
        
        tk.Label(welcome_frame, text=info_text, font=("Arial", 10),
                bg="#34495e", fg="#ecf0f1", justify=tk.LEFT).pack(pady=15)
        
        tk.Label(welcome_frame, text="Right-click on desktop for more options (coming soon)",
                font=("Arial", 8), bg="#34495e", fg="#95a5a6").pack(pady=5)
    
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
            "✓ Memory management initialized (256 MB)",
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
        term_window.geometry("800x600")
        term_window.configure(bg="#000000")
        
        # Terminal header
        header = tk.Frame(term_window, bg="#1a1a1a")
        header.pack(fill=tk.X)
        tk.Label(header, text="jskeen@os-desktop:~$", font=("Courier", 10, "bold"),
                bg="#1a1a1a", fg="#00ff00").pack(anchor=tk.W, padx=5, pady=5)
        
        # Terminal output
        output_frame = tk.Frame(term_window)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(output_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        output_text = tk.Text(output_frame, bg="#000000", fg="#00ff00",
                             font=("Courier", 10), yscrollcommand=scrollbar.set,
                             state=tk.DISABLED)
        output_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=output_text.yview)
        
        # Initial output
        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, "Operating System OS - Terminal\n")
        output_text.insert(tk.END, "Type 'help' for commands, 'exit' to close\n\n")
        output_text.config(state=tk.DISABLED)
        
        # Input frame
        input_frame = tk.Frame(term_window, bg="#1a1a1a")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        prompt = tk.Label(input_frame, text="> ", font=("Courier", 10, "bold"),
                         bg="#1a1a1a", fg="#00ff00")
        prompt.pack(side=tk.LEFT)
        
        input_entry = tk.Entry(input_frame, bg="#1a1a1a", fg="#00ff00",
                              font=("Courier", 10), insertbackground="#00ff00")
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def execute_command(event=None):
            cmd = input_entry.get()
            input_entry.delete(0, tk.END)
            
            output_text.config(state=tk.NORMAL)
            output_text.insert(tk.END, f"> {cmd}\n")
            
            if cmd == "help":
                output_text.insert(tk.END, "Available commands: help, ps, exec, meminfo, ls, exit\n")
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
                for name in self.files:
                    if name != "/":
                        info = self.files[name]
                        output_text.insert(tk.END, f"  {info['icon']} {name}\n")
            elif cmd == "exit":
                term_window.destroy()
                return
            elif cmd == "clear":
                output_text.delete("1.0", tk.END)
                return
            elif cmd == "":
                pass
            else:
                output_text.insert(tk.END, f"Unknown command: {cmd}\n")
            
            output_text.see(tk.END)
            output_text.config(state=tk.DISABLED)
        
        input_entry.bind("<Return>", execute_command)
        input_entry.focus()
    
    def open_file_manager(self):
        """Open file manager window"""
        file_window = tk.Toplevel(self.root)
        file_window.title("File Manager - Operating System OS")
        file_window.geometry("800x600")
        file_window.configure(bg="#ecf0f1")
        
        # Toolbar
        toolbar = tk.Frame(file_window, bg="#34495e")
        toolbar.pack(fill=tk.X)
        
        tk.Label(toolbar, text="📁 File Manager", font=("Arial", 12, "bold"),
                bg="#34495e", fg="#ecf0f1").pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(toolbar, text="Current: /", font=("Arial", 10),
                bg="#34495e", fg="#bdc3c7").pack(side=tk.LEFT, padx=10, pady=5)
        
        # File list
        list_frame = tk.Frame(file_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Headers
        header_frame = tk.Frame(list_frame, bg="#95a5a6")
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Name", font=("Arial", 10, "bold"),
                bg="#95a5a6", fg="white", width=40).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Label(header_frame, text="Type", font=("Arial", 10, "bold"),
                bg="#95a5a6", fg="white", width=15).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Label(header_frame, text="Size", font=("Arial", 10, "bold"),
                bg="#95a5a6", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                            font=("Arial", 10), bg="white", selectmode=tk.SINGLE)
        listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        def populate_list():
            listbox.delete(0, tk.END)
            for fname in sorted(self.files.keys()):
                if fname != "/":
                    info = self.files[fname]
                    icon = info['icon']
                    ftype = info['type'].upper()
                    size = info['size']
                    display = f"{icon} {fname:<35} {ftype:<10} {size} bytes"
                    listbox.insert(tk.END, display)
        
        populate_list()
        
        # Button frame
        button_frame = tk.Frame(file_window, bg="#ecf0f1")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def new_file():
            name = simpledialog.askstring("New File", "File name:")
            if name:
                self.files[f"/{name}"] = {"type": "file", "icon": "📄", "size": 0}
                populate_list()
        
        def new_folder():
            name = simpledialog.askstring("New Folder", "Folder name:")
            if name:
                self.files[f"/{name}"] = {"type": "directory", "icon": "📁", "size": 0}
                populate_list()
        
        tk.Button(button_frame, text="New File", command=new_file,
                 bg="#3498db", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="New Folder", command=new_folder,
                 bg="#2ecc71", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", bg="#e74c3c", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Properties", bg="#9b59b6", fg="white", width=12).pack(side=tk.LEFT, padx=5)
    
    def open_system_monitor(self):
        """Open system monitor window"""
        monitor_window = tk.Toplevel(self.root)
        monitor_window.title("System Monitor - Operating System OS")
        monitor_window.geometry("900x700")
        monitor_window.configure(bg="#ecf0f1")
        
        # tabs
        notebook = ttk.Notebook(monitor_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Processes tab
        process_frame = ttk.Frame(notebook)
        notebook.add(process_frame, text="Processes")
        
        # Process tree
        tree_frame = tk.Frame(process_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree = ttk.Treeview(tree_frame, columns=("PID", "Name", "State", "Priority", "Memory", "CPU"),
                           yscrollcommand=scrollbar.set, height=20)
        scrollbar.config(command=tree.yview)
        
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("PID", anchor=tk.W, width=50)
        tree.column("Name", anchor=tk.W, width=150)
        tree.column("State", anchor=tk.W, width=100)
        tree.column("Priority", anchor=tk.CENTER, width=70)
        tree.column("Memory", anchor=tk.CENTER, width=80)
        tree.column("CPU", anchor=tk.CENTER, width=60)
        
        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("PID", text="PID", anchor=tk.W)
        tree.heading("Name", text="Process Name", anchor=tk.W)
        tree.heading("State", text="State", anchor=tk.W)
        tree.heading("Priority", text="Priority", anchor=tk.CENTER)
        tree.heading("Memory", text="Memory (KB)", anchor=tk.CENTER)
        tree.heading("CPU", text="CPU %", anchor=tk.CENTER)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        def update_processes():
            for item in tree.get_children():
                tree.delete(item)
            for p in self.process_table:
                if p.state != ProcessState.TERMINATED:
                    tree.insert("", "end", values=(p.pid, p.name, p.state.value, p.priority, p.memory_kb, p.cpu_usage))
            monitor_window.after(1000, update_processes)
        
        update_processes()
        
        # Memory tab
        memory_frame = ttk.Frame(notebook)
        notebook.add(memory_frame, text="Memory")
        
        mem_label_frame = tk.LabelFrame(memory_frame, text="Memory Usage", font=("Arial", 10, "bold"))
        mem_label_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Memory bar
        percent_used = (self.memory_allocated_kb / self.memory_total_kb) * 100
        
        canvas = tk.Canvas(mem_label_frame, height=40, bg="white")
        canvas.pack(fill=tk.X, padx=10, pady=10)
        
        bar_width = 600
        used_width = (percent_used / 100) * bar_width
        
        canvas.create_rectangle(5, 5, 5 + bar_width, 35, outline="black", fill="#ecf0f1")
        canvas.create_rectangle(5, 5, 5 + used_width, 35, fill="#3498db")
        canvas.create_text(bar_width / 2 + 5, 20, text=f"{percent_used:.1f}% Used", font=("Arial", 10, "bold"))
        
        info_text = f"""
Total Memory: {self.memory_total_kb} KB (256 MB)
Allocated: {self.memory_allocated_kb} KB
Free: {self.memory_total_kb - self.memory_allocated_kb} KB

Page Size: 4 KB
Total Pages: {self.memory_total_kb // 4}
Kernel Pages: 256
Available Pages: {(self.memory_total_kb - self.memory_allocated_kb) // 4}
        """
        
        tk.Label(mem_label_frame, text=info_text, font=("Courier", 10),
                justify=tk.LEFT, bg="white").pack(anchor=tk.W, padx=10, pady=10)
        
        # System tab
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="System")
        
        self.sys_info_label = tk.Label(system_frame, text="", font=("Courier", 10),
                                       justify=tk.LEFT, bg="white")
        self.sys_info_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def update_system_info():
            h, m, s = self.get_uptime()
            info = f"""
Operating System OS - System Information
{'='*50}

Kernel: Operating System OS v1.0
Architecture: Intel 80386 (32-bit)
Build Date: February 13, 2026

System Uptime: {h}h {m}m {s}s
Boot Time: {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}

Processor:
  • Cores: 1
  • Threads: 1
  • Architecture: x86

Memory:
  • Total: 256 MB
  • Used: {self.memory_allocated_kb} KB
  • Free: {self.memory_total_kb - self.memory_allocated_kb} KB

Processes:
  • Running: {len([p for p in self.process_table if p.state == ProcessState.RUNNING])}
  • Ready: {len([p for p in self.process_table if p.state == ProcessState.READY])}
  • Total: {len(self.process_table)}
  • Max: {self.max_processes}

File System:
  • Total Files: {len(self.files)}
  • Block Size: 4 KB
  • Total Blocks: 8192
  • Max Files: 512
            """
            self.sys_info_label.config(text=info)
            monitor_window.after(2000, update_system_info)
        
        update_system_info()
    
    def get_uptime(self):
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return hours, minutes, seconds
    
    def show_about(self):
        messagebox.showinfo("About Operating System OS", """
Operating System OS v1.0
Complete Desktop Environment

A full-featured operating system with:
✓ 32-bit x86 kernel
✓ Process management (256 processes)
✓ Virtual memory (256 MB)
✓ File system (512 files)
✓ Interactive shell
✓ Graphical desktop

Created February 13, 2026
GitHub: github.com/Jskeen5822/Operating-System-OS

Features:
• Multi-process support
• Memory management with paging
• Unix-like file system
• Interactive shell commands
• System monitoring
• Process scheduling
• Round-robin algorithm

This is an educational OS demonstrating:
- Kernel architecture
- Process management
- Memory management
- File system design
- System scheduling
        """)
    
    def start_update_thread(self):
        """Update clock and status in taskbar"""
        def update():
            while True:
                try:
                    now = datetime.now().strftime("%H:%M:%S")
                    h, m, s = self.get_uptime()
                    status = f"Uptime: {h}h {m}m {s}s"
                    
                    self.time_label.config(text=now)
                    self.status_label.config(text=status)
                    time.sleep(1)
                except:
                    break
        
        thread = threading.Thread(target=update, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = OSDesktop(root)
    root.mainloop()

if __name__ == "__main__":
    main()
