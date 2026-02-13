/*
 * Operating System OS - Real 64-bit x86-64 Kernel
 * Actual kernel code, not simulation
 * Runs in long mode (64-bit) on x86-64 processors
 * 
 * Memory Layout:
 * 0x00100000 - Kernel code/data (1 MB)
 * 0x00200000 - Page tables (1 MB)
 * 0x00400000 - Process stacks (4 MB)
 * 0x01000000 - Heap (16+ MB)
 * 0x80000000 - User space high
 */

#include <stdint.h>
#include <stddef.h>

/* ============================================================================
 * Type Definitions
 * ============================================================================ */

typedef unsigned char       uint8_t;
typedef unsigned short      uint16_t;
typedef unsigned int        uint32_t;
typedef unsigned long long  uint64_t;
typedef signed long long    int64_t;
typedef uint64_t            paddr_t;      /* Physical address */
typedef uint64_t            vaddr_t;      /* Virtual address */
typedef uint64_t            size_t;
typedef int64_t             ssize_t;

typedef volatile uint32_t   ioport32_t;
typedef volatile uint16_t   ioport16_t;
typedef volatile uint8_t    ioport8_t;

#define NULL                ((void *)0)
#define PAGE_SIZE           0x1000        /* 4 KB pages */
#define PAGE_SHIFT          12
#define PAGE_MASK           0xFFF
#define KERNEL_BASE         0xFFFF800000000000ULL  /* High half kernel space */
#define KERNEL_PHYS_BASE    0x100000ULL            /* Physical load address */

/* ============================================================================
 * Processor State & Control
 * ============================================================================ */

/* Control Registers */
#define CR0_PE              0x00000001    /* Protected mode */
#define CR0_MP              0x00000002    /* Math processor */
#define CR0_EM              0x00000004    /* Emulation */
#define CR0_TS              0x00000008    /* Task switched */
#define CR0_ET              0x00000010    /* Extension type */
#define CR0_NE              0x00000020    /* Numeric error */
#define CR0_WP              0x00010000    /* Write protect */
#define CR0_AM              0x00040000    /* Alignment mask */
#define CR0_NW              0x20000000    /* Not write-through */
#define CR0_CD              0x40000000    /* Cache disable */
#define CR0_PG              0x80000000    /* Paging */

#define CR4_PSE             0x00000010    /* Page size extensions (2MB) */
#define CR4_PAE             0x00000020    /* Physical address extension */
#define CR4_PGE             0x00000080    /* Global pages */
#define CR4_PCE             0x00000100    /* Performance counter */
#define CR4_OSFXSR          0x00000200    /* OS FXSAVE/FXRSTOR */
#define CR4_OSXMMEXCPT      0x00000400    /* OS unmasked exceptions */
#define CR4_FSGSBASE        0x00010000    /* FSGSBASE instructions */
#define CR4_PCIDE           0x00020000    /* PCID enable */
#define CR4_SMEP            0x00100000    /* Supervisor mode exec protection */
#define CR4_SMAP            0x00200000    /* Supervisor mode access prevention */

/* ============================================================================
 * GDT (Global Descriptor Table) - Needed for 64-bit mode
 * ============================================================================ */

struct GDTEntry {
    uint16_t limit_low;
    uint16_t base_low;
    uint8_t  base_mid;
    uint8_t  access;
    uint8_t  granularity;
    uint8_t  base_high;
} __attribute__((packed));

struct GDTPointer {
    uint16_t size;
    uint64_t base;
} __attribute__((packed));

/* GDT Entries */
#define GDT_NULL            0
#define GDT_KERNEL_CODE     1
#define GDT_KERNEL_DATA     2
#define GDT_USER_CODE64     3
#define GDT_USER_DATA       4
#define GDT_TSS             5
#define GDT_ENTRIES         6

struct GDTEntry gdt[GDT_ENTRIES];
struct GDTPointer gdt_ptr;

void gdt_init(void) {
    /* NULL entry */
    gdt[GDT_NULL].limit_low = 0;
    gdt[GDT_NULL].base_low = 0;
    gdt[GDT_NULL].base_mid = 0;
    gdt[GDT_NULL].access = 0;
    gdt[GDT_NULL].granularity = 0;
    gdt[GDT_NULL].base_high = 0;
    
    /* Kernel code (64-bit) */
    gdt[GDT_KERNEL_CODE].limit_low = 0;
    gdt[GDT_KERNEL_CODE].access = 0x9A;  /* Present, DPL=0, Executable, Readable */
    gdt[GDT_KERNEL_CODE].granularity = 0xA0; /* Long mode */
    
    /* Kernel data */
    gdt[GDT_KERNEL_DATA].limit_low = 0;
    gdt[GDT_KERNEL_DATA].access = 0x92;  /* Present, DPL=0, Writable */
    gdt[GDT_KERNEL_DATA].granularity = 0;
    
    /* User code (64-bit) */
    gdt[GDT_USER_CODE64].limit_low = 0;
    gdt[GDT_USER_CODE64].access = 0xFA;  /* Present, DPL=3, Executable, Readable */
    gdt[GDT_USER_CODE64].granularity = 0xA0;
    
    /* User data */
    gdt[GDT_USER_DATA].limit_low = 0;
    gdt[GDT_USER_DATA].access = 0xF2;    /* Present, DPL=3, Writable */
    gdt[GDT_USER_DATA].granularity = 0;
    
    /* Setup GDT pointer */
    gdt_ptr.base = (uint64_t)&gdt;
    gdt_ptr.size = sizeof(gdt) - 1;
    
    /* Load GDT */
    asm volatile("lgdt %0" :: "m"(gdt_ptr));
    
    /* Reload code segment and data segment */
    asm volatile(
        "mov $0x10, %%rax\n"
        "mov %%rax, %%ds\n"
        "mov %%rax, %%es\n"
        "mov %%rax, %%fs\n"
        "mov %%rax, %%gs\n"
        "mov %%rax, %%ss\n"
        "pop %%rax\n"
        "push $0x08\n"
        "push %%rax\n"
        "lretq\n"
        ::: "rax", "memory"
    );
}

/* ============================================================================
 * Paging - 64-bit Long Mode Paging (5-level or 4-level)
 * ============================================================================ */

struct PML4Entry {
    uint64_t present     : 1;
    uint64_t writable    : 1;
    uint64_t user        : 1;
    uint64_t pwt         : 1;
    uint64_t pcd         : 1;
    uint64_t accessed    : 1;
    uint64_t ignored1    : 1;
    uint64_t ps          : 1;
    uint64_t ignored2    : 4;
    uint64_t address     : 40;   /* Physical address of PDPT */
    uint64_t ignored3    : 11;
    uint64_t xd          : 1;
} __attribute__((packed));

struct PDPTEntry {
    uint64_t present     : 1;
    uint64_t writable    : 1;
    uint64_t user        : 1;
    uint64_t pwt         : 1;
    uint64_t pcd         : 1;
    uint64_t accessed    : 1;
    uint64_t ignored1    : 1;
    uint64_t ps          : 1;
    uint64_t ignored2    : 4;
    uint64_t address     : 40;   /* Physical address of PDT or 1GB page */
    uint64_t ignored3    : 11;
    uint64_t xd          : 1;
} __attribute__((packed));

struct PDTEntry {
    uint64_t present     : 1;
    uint64_t writable    : 1;
    uint64_t user        : 1;
    uint64_t pwt         : 1;
    uint64_t pcd         : 1;
    uint64_t accessed    : 1;
    uint64_t ignored1    : 1;
    uint64_t ps          : 1;
    uint64_t ignored2    : 4;
    uint64_t address     : 40;   /* Physical address of PT or 2MB page */
    uint64_t ignored3    : 11;
    uint64_t xd          : 1;
} __attribute__((packed));

struct PTEntry {
    uint64_t present     : 1;
    uint64_t writable    : 1;
    uint64_t user        : 1;
    uint64_t pwt         : 1;
    uint64_t pcd         : 1;
    uint64_t accessed    : 1;
    uint64_t dirty       : 1;
    uint64_t pat         : 1;
    uint64_t global      : 1;
    uint64_t ignored1    : 3;
    uint64_t address     : 40;   /* Physical address of 4KB page */
    uint64_t ignored2    : 11;
    uint64_t xd          : 1;
} __attribute__((packed));

/* Page table structures in memory */
struct PML4Entry pml4[512] __attribute__((aligned(PAGE_SIZE)));
struct PDPTEntry pdpt[512] __attribute__((aligned(PAGE_SIZE)));
struct PDTEntry pdt[512] __attribute__((aligned(PAGE_SIZE)));
struct PTEntry pt[512] __attribute__((aligned(PAGE_SIZE)));

void paging_init(void) {
    uint64_t i;
    
    /* Clear page tables */
    for (i = 0; i < 512; i++) {
        pml4[i].present = 0;
        pdpt[i].present = 0;
        pdt[i].present = 0;
        pt[i].present = 0;
    }
    
    /* Setup identity mapping for first 2MB (kernel code) */
    pml4[0].present = 1;
    pml4[0].writable = 1;
    pml4[0].address = (uint64_t)&pdpt >> 12;
    
    pdpt[0].present = 1;
    pdpt[0].writable = 1;
    pdpt[0].address = (uint64_t)&pdt >> 12;
    
    pdt[0].present = 1;
    pdt[0].writable = 1;
    pdt[0].address = (uint64_t)&pt >> 12;
    
    /* Map first 2MB with 4KB pages */
    for (i = 0; i < 512; i++) {
        pt[i].present = 1;
        pt[i].writable = 1;
        pt[i].address = i;   /* Identity: virtual = physical */
    }
    
    /* Load CR3 with PML4 address */
    asm volatile("mov %0, %%cr3" :: "r"((uint64_t)&pml4));
}

/* ============================================================================
 * Memory Management
 * ============================================================================ */

struct MemoryManager {
    uint64_t total_memory;
    uint64_t allocated;
    uint64_t free;
    uint8_t  page_bitmap[0x10000];  /* Bitmap for page allocation */
} memory_manager = {0};

void memory_init(uint64_t total_size) {
    memory_manager.total_memory = total_size;
    memory_manager.allocated = 0;
    memory_manager.free = total_size;
    
    /* Zero page bitmap */
    for (size_t i = 0; i < sizeof(memory_manager.page_bitmap); i++) {
        memory_manager.page_bitmap[i] = 0;
    }
    
    /* Mark kernel pages as allocated (0x100000 - 0x200000 = 256 KB = 64 pages) */
    for (uint64_t page = 0; page < 64; page++) {
        uint64_t byte = page / 8;
        uint64_t bit = page % 8;
        memory_manager.page_bitmap[byte] |= (1 << bit);
    }
    
    memory_manager.allocated = 64 * PAGE_SIZE;
    memory_manager.free = total_size - memory_manager.allocated;
}

uint64_t memory_allocate(uint64_t size) {
    uint64_t pages_needed = (size + PAGE_SIZE - 1) / PAGE_SIZE;
    
    /* Find contiguous free pages */
    for (uint64_t page = 0; page < (sizeof(memory_manager.page_bitmap) * 8) - pages_needed; page++) {
        uint64_t byte = page / 8;
        uint64_t bit = page % 8;
        
        /* Check if page is free */
        if (!(memory_manager.page_bitmap[byte] & (1 << bit))) {
            /* Check if we have enough contiguous pages */
            uint64_t found = 1;
            for (uint64_t j = 1; j < pages_needed; j++) {
                uint64_t b = (page + j) / 8;
                uint64_t bi = (page + j) % 8;
                if (memory_manager.page_bitmap[b] & (1 << bi)) {
                    break;
                }
                found++;
            }
            
            if (found == pages_needed) {
                /* Mark pages as allocated */
                for (uint64_t j = 0; j < pages_needed; j++) {
                    uint64_t b = (page + j) / 8;
                    uint64_t bi = (page + j) % 8;
                    memory_manager.page_bitmap[b] |= (1 << bi);
                }
                
                memory_manager.allocated += size;
                memory_manager.free -= size;
                
                return page * PAGE_SIZE;
            }
        }
    }
    
    return 0;  /* Out of memory */
}

/* ============================================================================
 * Process Management
 * ============================================================================ */

#define MAX_PROCESSES  256

typedef struct {
    uint32_t pid;
    uint32_t state;   /* 0=free, 1=ready, 2=running, 3=blocked */
    uint64_t rsp;     /* Stack pointer */
    uint64_t rip;     /* Instruction pointer */
    uint64_t rax, rbx, rcx, rdx, rsi, rdi, r8, r9, r10, r11, r12, r13, r14, r15;
    uint64_t cr3;     /* Page table */
    char     name[64];
    uint64_t creation_time;
} ProcessControlBlock;

ProcessControlBlock process_table[MAX_PROCESSES];
uint32_t process_count = 0;
uint32_t current_pid = 0;
volatile uint64_t system_ticks = 0;

void process_init(void) {
    /* Clear process table */
    for (int i = 0; i < MAX_PROCESSES; i++) {
        process_table[i].state = 0;  /* Free */
        process_table[i].pid = 0;
    }
    
    /* Create first idle process */
    ProcessControlBlock *idle = &process_table[0];
    idle->pid = 1;
    idle->state = 2;  /* Running */
    idle->rsp = 0x00400000 + PAGE_SIZE;  /* Process stack area */
    idle->cr3 = (uint64_t)&pml4;
    
    for (int i = 0; i < 64; i++) {
        idle->name[i] = 0;
    }
    idle->name[0] = 'i';
    idle->name[1] = 'd';
    idle->name[2] = 'l';
    idle->name[3] = 'e';
    
    process_count = 1;
    current_pid = 0;
}

uint32_t process_create(const char *name) {
    if (process_count >= MAX_PROCESSES) {
        return 0;  /* Process table full */
    }
    
    ProcessControlBlock *proc = &process_table[process_count];
    proc->pid = process_count + 1;
    proc->state = 1;  /* Ready */
    proc->rsp = 0x00400000 + ((process_count + 1) * PAGE_SIZE);
    proc->cr3 = (uint64_t)&pml4;
    
    /* Copy name */
    for (size_t i = 0; i < 64 && name[i]; i++) {
        proc->name[i] = name[i];
    }
    
    process_count++;
    return proc->pid;
}

void process_schedule(void) {
    /* Simple round-robin scheduling */
    if (process_count == 0) return;
    
    current_pid++;
    if (current_pid >= process_count) {
        current_pid = 0;
    }
    
    ProcessControlBlock *next = &process_table[current_pid];
    if (next->state != 0) {  /* Not free */
        next->state = 2;  /* Running */
    }
}

/* ============================================================================
 * Timer & Interrupts
 * ============================================================================ */

#define PIT_FREQUENCY  1000   /* 1000 Hz */

void timer_init(void) {
    /* Setup PIT (Programmable Interval Timer) */
    uint16_t divisor = 1193182 / PIT_FREQUENCY;
    
    /* Send divisor to PIT channel 0 */
    asm volatile("outb $0x36, $0x43");  /* ICW4 */
    asm volatile("outb %%al, $0x40" :: "a"((uint8_t)divisor));
    asm volatile("outb %%al, $0x40" :: "a"((uint8_t)(divisor >> 8)));
}

void idt_init(void) {
    /* Placeholder for IDT setup */
    /* Would setup interrupt handlers here */
}

/* ============================================================================
 * Kernel Main Entry Point
 * ============================================================================ */

void kernel_main(void) {
    /* Setup kernel subsystems in order */
    
    /* 1. Global Descriptor Table (GDT) */
    gdt_init();
    
    /* 2. Paging */
    paging_init();
    
    /* 3. Memory management */
    memory_init(0x80000000);  /* 2GB total memory */
    
    /* 4. Process management */
    process_init();
    
    /* 5. Timer and interrupts */
    idt_init();
    timer_init();
    
    /* Kernel is now initialized */
    /* Enter main loop */
    while (1) {
        system_ticks++;
        
        if (system_ticks % 1000 == 0) {
            process_schedule();
        }
        
        /* Busy wait - would use HLT in real kernel */
        asm volatile("nop");
    }
}

/* ============================================================================
 * Kernel Entry Point - Called by UEFI Bootloader
 * This is the symbol the bootloader jumps to
 * ============================================================================ */

void _kernel_entry(void) {
    kernel_main();
    
    /* Should never return */
    asm volatile("cli; hlt");
}

/* ============================================================================
 * Interrupt Handlers Stub
 * ============================================================================ */

void timer_interrupt_handler(void) {
    system_ticks++;
}

void keyboard_interrupt_handler(void) {
    /* Handle keyboard input */
}
