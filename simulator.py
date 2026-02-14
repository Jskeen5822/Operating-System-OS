#!/usr/bin/env python3
"""
Operating System OS Simulator
Demonstrates the kernel, process management, memory, and shell
"""

import os
import sys
import time
from datetime import datetime
from enum import Enum

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
        self.memory_kb = 0
        self.creation_time = time.time()
    
    def __repr__(self):
        return f"{self.pid}\t{self.name:<15}\t{self.state.value:<8}\t{self.priority}"

class OSSimulator:
    def __init__(self):
        self.process_table = []
        self.next_pid = 1
        self.current_process = None
        self.system_ticks = 0
        self.memory_total_kb = 262144          
        self.memory_allocated_kb = 256 * 4                  
        self.max_processes = 256
        self.start_time = time.time()
        
                     
        self.files = {
            "/": {"type": "directory", "size": 0},
            "/system.bin": {"type": "file", "size": 1024},
            "/kernel.bin": {"type": "file", "size": 2048},
            "/shell.bin": {"type": "file", "size": 512},
        }
        self.current_directory = "/"
        
                             
        self.create_process("idle", priority=0)
        self.current_process = self.process_table[0]
        self.current_process.state = ProcessState.RUNNING

    def create_process(self, name, priority=0):
        if len(self.process_table) >= self.max_processes:
            print(f"Error: Maximum process limit reached")
            return None
        
        process = Process(self.next_pid, name, priority)
        self.process_table.append(process)
        self.next_pid += 1
        print(f"Process created: PID={process.pid}, Name='{name}'")
        return process
    
    def schedule(self):
        """Round-robin scheduling"""
        if not self.process_table:
            return
        
                                 
        for p in self.process_table:
            if p.state == ProcessState.READY:
                if self.current_process:
                    self.current_process.state = ProcessState.READY
                self.current_process = p
                self.current_process.state = ProcessState.RUNNING
                return
    
    def list_processes(self):
        print("\nRunning Processes:")
        print("-" * 50)
        print("PID\tName\t\t\tState\tPriority")
        print("-" * 50)
        for p in self.process_table:
            if p.state != ProcessState.TERMINATED:
                print(p)
        print()
    
    def show_memory_info(self):
        free_kb = self.memory_total_kb - self.memory_allocated_kb
        print("\nMemory Information:")
        print("-" * 40)
        print(f"Total Memory: {self.memory_total_kb} KB")
        print(f"Kernel Space: 256 pages (1 MB)")
        print(f"Used: {self.memory_allocated_kb} KB")
        print(f"Free: {free_kb} KB")
        print(f"Available Pages: {free_kb // 4}")
        print(f"Page Size: 4096 bytes")
        print()
    
    def list_directory(self, path="/"):
        print(f"\nDirectory: {path}")
        print("-" * 40)
        print("Files:")
        print("  .")
        print("  ..")
        
        for file_path in self.files:
            if file_path != "/":
                name = file_path.split("/")[-1]
                file_info = self.files[file_path]
                size = file_info["size"]
                print(f"  {name:<20} {size} bytes")
        print()
    
    def create_file(self, filename):
        path = self.current_directory.rstrip("/") + "/" + filename
        if path not in self.files:
            self.files[path] = {"type": "file", "size": 0}
            print(f"Created file: {filename}")
        else:
            print(f"File already exists: {filename}")
    
    def create_directory(self, dirname):
        path = self.current_directory.rstrip("/") + "/" + dirname
        if path not in self.files:
            self.files[path] = {"type": "directory", "size": 0}
            print(f"Created directory: {dirname}")
        else:
            print(f"Directory already exists: {dirname}")
    
    def get_uptime(self):
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        return hours, minutes, seconds
    
    def show_uptime(self):
        h, m, s = self.get_uptime()
        print(f"System uptime: {h} hours, {m} minutes, {s} seconds\n")
    
    def show_help(self):
        print("\nAvailable Commands:")
        print("-" * 50)
        commands = [
            ("help", "Display available commands"),
            ("ps", "List running processes"),
            ("exec <name>", "Execute new process"),
            ("ls", "List directory contents"),
            ("mkdir <name>", "Create directory"),
            ("touch <name>", "Create file"),
            ("pwd", "Print working directory"),
            ("echo <text>", "Output text"),
            ("meminfo", "Display memory information"),
            ("uptime", "Display system uptime"),
            ("clear", "Clear screen"),
            ("exit", "Exit shell"),
        ]
        for cmd, desc in commands:
            print(f"  {cmd:<20} - {desc}")
        print()

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def boot_sequence():
    """Display boot sequence"""
    clear_screen()
    print("=" * 60)
    print("Operating System OS - Bootloader")
    print("=" * 60)
    print()
    print("Starting bootloader...")
    time.sleep(0.5)
    print("✓ BIOS initialization complete")
    time.sleep(0.3)
    print("✓ Loading kernel from disk")
    time.sleep(0.3)
    print("✓ Switching to 32-bit protected mode")
    time.sleep(0.3)
    print("✓ Kernel loaded at 0x1000")
    print()
    print("=" * 60)
    print("Operating System OS - Kernel Initialization")
    print("=" * 60)
    print()
    time.sleep(0.3)
    print("Initializing kernel subsystems...")
    time.sleep(0.2)
    print("✓ Interrupts initialized")
    time.sleep(0.2)
    print("✓ Memory management initialized")
    print("  - Total memory: 256 MB")
    print("  - Page size: 4 KB")
    print("  - Kernel reserved: 1 MB (256 pages)")
    time.sleep(0.2)
    print("✓ File system initialized")
    print("  - Max files: 512")
    print("  - Max blocks: 8192")
    print("  - Block size: 4 KB")
    time.sleep(0.2)
    print("✓ Idle process created (PID=1)")
    print()
    time.sleep(0.5)

def main():
    boot_sequence()
    
    simulator = OSSimulator()
    
    print("=" * 60)
    print("Operating System OS Shell v1.0")
    print("Type 'help' for available commands")
    print("=" * 60)
    print()
    
    while True:
        try:
            cmd_input = input("> ").strip()
            
            if not cmd_input:
                continue
            
            parts = cmd_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if cmd == "help":
                simulator.show_help()
            
            elif cmd == "ps":
                simulator.list_processes()
            
            elif cmd == "exec":
                if arg:
                    simulator.create_process(arg, priority=0)
                else:
                    print("Usage: exec <process_name>")
            
            elif cmd == "ls":
                simulator.list_directory(simulator.current_directory)
            
            elif cmd == "pwd":
                print(simulator.current_directory)
                print()
            
            elif cmd == "mkdir":
                if arg:
                    simulator.create_directory(arg)
                    print()
                else:
                    print("Usage: mkdir <directory_name>")
            
            elif cmd == "touch":
                if arg:
                    simulator.create_file(arg)
                    print()
                else:
                    print("Usage: touch <filename>")
            
            elif cmd == "echo":
                if arg:
                    print(arg)
                    print()
                else:
                    print()
            
            elif cmd == "meminfo":
                simulator.show_memory_info()
            
            elif cmd == "uptime":
                simulator.show_uptime()
            
            elif cmd == "clear":
                clear_screen()
            
            elif cmd == "exit":
                print("Exiting shell...")
                print("Shutting down kernel...")
                print("System halted.")
                break
            
            else:
                print(f"Unknown command: {cmd}")
                print("Type 'help' for available commands.")
                print()
        
        except KeyboardInterrupt:
            print("\n\nInterrupt received. Type 'exit' to shutdown.")
            print()
        except EOFError:
            print("\nExiting shell...")
            break

if __name__ == "__main__":
    main()
