------------------------------completely vibe coded------------------------------------------------------------
# Operating System OS
A full-featured 32-bit x86 operating system written in C and Assembly, featuring process management, virtual memory, a file system, and an interactive shell.

## 🎯 Features

### Core Kernel
- **32-bit x86 Protected Mode** bootloader and kernel
- **Interrupt handling** with timer and keyboard support
- **Modular architecture** with clean separation of concerns

### Process Management
- Process creation and destruction
- Round-robin process scheduling
- Process state machine (Ready, Running, Waiting, Blocked, Terminated)
- Process priority support
- Up to 256 concurrent processes

### Memory Management
- **Virtual memory** with paging
- Page-based memory allocation and deallocation
- 4KB page size
- Up to 256 MB addressable memory
- Kernel space isolation (3GB to 4GB range)

### File System
- **Inode-based file system** with direct and indirect blocks
- Directory support
- File creation and deletion
- File permissions and metadata
- Up to 512 files and 8192 blocks

### Shell/Command Interface
- Interactive command-line shell
- Built-in commands:
  - `help` - Display available commands
  - `ps` - List running processes
  - `exec` - Execute new process
  - `ls` - List directory contents
  - `mkdir` - Create directories
  - `touch` - Create files
  - `pwd` - Print working directory
  - `echo` - Output text
  - `meminfo` - Display memory statistics
  - `uptime` - System uptime
  - `clear` - Clear screen
  - `exit` - Exit shell

## 📁 Project Structure

```
Operating-System-OS/
├── bootloader/          # x86 bootloader code
│   └── boot.asm        # Boot sector and protected mode init
├── kernel/             # Kernel core modules
│   ├── kernel.c        # Main kernel (init, scheduling, utilities)
│   ├── kernel.h        # Kernel headers
│   ├── process.c       # Process management
│   ├── memory.c        # Memory management
│   ├── filesystem.c    # File system implementation
│   └── interrupt.asm   # Interrupt handlers
├── shell/              # User-facing shell
│   ├── shell.c         # Shell implementation and commands
│   └── shell.h         # Shell headers
├── include/            # Global headers
│   ├── types.h         # Type definitions
│   └── defs.h          # Data structure definitions
├── drivers/            # Hardware drivers (extensible)
├── Makefile            # Build system
└── README.md          # This file
```

## 🛠️ Building

### Prerequisites
- GCC (cross-compiler for i386 or native 32-bit gcc)
- NASM (Netwide Assembler)
- GNU Make
- LD (GNU Linker)

### Build Commands

```bash
# Build the OS
make build

# Clean build artifacts
make clean

# Show build instructions
make run
```

## 🚀 Running the OS

### Using QEMU (Recommended)
```bash
qemu-system-i386 -kernel build/bin/os.bin
```

### Using Other Emulators
- **VirtualBox**: Create a new VM and load the `.bin` file
- **Bochs**: Configure bochs with the kernel image
- **Physical Hardware**: Create bootable USB/CD and boot directly

## 📋 Command Examples

```bash
# View help
> help

# List processes
> ps

# Create a new process
> exec myprocess

# Check memory usage
> meminfo

# System uptime
> uptime

# Create files
> touch myfile.txt

# Create directories
> mkdir myfolder

# List directory
> ls

# Exit shell
> exit
```

## 🏗️ Architecture Overview

### Boot Process
1. **Boot Sector** (512 bytes)
   - Initializes basic hardware
   - Loads kernel from disk
   - Switches to 32-bit protected mode
   - Jumps to kernel entry point

2. **Kernel Initialization**
   - Sets up interrupt handlers
   - Initializes memory management
   - Initializes file system
   - Creates idle process
   - Starts shell

### Process Model
- **PCB (Process Control Block)**: Stores per-process state
- **Scheduling**: Round-robin with priority support
- **States**: Ready → Running → Waiting/Blocked → Terminated
- **Context Switching**: Via timer interrupt handler

### Memory Layout
```
0xFFFFFFFF ┌─────────────────────┐
           │  Kernel Space       │ (1 GB: 3-4GB)
0xC0000000 ├─────────────────────┤
           │  User Space         │
           │  (Dynamic Allocation)
           ├─────────────────────┤
           │  Heap               │
           ├─────────────────────┤
           │  Stack              │
           ├─────────────────────┤
           │  BSS                │
           ├─────────────────────┤
           │  Data               │
           ├─────────────────────┤
           │  Code               │
0x00001000 ├─────────────────────┤
0x00000000 │  Reserved/BIOS Data │
```

### File System Structure
- **Superblock**: Metadata (block count, inode count, block size)
- **Inode Table**: 512 inodes (one per file/directory)
- **Block Bitmap**: Tracks allocated blocks
- **Inode Bitmap**: Tracks allocated inodes
- **Data Blocks**: 8192 blocks of 4KB each

## 🔧 System Calls (Future Implementation)

Planned system calls:
- `fork()` - Create new process
- `exit()` - Terminate process
- `wait()` - Wait for child process
- `open()` - Open file
- `close()` - Close file
- `read()` - Read from file
- `write()` - Write to file
- `mkdir()` - Create directory
- `exec()` - Execute program

## 📈 Performance Characteristics

- **Page Size**: 4 KB (standard x86)
- **Max Memory**: 256 MB (with current page table)
- **Max Processes**: 256
- **Context Switch Interval**: 10 ms (100 Hz)
- **Block Size**: 4 KB (standard)
- **Max File Count**: 512

## 🐛 Known Limitations

1. **Single CPU**: No SMP support
2. **No Virtual File System**: Hardcoded filesystem
3. **Basic Paging**: No swap/TLB management
4. **Limited Drivers**: Keyboard and video only
5. **No Networking**: Not network-capable
6. **Monolithic Design**: All modules in kernel space
7. **No Security**: No privilege levels between processes

## 🚧 Future Enhancements

- [ ] Loadable kernel modules
- [ ] Virtual file system layer
- [ ] Network stack (TCP/IP)
- [ ] Graphics subsystem (VESA)
- [ ] Sound subsystem
- [ ] User/kernel separation
- [ ] Multi-CPU support
- [ ] Advanced scheduling algorithms
- [ ] Dynamic module loading
- [ ] POSIX compatibility layer

## 📚 References

- [x86 Assembly Language](https://en.wikibooks.org/wiki/X86_Assembly)
- [Intel Manual - Protected Mode](https://www.intel.com/content/dam/develop/external/us/en/documents/manual/64-ia-32-architectures-software-developer-vol-1-manual.pdf)
- [OS Development - OSDev.org](https://wiki.osdev.org/)
- [GNU Linker Documentation](https://sourceware.org/binutils/docs/ld/)

## 📄 License

Educational and open source. Modify freely for learning purposes.

## 👤 Author

Created as a comprehensive demonstration of operating system design principles.

---

**Operating System OS** - Where simple ideas lead to complex systems.