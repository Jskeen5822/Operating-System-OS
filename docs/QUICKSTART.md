# Operating System OS - Getting Started

Quick setup and testing guide.

## Prerequisites

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install build-essential nasm gcc-multilib g++-multilib qemu-system-x86
```

### Fedora/RHEL
```bash
sudo dnf groupinstall "Development Tools"
sudo dnf install nasm gcc glibc-devel.686 qemu-system-x86
```

### macOS
```bash
brew install nasm dosfstools qemu
```

### Manual Installation
- **GCC**: https://gcc.gnu.org/
- **NASM**: https://www.nasm.us/
- **QEMU**: https://www.qemu.org/
- **GNU Binutils**: https://www.gnu.org/software/binutils/

## Quick Start

### 1. Build the OS
```bash
cd /home/jskeen/Operating-System-OS
make build
```

Expected output:
```
Compiling: kernel/kernel.c
Compiling: kernel/process.c
Compiling: kernel/memory.c
Compiling: kernel/filesystem.c
Compiling: shell/shell.c
Assembling: bootloader/boot.asm
Assembling: kernel/interrupt.asm
Linking: build/bin/os.bin
Built: build/bin/os.bin
```

### 2. Run in QEMU
```bash
qemu-system-i386 -kernel build/bin/os.bin
```

### 3. Test Shell Commands
```
> help
> ps
> meminfo
> exec test_process
> ls
> exit
```

## Project Layout

```
Operating-System-OS/
├── bootloader/      - x86 bootloader (assembly)
├── kernel/          - Core OS kernel (C + assembly)
├── shell/           - User shell interface (C)
├── include/         - Header files
├── drivers/         - Hardware drivers
├── build/           - Generated files (gitignore'd)
├── Makefile         - Build rules
├── README.md        - Full documentation
├── CONFIG.md        - Architecture & design
├── DEVELOPMENT.md   - Development guidelines
└── QUICKSTART.md    - This file
```

## Key Files to Know

| File | Purpose |
|------|---------|
| [kernel/kernel.c](../kernel/kernel.c) | Main kernel logic |
| [kernel/process.c](../kernel/process.c) | Process management |
| [kernel/memory.c](../kernel/memory.c) | Virtual memory |
| [kernel/filesystem.c](../kernel/filesystem.c) | File system |
| [shell/shell.c](../shell/shell.c) | Command interface |

## Common Tasks

### Add a New Shell Command

1. Edit [shell/shell.c](../shell/shell.c)
2. Add function:
```c
static void cmd_newcommand(uint32_t argc, char *argv[]) {
    printf("Hello from newcommand!\n");
}
```
3. Add to command table
4. Rebuild: `make clean && make build`

### Debug Build Issues

```bash
# See compilation errors
make clean
make build 2>&1 | head -20

# Check if tools are installed
nasm --version
gcc --version
ld --version

# Verify architecture support
gcc -m32 -c -x c /dev/null -o /tmp/test.o
```

### Run with More Debug Info

```bash
# QEMU with debugging
qemu-system-i386 -kernel build/bin/os.bin -serial stdio

# With GDB
qemu-system-i386 -kernel build/bin/os.bin -S -gdb tcp::1234
# In another terminal:
gdb -ex "target remote localhost:1234" build/bin/os.bin
```

## Troubleshooting

### "gcc: command not found"
Install GCC: See Prerequisites section

### "nasm not found"
Install NASM: See Prerequisites section

### "qemu-system-i386: not found"
Install QEMU: See Prerequisites section

### Build fails with "-m32" error
32-bit libraries missing:
```bash
# Ubuntu/Debian
sudo apt-get install gcc-multilib g++-multilib

# Fedora
sudo dnf install glibc-devel.686
```

### Binary is too large
Check if stripping debug symbols helps:
```bash
make clean
# In Makefile, change:
# CFLAGS += -g  (remove this or set to -O2)
make build
```

## Learning Resources

### Understanding the Code
1. **Start here**: [README.md](../README.md) - Overview
2. **Then study**: [CONFIG.md](../CONFIG.md) - Architecture details
3. **Implementation**: [kernel/kernel.c](../kernel/kernel.c) - Main logic
4. **References**: See README.md for external links

### OS Concepts
- **Processes**: [kernel/process.c](../kernel/process.c)
- **Memory**: [kernel/memory.c](../kernel/memory.c)
- **Files**: [kernel/filesystem.c](../kernel/filesystem.c)
- **Shell**: [shell/shell.c](../shell/shell.c)

### Assembly Programming
- x86 instruction set
- Protected mode operation
- Interrupt handling
- See [CONFIG.md](../CONFIG.md#boot-sequence)

## Next Steps

1. **Explore the Code**: Read through [kernel/kernel.c](../kernel/kernel.c)
2. **Add Features**: Implement a new shell command
3. **Extend Design**: Review [DEVELOPMENT.md](../DEVELOPMENT.md)
4. **Contribute**: See pull request process

## Performance Notes

### Current Limitations
- Single CPU (no SMP)
- Basic scheduling (round-robin)
- No swap/paging to disk
- Limited drivers

### Safe to Modify
- Shell commands
- Scheduling algorithm
- Memory allocation strategy
- Process creation logic

## Getting Help

1. **Code Comments**: Look for `//` and `/* */` explanations
2. **Doc Files**: README.md and CONFIG.md
3. **Function Names**: Descriptively named (`process_create()`, etc.)
4. **Variable Names**: Lowercase with underscores (`page_directory`)

## Building Incrementally

```bash
# Build individual components
gcc -m32 -ffreestanding -c kernel/kernel.c -o build/kernel.o
nasm -f elf32 bootloader/boot.asm -o build/boot.o

# Or full build
make build

# Rebuild after single file change
make build/kernel.o  # just this object
```

## Tips & Tricks

### Fast Rebuild
```bash
make build  # Incremental build (only changed files)
```

### Full Rebuild
```bash
make clean && make build  # Complete rebuild
```

### View Generated Assembly
```bash
gcc -m32 -S kernel/kernel.c -o build/kernel.s
cat build/kernel.s | head -50
```

### Check Memory Usage
```bash
size build/bin/os.bin
# Shows: text, data, bss segments
```

---

**You're all set!** Try `make build && qemu-system-i386 -kernel build/bin/os.bin`

Good luck with your OS journey! 🚀
