# Development Guide - Operating System OS

## Contributing to the OS

This document provides guidelines for contributing to the Operating System OS project.

## Code Organization

### Kernel (kernel/)
- `kernel.c/h` - Main kernel initialization and utilities
- `process.c` - Process management and scheduling
- `memory.c` - Virtual memory and paging
- `filesystem.c` - File system implementation
- `interrupt.asm` - Low-level interrupt handlers

### Shell (shell/)
- `shell.c/h` - Interactive command interface

### Headers (include/)
- `types.h` - Basic type definitions
- `defs.h` - Core data structures

## Coding Standards

### C Code Style
```c
/* Function documentation */
void meaningful_function_name(int param1, const char *param2) {
    /* Clear variable names */
    uint32_t total_size = 0;
    
    /* Descriptive comments */
    for (uint32_t i = 0; i < MAX_ITEMS; i++) {
        total_size += items[i].size;
    }
    
    return total_size;
}
```

### Assembly Code Style
```asm
; Clear section comments
section .text
    
; Function labels in lowercase with underscores
_kernel_init:
    mov eax, ebx        ; Short explanatory comment
    add eax, 1
    ret
```

### Naming Conventions
- **Functions**: `snake_case` - `process_create()`, `memory_allocate()`
- **Variables**: `snake_case` - `page_table`, `inode_number`
- **Constants**: `UPPER_CASE` - `MAX_PROCESSES`, `PAGE_SIZE`
- **Types**: `PascalCase` - `ProcessControlBlock`, `Inode`
- **Structs**: `snake_case` - `struct page_table_entry`

## Adding New Commands to Shell

### Step-by-Step Process

1. **Declare the handler function** in [shell/shell.c](shell/shell.c):
```c
static void cmd_mycommand(uint32_t argc, char *argv[]);
```

2. **Add to command table**:
```c
static ShellCommand commands[] = {
    // ... existing commands ...
    {"mycommand", cmd_mycommand, "Description of mycommand"},
    {NULL, NULL, NULL}
};
```

3. **Implement the function**:
```c
static void cmd_mycommand(uint32_t argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: mycommand <argument>\n");
        return;
    }
    
    printf("Executing mycommand with: %s\n", argv[1]);
    // Your command logic here
}
```

## Adding System Calls

1. **Define syscall number** in [include/defs.h](include/defs.h):
```c
#define SYSCALL_MYFUNCTION 20
```

2. **Create handler** in [kernel/kernel.c](kernel/kernel.c):
```c
uint32_t sys_myfunction(int arg1) {
    // Implementation
    return result;
}
```

3. **Dispatch from interrupt handler** (assembly):
```asm
; In interrupt.asm
syscall_dispatcher:
    cmp eax, SYSCALL_MYFUNCTION
    je sys_myfunction_handler
```

## Extending the File System

### Adding File Types

Edit [include/defs.h](include/defs.h):
```c
#define FILE_TYPE_REGULAR 0
#define FILE_TYPE_DIRECTORY 1
#define FILE_TYPE_SYMLINK 2          /* New */
#define FILE_TYPE_DEVICE 3            /* New */
```

### Adding File Operations

Extend [kernel/filesystem.c](kernel/filesystem.c):
```c
uint32_t filesystem_read_file(uint32_t inode_num, uint32_t offset, 
                              void *buffer, uint32_t size) {
    // Read implementation
}

uint32_t filesystem_write_file(uint32_t inode_num, uint32_t offset, 
                               const void *buffer, uint32_t size) {
    // Write implementation
}
```

## Process Management Extensions

### Custom Scheduling

To implement different scheduling algorithms:

1. **Modify scheduler** in [kernel/kernel.c](kernel/kernel.c#process_schedule):
```c
void process_schedule(void) {
    /* Implement new scheduling algorithm */
    /* Examples: Priority scheduling, Lottery scheduling, etc. */
}
```

2. **Adjust context switch interval**:
```c
#define SCHEDULE_INTERVAL 10  /* Milliseconds */
```

## Memory Management Updates

### Page Size Configuration

To change page size, modify [include/types.h](include/types.h):
```c
#define PAGE_SIZE 4096  /* Change to 8192, 16384, etc. */
```

### Adding Virtual Memory Features

Implement in [kernel/memory.c](kernel/memory.c):
```c
uint32_t memory_allocate_aligned(uint32_t size, uint32_t alignment) {
    /* Alignment-aware allocation */
}

void memory_swap_page(uint32_t page_num) {
    /* Swap implementation */
}
```

## Testing

### Unit Test Example

Create test files in a dedicated directory:

```c
/* test_memory.c */
void test_memory_allocation(void) {
    uint32_t addr = memory_allocate(1024);
    assert(addr != 0);
    memory_free(addr, 1024);
}

void test_process_creation(void) {
    process_create("test", 0);
    assert(process_count == 1);
}
```

## Build and Compilation

### Clean Build
```bash
make clean
make build
```

### Debugging Build
```bash
# Add debug symbols
CFLAGS += -g
make build

# Use GDB with QEMU
qemu-system-i386 -kernel build/bin/os.bin -S -gdb tcp::1234 &
gdb ./build/bin/os.bin
(gdb) target remote localhost:1234
```

## Performance Profiling

### Enable Timing
```c
// In kernel.c
#include <stdint.h>
uint64_t system_ticks = 0;

// On every interrupt
system_ticks++;

// Get elapsed time
uint64_t elapsed = system_ticks * (1000 / TIMER_FREQ);  /* ms */
```

## Documentation

### Adding Function Documentation

Use this format:
```c
/**
 * Brief description of function
 * 
 * Longer description explaining what the function does,
 * how it works, and any important notes.
 * 
 * @param arg1 - Description of arg1
 * @param arg2 - Description of arg2
 * @return Description of return value
 * 
 * @note Any important notes or warnings
 */
uint32_t my_function(uint32_t arg1, const char *arg2);
```

## Debugging Tips

### Print Debugging
```c
printf("Debug: variable value = %d\n", variable);
printf("Debug: pointer = %x\n", (uint32_t)pointer);
```

### Using Assertions
```c
#define ASSERT(condition) \
    if (!(condition)) { \
        printf("ASSERTION FAILED: %s (line %d)\n", \
               #condition, __LINE__); \
        panic("Assertion failed"); \
    }

ASSERT(process_count < MAX_PROCESSES);
```

### QEMU Debugging
```bash
# Start QEMU with debugging support
qemu-system-i386 -kernel os.bin -S -gdb tcp::1234

# In another terminal
gdb
(gdb) target remote localhost:1234
(gdb) symbol-file ./build/kernel.o
(gdb) set architecture i386
(gdb) break main
(gdb) continue
```

## Commit Message Format

```
Title (50 chars or less)

Detailed description of changes. Explain what, why, and how.
Keep lines to 72 characters for readability.

Fixes: #issue_number
Related: #related_issue
```

## Pull Request Process

1. Create feature branch: `git checkout -b feature/description`
2. Make changes following coding standards
3. Test: `make clean && make build`
4. Commit with clear messages
5. Submit PR with description of changes

## Performance Guidelines

### Optimization Priorities
1. **Correctness** - Works first, fast second
2. **Simplicity** - Simple code is fast code
3. **Measurement** - Profile before optimizing
4. **Algorithm** - Better algorithm > micro-optimization

### Do NOT Optimize
- Code that runs rarely
- Code that's not measured
- Code that's not broken
- Code that's not understood

## Future Development Areas

### High Priority
- [ ] Implement disk I/O drivers
- [ ] Complete system call interface
- [ ] Add user/kernel separation
- [ ] Implement fork/exec

### Medium Priority
- [ ] Virtual file system layer
- [ ] Advanced memory management
- [ ] Network stack foundation
- [ ] Loadable modules

### Low Priority
- [ ] GUI framework
- [ ] Audio subsystem
- [ ] High-performance caching
- [ ] Distributed features

---

**Happy coding!** Remember, OS development is a journey. Start small, test often, and enjoy the learning process.
