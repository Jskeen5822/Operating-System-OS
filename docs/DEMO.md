Operating System OS - Shell Demo Output
=========================================

Below is what the shell looks like when the OS boots and runs:

```
========================================
  Operating System OS Shell v1.0
  Type 'help' for available commands
========================================

> help

Available Commands:
------------------
  help             - Display available commands
  ps               - List running processes
  exec             - Execute new process
  ls               - List directory contents
  mkdir            - Create directories
  touch            - Create files
  pwd              - Print working directory
  echo             - Output text
  meminfo          - Display memory statistics
  uptime           - System uptime
  clear            - Clear screen
  exit             - Exit shell

> ps

Running Processes:
------------------
PID	Name		State	Priority
---	----		-----	--------
1	idle		RUNNING	0

> meminfo

Memory Information:
-------------------
Total Memory: 262144 KB
Kernel Space: 256 pages
Available: 65280 pages
Page Size: 4096 bytes

> echo Hello from Operating System OS
Hello from Operating System OS

> exec myapp
Process created: PID=2, Name='myapp'

> ps

Running Processes:
------------------
PID	Name		State	Priority
---	----		-----	--------
1	idle		RUNNING	0
2	myapp		READY	0

> uptime
System uptime: 0 hours, 0 minutes, 0 seconds

> ls

Directory: /
Files:
  .
  ..
  system.bin
  kernel.bin
  shell.bin

> mkdir testfolder
Created directory: testfolder

> touch myfile.txt
Created file: myfile.txt

> exit
Exiting shell...
```

## System Specifications

**Build Information:**
- Binary Size: 20 KB
- Format: ELF 32-bit LSB executable
- Architecture: Intel 80386
- Compilation: GCC (32-bit), NASM Assembly

**Runtime Capabilities:**
- ✅ Multi-process support (up to 256 processes)
- ✅ Virtual memory with paging (4KB pages, 256 MB total)
- ✅ Inode-based file system (512 files, 8192 blocks)
- ✅ Interactive shell with 13 built-in commands
- ✅ Process scheduling with round-robin algorithm
- ✅ Memory management with bitmap allocation

**Kernel Components:**
1. Process Manager - Round-robin scheduling
2. Memory Manager - Page-based virtual memory
3. File System - Unix-like inode structure
4. Shell Interface - Command-line interpreter
5. Interrupt Handlers - Hardware event handling

## How It Works

1. **Boot**: The bootloader initializes the CPU in protected mode and jumps to the kernel
2. **Initialization**: Kernel sets up memory, file system, and creates the idle process
3. **Shell Start**: Interactive shell begins accepting user commands
4. **Command Processing**: User input is parsed and executed by the appropriate command handler
5. **Process Management**: Processes are scheduled using round-robin scheduling

## Building and Running

```bash
# Build
make build

# Run in QEMU
qemu-system-i386 -kernel build/bin/os.bin
```

## Repository

🔗 GitHub: https://github.com/Jskeen5822/Operating-System-OS

The complete source code with documentation is available on GitHub!
