#!/usr/bin/env python3
"""
Operating System OS - Modern Desktop Environment
Combines Qubes OS compartmentalization with Ubuntu design
64-bit x86-64 kernel simulation with domain isolation

Features:
- Color-coded domains (system, user, network, storage, USB)
- Qubes-style window decoration and VM isolation
- Ubuntu-like modern polish and design
- Real-time system monitoring
- Multi-domain process management
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional

                                                                              
                                           
                                                                              

class DomainType(Enum):
    SYSTEM = "#FF0000"                          
    USER = "#00AA00"                                    
    NETWORK = "#0066FF"                         
    STORAGE = "#FFAA00"                           
    WORK = "#8040FF"                              

@dataclass
class Domain:
    """Represents an isolated execution domain"""
    name: str
    color: str
    domain_type: DomainType
    is_isolated: bool = True
    has_network: bool = False
    has_usb: bool = False
    processes: List = None
    memory_limit_mb: int = 2048
    
    def __post_init__(self):
        if self.processes is None:
            self.processes = []

                                                                              
                                              
                                                                              

@dataclass
class Process:
    """Process running in a domain"""
    pid: int
    name: str
    domain: 'Domain'
    state: str
    memory_mb: float
    cpu_percent: float
    creation_time: float

class OSKernel:
    """Modern 64-bit OS Kernel Simulator"""
    
    def __init__(self):
        self.running = True
        self.boot_time = time.time()
        self.ticks = 0
        self.cpu_count = 3
        self.total_memory_gb = 8
        self.processes: List[Process] = []
        self.next_pid = 1
        
                            
        self.domains: Dict[str, Domain] = {
            'sys': Domain('sys', '#FF0000', DomainType.SYSTEM, True, False, False),
            'personal': Domain('personal', '#00AA00', DomainType.USER, True, False, False),
            'work': Domain('work', '#8040FF', DomainType.WORK, True, False, False),
            'net': Domain('net', '#0066FF', DomainType.NETWORK, True, True, False),
            'usb': Domain('usb', '#FFAA00', DomainType.STORAGE, True, False, True),
        }
        
                                         
        self._create_initial_processes()
        self._start_scheduler()
    
    def _create_initial_processes(self):
        """Create initial system processes"""
        self.create_process('systemd', 'sys', 128)
        self.create_process('kernel', 'sys', 256)
        self.create_process('desktop', 'personal', 512)
    
    def create_process(self, name: str, domain_name: str, memory_mb: float = 64):
        """Create a new process in a domain"""
        domain = self.domains.get(domain_name, self.domains['sys'])
        
        process = Process(
            pid=self.next_pid,
            name=name,
            domain=domain,
            state='RUNNING',
            memory_mb=memory_mb,
            cpu_percent=0.0,
            creation_time=time.time()
        )
        self.processes.append(domain.processes)
        self.processes.append(process)
        self.next_pid += 1
        return process.pid
    
    def get_uptime_seconds(self):
        """Get system uptime in seconds"""
        return time.time() - self.boot_time
    
    def get_uptime_formatted(self):
        """Get formatted uptime string"""
        seconds = int(self.get_uptime_seconds())
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m"
    
    def get_memory_usage(self):
        """Get total memory usage"""
        return sum(p.memory_mb for p in self.processes)
    
    def get_memory_percent(self):
        """Get memory usage as percentage"""
        total_mb = self.total_memory_gb * 1024
        used = self.get_memory_usage()
        return (used / total_mb) * 100
    
    def _start_scheduler(self):
        """Start background scheduler"""
        def scheduler():
            while self.running:
                self.ticks += 1
                                         
                for process in self.processes:
                    if process.state == 'RUNNING':
                        process.cpu_percent = (self.ticks % 100) * 0.01
                time.sleep(0.1)
        
        thread = threading.Thread(target=scheduler, daemon=True)
        thread.start()
    
    def shutdown(self):
        """Shutdown the OS"""
        self.running = False

                                                                              
                                    
                                                                              

class ModernDesktop:
    """Modern Qubes OS + Ubuntu styled desktop"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Operating System OS - Modern Desktop")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1E1E1E")
        
        self.os_kernel = OSKernel()
        self.active_domain = None
        self.windows_open = {}
        
                  
        self._setup_styles()
        self._create_ui()
        self._start_update_thread()
    
    def _setup_styles(self):
        """Setup modern Tkinter styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
                       
        bg_dark = "#1E1E1E"
        bg_panel = "#252525"
        fg_text = "#E0E0E0"
        accent = "#0078D4"
        
        style.configure('TButton', font=('Ubuntu', 10))
        style.configure('TLabel', background=bg_dark, foreground=fg_text)
        style.configure('Title.TLabel', font=('Ubuntu', 24, 'bold'), 
                       background=bg_dark, foreground=fg_text)
        style.configure('Subtitle.TLabel', font=('Ubuntu', 14), 
                       background=bg_panel, foreground=fg_text)
    
    def _create_ui(self):
        """Create main UI layout"""
                                  
        self._create_top_bar()
        
                                        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
                              
        self._create_sidebar(main_frame)
        
                           
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        self._create_content_area(content_frame)
        
                        
        self._create_taskbar()
    
    def _create_top_bar(self):
        """Create top system bar"""
        top_bar = tk.Frame(self.root, bg="#0D0D0D", height=50)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)
        
               
        title = tk.Label(top_bar, text="🖥️  Operating System OS - Modern Desktop",
                        fg="#E0E0E0", bg="#0D0D0D", font=("Ubuntu", 14, "bold"))
        title.pack(side=tk.LEFT, padx=15, pady=10)
        
                     
        self.time_label = tk.Label(top_bar, text="", fg="#00AA00", 
                                  bg="#0D0D0D", font=("Ubuntu", 9, "mono"))
        self.time_label.pack(side=tk.RIGHT, padx=15, pady=10)
    
    def _create_sidebar(self, parent):
        """Create domain sidebar"""
        sidebar = tk.Frame(parent, bg="#252525", width=220)
        sidebar.pack(fill=tk.Y, side=tk.LEFT, padx=5, pady=5)
        sidebar.pack_propagate(False)
        
               
        title = tk.Label(sidebar, text="DOMAINS", fg="#E0E0E0", bg="#252525",
                        font=("Ubuntu", 11, "bold"))
        title.pack(pady=10)
        
                        
        for domain_name, domain in self.os_kernel.domains.items():
            self._create_domain_button(sidebar, domain_name, domain)
        
                   
        sep = tk.Frame(sidebar, bg="#404040", height=1)
        sep.pack(fill=tk.X, pady=10)
        
                             
        info_title = tk.Label(sidebar, text="SYSTEM", fg="#E0E0E0", 
                             bg="#252525", font=("Ubuntu", 10, "bold"))
        info_title.pack(pady=5)
        
        self.info_frame = tk.Frame(sidebar, bg="#252525")
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=5)
    
    def _create_domain_button(self, parent, name, domain):
        """Create a domain button with color indicator"""
        btn_frame = tk.Frame(parent, bg="#252525", highlightthickness=0)
        btn_frame.pack(fill=tk.X, padx=5, pady=3)
        
                         
        color_box = tk.Frame(btn_frame, width=6, bg=domain.color)
        color_box.pack(side=tk.LEFT, fill=tk.Y)
        
                     
        btn = tk.Button(btn_frame, text=f"{name.upper()}", 
                       bg="#333333", fg="#E0E0E0", 
                       font=("Ubuntu", 9, "bold"),
                       border=0, padx=10, pady=6,
                       command=lambda: self._switch_domain(name))
        btn.pack(fill=tk.BOTH, expand=True)
    
    def _switch_domain(self, domain_name):
        """Switch to a different domain"""
        self.active_domain = domain_name
        messagebox.showinfo("Domain Switch", 
                          f"Switched to domain: {domain_name}")
    
    def _create_content_area(self, parent):
        """Create main content display area"""
                       
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
                      
        overview_frame = tk.Frame(notebook, bg="#1E1E1E")
        notebook.add(overview_frame, text="Overview")
        self._create_overview_tab(overview_frame)
        
                       
        processes_frame = tk.Frame(notebook, bg="#1E1E1E")
        notebook.add(processes_frame, text="Processes")
        self._create_processes_tab(processes_frame)
        
                     
        domains_frame = tk.Frame(notebook, bg="#1E1E1E")
        notebook.add(domains_frame, text="Domains")
        self._create_domains_tab(domains_frame)
        
                      
        terminal_frame = tk.Frame(notebook, bg="#1E1E1E")
        notebook.add(terminal_frame, text="Terminal")
        self._create_terminal_tab(terminal_frame)
    
    def _create_overview_tab(self, parent):
        """Create overview display"""
        Label = tk.Label
        
                     
        info_title = Label(parent, text="System Information", 
                          fg="#E0E0E0", bg="#1E1E1E", 
                          font=("Ubuntu", 12, "bold"))
        info_title.pack(anchor=tk.W, padx=10, pady=10)
        
        info_text = f"""
Architecture:       x86-64 (64-bit)
Bootloader:         UEFI
CPU Cores:          3 (max)
Total Memory:       8 GB
Kernel:             Operating System OS 64-bit
Boot Time:          {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.os_kernel.boot_time))}
        """
        
        info = Label(parent, text=info_text, fg="#00AA00", bg="#252525",
                    font=("Ubuntu Mono", 9), justify=tk.LEFT)
        info.pack(fill=tk.BOTH, padx=10, pady=5)
        
                            
        perf_title = Label(parent, text="Performance", 
                          fg="#E0E0E0", bg="#1E1E1E",
                          font=("Ubuntu", 12, "bold"))
        perf_title.pack(anchor=tk.W, padx=10, pady=(20, 10))
        
                    
        mem_frame = tk.Frame(parent, bg="#252525", height=30)
        mem_frame.pack(fill=tk.X, padx=10, pady=5)
        mem_frame.pack_propagate(False)
        
        mem_percent = self.os_kernel.get_memory_percent()
        mem_label = Label(mem_frame, text=f"Memory: {mem_percent:.1f}%",
                         fg="#00AA00", bg="#252525", font=("Ubuntu", 9))
        mem_label.pack(side=tk.LEFT, padx=5, pady=5)
        
                        
        canvas = tk.Canvas(mem_frame, bg="#333333", height=20, highlightthickness=0)
        canvas.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        bar_width = canvas.winfo_width() * (mem_percent / 100)
        canvas.create_rectangle(0, 0, bar_width, 20, fill="#00AA00", outline="")
    
    def _create_processes_tab(self, parent):
        """Create processes list"""
                         
        columns = ("PID", "Name", "Domain", "State", "Memory (MB)", "CPU %")
        tree = ttk.Treeview(parent, columns=columns, height=20)
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("PID", anchor=tk.W, width=50)
        tree.column("Name", anchor=tk.W, width=150)
        tree.column("Domain", anchor=tk.W, width=100)
        tree.column("State", anchor=tk.CENTER, width=80)
        tree.column("Memory (MB)", anchor=tk.E, width=100)
        tree.column("CPU %", anchor=tk.E, width=80)
        
                  
        tree.heading("#0", text="", anchor=tk.W)
        for col in columns:
            tree.heading(col, text=col, anchor=tk.W)
        
                       
        for process in self.os_kernel.processes:
            tree.insert("", "end", values=(
                process.pid,
                process.name,
                process.domain.name,
                process.state,
                f"{process.memory_mb:.1f}",
                f"{process.cpu_percent:.1f}"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
                   
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscroll=scrollbar.set)
    
    def _create_domains_tab(self, parent):
        """Create domains overview"""
        title = tk.Label(parent, text="Isolated Domains", 
                        fg="#E0E0E0", bg="#1E1E1E",
                        font=("Ubuntu", 12, "bold"))
        title.pack(anchor=tk.W, padx=10, pady=10)
        
        for name, domain in self.os_kernel.domains.items():
            self._create_domain_card(parent, name, domain)
    
    def _create_domain_card(self, parent, name, domain):
        """Create a domain card"""
        card = tk.Frame(parent, bg="#252525")
        card.pack(fill=tk.X, padx=10, pady=5)
        
                           
        header = tk.Frame(card, bg=domain.color, height=4)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
                 
        content = tk.Label(card, bg="#252525", fg="#E0E0E0", 
                          font=("Ubuntu", 9), justify=tk.LEFT)
        content_text = f"{name.upper()}\nIsolated: {domain.is_isolated}\nNetwork: {domain.has_network}\nUSB: {domain.has_usb}"
        content.config(text=content_text)
        content.pack(fill=tk.BOTH, padx=10, pady=8)
    
    def _create_terminal_tab(self, parent):
        """Create terminal emulator"""
        terminal = tk.Text(parent, bg="#000000", fg="#00AA00",
                          font=("Ubuntu Mono", 10), insertbackground="#00AA00")
        terminal.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        terminal.insert("1.0", "$ Operating System OS Terminal v64\n$ Type 'help' for commands\n\n$ ")
        terminal.bind("<Return>", lambda e: self._handle_terminal_command(e, terminal))
    
    def _handle_terminal_command(self, event, terminal):
        """Handle terminal command"""
                          
        current_line = terminal.get("end-2c linestart", "end")
        command = current_line.replace("$ ", "").strip()
        
        if command == "help":
            output = """Commands: help, ps, exec NAME, clear, shutdown
"""
        elif command == "ps":
            output = "All running processes listed in Processes tab\n"
        elif command.startswith("exec"):
            parts = command.split()
            if len(parts) > 1:
                name = parts[1]
                self.os_kernel.create_process(name, 'personal')
                output = f"Process '{name}' created\n"
            else:
                output = "Usage: exec NAME\n"
        elif command == "clear":
            terminal.delete("1.0", tk.END)
            output = ""
        elif command == "shutdown":
            self.root.quit()
            output = ""
        else:
            output = f"Unknown command: {command}\n"
        
        terminal.insert(tk.END, output + "$ ")
        terminal.see(tk.END)
        return "break"
    
    def _create_taskbar(self):
        """Create bottom taskbar"""
        taskbar = tk.Frame(self.root, bg="#0D0D0D", height=40)
        taskbar.pack(fill=tk.X)
        taskbar.pack_propagate(False)
        
                           
        left_frame = tk.Frame(taskbar, bg="#0D0D0D")
        left_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        apps = ["File Manager", "Settings", "Help"]
        for app in apps:
            btn = tk.Button(left_frame, text=app, bg="#333333", fg="#E0E0E0",
                           font=("Ubuntu", 9), border=0, padx=10, pady=3)
            btn.pack(side=tk.LEFT, padx=2)
        
                       
        right_frame = tk.Frame(taskbar, bg="#0D0D0D")
        right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.status_label = tk.Label(right_frame, text="Ready", 
                                    fg="#00AA00", bg="#0D0D0D",
                                    font=("Ubuntu Mono", 8))
        self.status_label.pack()
    
    def _start_update_thread(self):
        """Start background update thread"""
        def update_loop():
            while True:
                self._update_displays()
                time.sleep(1)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    def _update_displays(self):
        """Update all displays"""
        try:
                         
            uptime = self.os_kernel.get_uptime_formatted()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=f"Uptime: {uptime} | {timestamp}")
            
                           
            mem_percent = self.os_kernel.get_memory_percent()
            processes = len(self.os_kernel.processes)
            self.status_label.config(text=f"Processes: {processes} | Memory: {mem_percent:.1f}%")
        except:
            pass

                                                                              
                         
                                                                              

def main():
    root = tk.Tk()
    desktop = ModernDesktop(root)
    root.mainloop()

if __name__ == "__main__":
    main()
