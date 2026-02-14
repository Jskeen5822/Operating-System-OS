# Operating System OS - Architecture & Design

## System Architecture Overview

```
┌─────────────────────────────────────┐
│         User Applications           │
├─────────────────────────────────────┤
│            Shell (CLI)              │
├─────────────────────────────────────┤
│          System Calls Interface      │
├─────────────────────────────────────┤
│          Kernel Subsystems          │
│  ┌──────┬──────────┬────┬─────┐    │
│  │ Proc │ Memory   │FS  │ I/O │    │
│  └──────┴──────────┴────┴─────┘    │
├─────────────────────────────────────┤
│      Interrupt & Trap Handlers      │
├─────────────────────────────────────┤
│      Hardware Abstraction Layer      │
├─────────────────────────────────────┤
│            Bootloader               │
├─────────────────────────────────────┤
│       x86 Protected Mode Hardware    │
└─────────────────────────────────────┘
```

## Kernel Components

### 1. Process Manager (kernel/process.c)
- **Process Control Block (PCB)**: Stores process state
- **Process Table**: Array of 256 PCBs
- **Scheduler**: Round-robin + priority
- **Synchronization**: Basic mutual exclusion

**Key Functions:**
- `process_create()`: Allocate new PCB
- `process_fork()`: Create child process
- `process_wait()`: Wait for process completion
- `process_exit()`: Terminate process
- `process_list()`: Enumerate processes

**Process States:**
```
READY ──→ RUNNING ──→ {WAITING | BLOCKED} ──→ TERMINATED
  ↑       (timer)              (I/O)              ↓
  └─────────────────────── reschedule ───────────┘
```

### 2. Memory Manager (kernel/memory.c)
- **Page-Based Allocation**: 4 KB pages
- **Bitmap Tracking**: Efficient space tracking
- **Virtual Memory Ready**: Page table structures

**Memory Regions:**
- Pages 0-255: Kernel (reserved)
- Pages 256+: User/Process memory
- Total: 65,536 pages × 4 KB = 256 MB

**Key Functions:**
- `memory_allocate()`: Allocate memory pages
- `memory_free()`: Return pages to free pool
- `memory_get_free_pages()`: Query available space
- `memory_print_stats()`: Display memory info

**Algorithm:**
```
For allocation:
  1. Calculate pages_needed = (size + PAGE_SIZE - 1) / PAGE_SIZE
  2. Search bitmap for contiguous free pages
  3. Mark pages as used in bitmap
  4. Return physical address

For deallocation:
  1. Calculate page range
  2. Clear used bits in bitmap
  3. Pages now available for reuse
```

### 3. File System (kernel/filesystem.c)
- **Inode-Based**: Unix-like structure
- **12 Direct Blocks + 1 Indirect**: Up to 4 GB files
- **Journaling Ready**: Structure supports logging

**File System Layout:**
```
┌──────────────────────────────┐
│   Superblock (4 KB)          │ Block 0
├──────────────────────────────┤
│   Inode Bitmap (4 KB)        │ Block 1
├──────────────────────────────┤
│   Block Bitmap (4 KB)        │ Block 2
├──────────────────────────────┤
│   Inode Table (512 × 128B)   │ Blocks 3-8
├──────────────────────────────┤
│   Data Blocks                │ Blocks 9+
│   (User file data)           │
└──────────────────────────────┘
```

**Inode Structure:**
```c
Inode (128 bytes):
  - inode_number: ID (32-bit)
  - file_type: 0=file, 1=directory (32-bit)
  - size: File size in bytes (32-bit)
  - permissions: Mode bits (32-bit)
  - block_pointers[12]: Direct blocks (48 bytes)
  - indirect_block: Single indirect block (4 bytes)
  - hard_link_count: Reference count (32-bit)
  - Created/Modified: Timestamps (16 bytes)
```

**Key Functions:**
- `filesystem_create_file()`: Create regular file
- `filesystem_create_directory()`: Create directory
- `filesystem_allocate_block()`: Get free block
- `filesystem_free_block()`: Return block
- `filesystem_list_directory()`: Read dir entries

### 4. Scheduler (kernel/kernel.c)
- **Algorithm**: Round-Robin with priority
- **Time Slice**: 10 ms (100 Hz timer)
- **Priority Levels**: 0 (low) to 255 (high)

**Scheduling Logic:**
```
Timer Interrupt (every 10 ms):
  1. system_ticks++
  2. If (system_ticks % 10 == 0):
     - Save current process stack pointer
     - Find next ready process
     - Restore new process context
     - Increment process instruction pointer
     - Return from interrupt
```

## Boot Sequence

### Stage 1: BIOS Boot (bootloader/boot.asm)
```
1. BIOS loads boot sector to 0x7C00
2. Initialize stack: sp = 0x9000
3. Display boot message
4. Load kernel sectors from disk
5. Set Global Descriptor Table (GDT)
6. Switch to 32-bit protected mode
   - Turn off interrupts
   - Set CR0 protected mode bit
   - Far jump to protected mode code
7. Initialize segment registers
8. Jump to kernel entry point
```

### Stage 2: Kernel Boot (kernel/kernel.c)
```
kernel_main():
  1. kernel_init()
     - setup_interrupts()
     - setup_memory()
     - setup_filesystem()
     - process_create("idle", 0)
  
  2. Display startup message
  
  3. shell_start()
     - Show shell banner
     - Enter command loop
     - Exit on user request
  
  4. panic("Shell terminated")
```

## Interrupt Handling

### Interrupt Vector
```
IRQ 0  (0x20): Timer interrupt
IRQ 1  (0x21): Keyboard interrupt
...
INT 80h:        System call interface
```

### Timer Interrupt Handler
```asm
timer_interrupt:
  1. Save all registers (PUSHA)
  2. Set EAX = 0 (IRQ 0)
  3. Call C interrupt handler
  4. Send EOI to PIC (port 0x20)
  5. Restore registers (POPA)
  6. Return from interrupt (IRET)
```

## System Calls

### Interface
```c
int sys_fork(void)              /* Create new process */
int sys_exit(int status)        /* Terminate process */
int sys_wait(pid_t pid)         /* Wait for child */
int sys_exec(const char *path)  /* Execute program */
int sys_open(const char *file)  /* Open file */
int sys_close(int fd)           /* Close file */
int sys_read(int fd, void *buf) /* Read from file */
int sys_write(int fd, const void *buf) /* Write to file */
```

### Calling Convention
```asm
; Parameters in: EAX, EBX, ECX, EDX
mov eax, SYSCALL_NUMBER
mov ebx, ARG1
mov ecx, ARG2
mov edx, ARG3
int 80h              ; Invoke system call
; Return value in EAX
```

## Data Structures

### Process Control Block
```c
struct PCB {
    uint32_t pid;                /* Unique process ID */
    uint32_t state;              /* READY/RUNNING/etc */
    uint32_t priority;           /* 0-255 */
    uint32_t page_directory;     /* Virtual memory root */
    uint32_t stack_pointer;      /* Saved SP */
    uint32_t instruction_pointer;/* Saved IP */
    uint32_t total_memory;       /* Allocated bytes */
    uint64_t creation_time;      /* System ticks */
    char name[64];               /* Process name */
}
```

### Page Table Entry (PTE)
```c
struct PTE {
    uint32_t present : 1;        /* Page in memory? */
    uint32_t writable : 1;       /* Writable? */
    uint32_t user : 1;           /* User accessible? */
    uint32_t write_through : 1;  /* Write-through cache? */
    uint32_t cache_disabled : 1; /* Caching disabled? */
    uint32_t accessed : 1;       /* Recently accessed? */
    uint32_t dirty : 1;          /* Modified? */
    uint32_t frame : 20;         /* Physical frame address */
}
```

## Synchronization

### Current Approach
- **No Locks**: Single-threaded per process
- **Interrupt Masking**: Critical sections
- **Atomic Operations**: Via interrupt disable

### Future Improvements
- Mutexes and semaphores
- Reader-writer locks
- Condition variables
- Deadlock detection

## Performance Optimization

### Current Optimizations
1. **Inline Functions**: Hot path functions
2. **Bitmap Storage**: Efficient resource tracking
3. **Direct Access**: No indirection layers
4. **Early Exit**: Fast path optimizations

### Potential Improvements
1. **TLB Management**: Reduce page walk overhead
2. **Page Coloring**: Reduce cache conflicts
3. **Load Balancing**: Better SMP readiness
4. **Memory Compression**: Save RAM

## Security Considerations

### Current State
- **No Privilege Levels**: All code runs in kernel mode
- **No Memory Protection**: Processes not isolated
- **No Authentication**: No user verification

### Future Security
- Ring 3 for user processes
- Page-level access control
- User authentication
- Capability-based security

---

See README.md for build and usage instructions.
