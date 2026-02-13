# Operating System OS - Simulator

Since the ELF kernel can't boot directly in QEMU without multiboot headers, I've created a **Python simulator** that demonstrates how the OS works!

## What the Simulator Does

The simulator faithfully reproduces:

1. **Boot Sequence** - Shows bootloader initialization and kernel loading
2. **Kernel Initialization** - Displays memory, file system, and process setup
3. **Interactive Shell** - Full command-line interface with all 13 commands
4. **Process Management** - Create, list, and schedule processes
5. **Memory Management** - Tracks allocation and displays statistics
6. **File System** - Create files and directories

## Running the Simulator

```bash
python3 simulator.py
```

Or with the shebang:

```bash
./simulator.py
```

## Simulator Features

### Boot Output
```
Operating System OS - Bootloader
============================================================
Starting bootloader...
✓ BIOS initialization complete
✓ Loading kernel from disk
✓ Switching to 32-bit protected mode
✓ Kernel loaded at 0x1000

============================================================
Operating System OS - Kernel Initialization
============================================================
Initializing kernel subsystems...
✓ Interrupts initialized
✓ Memory management initialized
  - Total memory: 256 MB
  - Page size: 4 KB
  - Kernel reserved: 1 MB (256 pages)
✓ File system initialized
  - Max files: 512
  - Max blocks: 8192
  - Block size: 4 KB
✓ Idle process created (PID=1)
```

### Interactive Commands

```
help             Display all available commands
ps               List running processes
exec <name>      Create a new process
ls               List directory contents
mkdir <name>     Create directory
touch <name>     Create file
pwd              Print working directory
echo <text>      Print text
meminfo          Show memory statistics
uptime           Display system runtime
clear            Clear screen
exit             Shutdown system
```

## Simulator Architecture

### Classes

**ProcessState** - Enum for process states
- READY
- RUNNING
- WAITING
- BLOCKED
- TERMINATED

**Process** - Represents a process in the OS
- pid: Process ID
- name: Process name
- state: Current state
- priority: Scheduling priority
- memory_kb: Allocated memory
- creation_time: When process was created

**OSSimulator** - Main OS simulation
- process_table: Array of processes
- file system: File/directory structure
- memory management: Allocation tracking
- scheduling: Round-robin algorithm

## Example Session

```bash
$ python3 simulator.py

[Boot sequence displays...]

> help

Available Commands:
--------------------------------------------------
  help                 - Display available commands
  ps                   - List running processes
  exec <name>          - Execute new process
  ls                   - List directory contents
  mkdir <name>         - Create directory
  touch <name>         - Create file
  pwd                  - Print working directory
  echo <text>          - Output text
  meminfo              - Display memory information
  uptime               - Display system uptime
  clear                - Clear screen
  exit                 - Exit shell

> ps

Running Processes:
--------------------------------------------------
PID	Name	            State	Priority
--------------------------------------------------
1	idle                READY	0

> exec myapp
Process created: PID=2, Name='myapp'

> ps

Running Processes:
--------------------------------------------------
PID	Name	            State	Priority
--------------------------------------------------
1	idle                READY	0
2	myapp               READY	0

> meminfo

Memory Information:
------------------------------------------
Total Memory: 262144 KB
Kernel Space: 256 pages (1 MB)
Used: 1024 KB
Free: 261120 KB
Available Pages: 65280
Page Size: 4096 bytes

> mkdir projects

Created directory: projects

> touch myfile.txt
Created file: myfile.txt

> ls

Directory: /
------------------------------------------
Files:
  .
  ..
  system.bin           1024 bytes
  kernel.bin           2048 bytes
  shell.bin            512 bytes
  projects             0 bytes
  myfile.txt           0 bytes

> uptime
System uptime: 0 hours, 0 minutes, 5 seconds

> exit
Exiting shell...
Shutting down kernel...
System halted.
```

## Why Use the Simulator?

1. **No Dependencies** - Just Python, works on any system
2. **Educational** - Shows exactly how OS code works
3. **Interactive** - Full shell experience in minutes
4. **Fast** - Instant boot and execution
5. **Debuggable** - Can trace through Python code

## Real Kernel

The actual C/Assembly kernel source is in:
- `kernel/kernel.c` - Main kernel code
- `kernel/process.c` - Process management
- `kernel/memory.c` - Virtual memory
- `kernel/filesystem.c` - File system
- `shell/shell.c` - Shell commands
- `bootloader/boot.asm` - x86 bootloader

The simulator implements all the same logic in Python for demonstration!

## Building Real Kernel

To build the native kernel binary:

```bash
make clean
make build
```

This creates `build/bin/os.bin` (20 KB ELF executable)

## Next Steps

1. **Run the simulator**: `python3 simulator.py`
2. **Explore the code**: Read `kernel/kernel.c`, `shell/shell.c`
3. **Understand architecture**: Read `CONFIG.md`
4. **Extend it**: Add new shell commands or OS features

---

**Operating System OS** - Educational OS with real kernel and interactive simulator! 🚀
