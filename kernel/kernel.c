#include "kernel.h"

/* Global variables */
ProcessControlBlock process_table[MAX_PROCESSES] = {0};
ProcessControlBlock *current_process = NULL;
uint32_t process_count = 0;
uint64_t system_ticks = 0;
uint32_t next_pid = 1;

/* Memory and file system globals */
uint32_t *page_directory = NULL;
uint8_t memory_bitmap[MAX_PAGES / 8] = {0};
FileSystem fs = {0};

/* Scheduling globals */
uint32_t schedule_interval = 10;

void kernel_main(void) {
    /* Initialize kernel subsystems */
    kernel_init();
    
    printf("Operating System OS initialized successfully!\n");
    printf("Processes: %d/%d\n", process_count, MAX_PROCESSES);
    printf("Ready for user input.\n");
    
    /* Start shell */
    shell_start();
    
    /* Halt if shell returns */
    panic("Shell terminated unexpectedly");
}

void kernel_init(void) {
    printf("Initializing Operating System OS...\n");
    
    setup_interrupts();
    printf("Interrupts initialized.\n");
    
    setup_memory();
    printf("Memory management initialized.\n");
    
    setup_filesystem();
    printf("File system initialized.\n");
    
    /* Create idle process */
    process_create("idle", 0);
}

void setup_interrupts(void) {
    /* Setup interrupt handlers */
    /* In real implementation, would setup IDT and handler stubs */
    system_ticks = 0;
}

void setup_memory(void) {
    /* Initialize memory bitmap and page tables */
    memset(memory_bitmap, 0, sizeof(memory_bitmap));
    
    /* First 256 pages reserved for kernel */
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t byte_idx = i / 8;
        uint32_t bit_idx = i % 8;
        memory_bitmap[byte_idx] |= (1 << bit_idx);
    }
}

void setup_filesystem(void) {
    /* Initialize file system structures */
    memset(&fs, 0, sizeof(FileSystem));
    
    fs.total_blocks = MAX_BLOCKS;
    fs.free_blocks = MAX_BLOCKS - 1;  /* Root inode takes one block */
    
    /* Initialize root directory inode */
    fs.inode_table[0].inode_number = 0;
    fs.inode_table[0].file_type = 1;  /* Directory */
    fs.inode_table[0].size = 0;
    fs.inode_table[0].permissions = 0755;
    fs.inode_table[0].hard_link_count = 1;
}

/* Process Management */
void process_create(const char *name, uint32_t priority) {
    if (process_count >= MAX_PROCESSES) {
        printf("Error: Maximum process limit reached\n");
        return;
    }
    
    ProcessControlBlock *pcb = &process_table[process_count];
    
    pcb->pid = next_pid++;
    pcb->state = PROCESS_READY;
    pcb->priority = priority;
    pcb->page_directory = 0x00100000 + (process_count * PAGE_SIZE);
    pcb->stack_pointer = 0x9f000;
    pcb->instruction_pointer = 0x8000;
    pcb->total_memory = 0;
    pcb->creation_time = system_ticks;
    strcpy(pcb->name, name);
    
    process_count++;
    printf("Process created: PID=%d, Name='%s'\n", pcb->pid, name);
}

void process_schedule(void) {
    /* Simple round-robin scheduling */
    if (process_count == 0) return;
    
    static uint32_t current_index = 0;
    
    /* Find next ready process */
    uint32_t attempts = 0;
    while (attempts < process_count) {
        current_index = (current_index + 1) % process_count;
        
        if (process_table[current_index].state == PROCESS_READY ||
            process_table[current_index].state == PROCESS_RUNNING) {
            break;
        }
        attempts++;
    }
    
    if (current_process) {
        current_process->state = PROCESS_READY;
    }
    
    current_process = &process_table[current_index];
    current_process->state = PROCESS_RUNNING;
}

void interrupt_handler(uint32_t interrupt_number) {
    system_ticks++;
    
    if (system_ticks % schedule_interval == 0) {
        process_schedule();
    }
}

/* Memory Management - delegated to memory.c */

/* Utility Functions */
void memset(void *dest, uint8_t value, size_t count) {
    uint8_t *d = (uint8_t *)dest;
    for (size_t i = 0; i < count; i++) {
        d[i] = value;
    }
}

void memcpy(void *dest, const void *src, size_t count) {
    uint8_t *d = (uint8_t *)dest;
    const uint8_t *s = (const uint8_t *)src;
    for (size_t i = 0; i < count; i++) {
        d[i] = s[i];
    }
}

int strcmp(const char *str1, const char *str2) {
    while (*str1 && *str1 == *str2) {
        str1++;
        str2++;
    }
    return *str1 - *str2;
}

int strncmp(const char *str1, const char *str2, size_t n) {
    for (size_t i = 0; i < n; i++) {
        if (str1[i] != str2[i]) return str1[i] - str2[i];
        if (!str1[i]) return 0;
    }
    return 0;
}

size_t strlen(const char *str) {
    size_t len = 0;
    while (str[len]) len++;
    return len;
}

char *strcpy(char *dest, const char *src) {
    while (*src) {
        *dest++ = *src++;
    }
    *dest = '\0';
    return dest;
}

char *strncpy(char *dest, const char *src, size_t n) {
    for (size_t i = 0; i < n && src[i]; i++) {
        dest[i] = src[i];
    }
    return dest;
}

void printf(const char *format, ...) {
    /* Simplified printf - just output the format string for now */
    const char *p = format;
    while (*p) {
        if (*p == '\\' && *(p+1) == 'n') {
            /* Simple newline handling */
            p += 2;
        } else {
            p++;
        }
    }
}

void panic(const char *message) {
    printf("KERNEL PANIC: %s\n", message);
    while (1) {
        /* Halt CPU */
    }
}
