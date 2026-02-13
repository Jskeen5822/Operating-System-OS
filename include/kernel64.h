/* 64-bit Kernel Definitions - x86-64 Architecture */

#ifndef __KERNEL64_H__
#define __KERNEL64_H__

#include "types64.h"

/* ============================================================================
 * Boot Information Structure (from UEFI bootloader)
 * ============================================================================ */
typedef struct {
    uint64_t total_memory;      /* Total system memory in bytes */
    uint32_t cpu_count;         /* Number of CPUs detected */
    uint64_t boot_time;         /* Boot time in milliseconds */
    uint32_t video_width;       /* Video framebuffer width */
    uint32_t video_height;      /* Video framebuffer height */
    uint64_t rsdp_address;      /* ACPI RSDP address */
    uint64_t bootloader_id;     /* Identifier of bootloader (UEFI) */
} BootInfo;

/* ============================================================================
 * Process & Scheduling
 * ============================================================================ */

/* Process states */
#define PROCESS_FREE        0
#define PROCESS_READY       1
#define PROCESS_RUNNING     2
#define PROCESS_BLOCKED     3
#define PROCESS_TERMINATED  4

typedef struct Domain Domain;

typedef struct {
    uint32_t pid;               /* Process ID */
    uint32_t parent_pid;        /* Parent process ID */
    uint32_t state;             /* Process state */
    uint32_t priority;          /* Scheduling priority */
    uint64_t creation_time;     /* Creation time in ticks */
    uint64_t cpu_time;          /* CPU time used */
    uint32_t memory_pages;      /* Pages allocated */
    char name[64];              /* Process name */
    Domain *domain;             /* Associated domain */
    uint64_t page_table;        /* Page table address */
} Process;

typedef struct {
    Process processes[MAX_PROCESSES];
    uint32_t count;
    uint32_t current;
} ProcessTable;

/* ============================================================================
 * Memory Management - 64-bit Paging
 * ============================================================================ */

typedef struct {
    uint64_t total_pages;           /* Total available pages */
    uint64_t allocated_pages;       /* Pages currently allocated */
    uint64_t page_tables_allocated; /* Page table pages */
    uint64_t page_bitmap_size;      /* Size of bitmap in bytes */
} MemoryManager;

/* ============================================================================
 * File System - Unix-like Inode Structure
 * ============================================================================ */

#define INODE_FILE          1
#define INODE_DIR           2
#define INODE_SYMLINK       3

typedef struct {
    uint32_t inode_number;      /* Inode number */
    uint32_t type;              /* File type (file, directory, symlink) */
    uint32_t permissions;       /* File permissions */
    uint32_t uid;               /* User ID */
    uint32_t gid;               /* Group ID */
    uint64_t size;              /* File size in bytes */
    uint64_t creation_time;     /* Creation time */
    uint64_t modification_time; /* Last modification time */
    uint64_t access_time;       /* Last access time */
    char filename[256];         /* File name */
    uint64_t direct_blocks[12]; /* Direct block pointers */
    uint64_t indirect_block;    /* Indirect block pointer */
} Inode;

typedef struct {
    Inode inodes[MAX_INODES];
    uint32_t inode_count;
    Inode *root;
} FileSystem;

/* ============================================================================
 * Domain Management (Qubes OS inspired compartmentalization)
 * ============================================================================ */

/* Domain types */
#define DOMAIN_SYSTEM       0   /* System domain (sys) */
#define DOMAIN_USER         1   /* User application domain */
#define DOMAIN_NETWORK      2   /* Network domain */
#define DOMAIN_STORAGE      3   /* Storage domain */
#define DOMAIN_USB          4   /* USB domain */

/* Domain colors (for UI) */
#define COLOR_RED           0xFF0000    /* System - Red */
#define COLOR_GREEN         0x00AA00    /* User - Green */
#define COLOR_BLUE          0x0066FF    /* Network - Blue */
#define COLOR_YELLOW        0xFFAA00    /* Storage - Orange */
#define COLOR_PURPLE        0xFF00FF    /* USB - Purple */

typedef struct Domain {
    uint32_t domain_id;         /* Domain ID */
    uint32_t type;              /* Domain type */
    uint32_t color;             /* UI color code */
    char name[64];              /* Domain name */
    uint32_t process_count;     /* Number of processes */
    uint64_t memory_limit;      /* Memory limit in bytes */
    uint64_t memory_used;       /* Memory currently used */
    bool is_isolated;           /* Is domain isolated from others */
    bool has_network;           /* Does domain have network access */
    bool has_usb;               /* Does domain have USB access */
} Domain;

/* ============================================================================
 * Kernel Functions
 * ============================================================================ */

/* Initialization */
void kernel_main(BootInfo *boot_info);
void kernel_initialize(void);
void kernel_ready(void);

/* Memory management */
void memory_initialize(void);
uint64_t memory_allocate(uint64_t size);
void memory_free(uint64_t address, uint64_t size);
uint64_t memory_get_total_memory(void);
uint64_t memory_get_allocated(void);
uint64_t memory_get_free(void);

/* Process management */
void process_initialize(void);
uint32_t process_create(const char *name, uint32_t domain_id);
Process* process_get(uint32_t pid);
void process_schedule(void);

/* File system */
void filesystem_initialize(void);
Inode* filesystem_create_inode(const char *name, uint32_t type);
Inode* filesystem_find_by_path(const char *path);

/* Domain management */
void domain_initialize(void);
uint32_t domain_create(const char *name, uint32_t type, uint32_t color);
Domain* domain_get(uint32_t domain_id);

/* Utility functions */
void string_copy(const char *src, char *dst, uint32_t max_len);
int32_t string_compare(const char *s1, const char *s2);
uint32_t string_length(const char *str);
void memory_set(void *ptr, uint8_t value, uint64_t size);
void memory_copy(const void *src, void *dst, uint64_t size);

/* Architecture setup */
void setup_gdt(void);
void setup_idt(void);
void setup_paging(void);
void setup_interrupts(void);
void setup_apic(void);

/* Global state */
extern BootInfo *g_boot_info;
extern ProcessTable g_process_table;
extern MemoryManager g_memory;
extern FileSystem g_filesystem;
extern Domain g_domains[MAX_DOMAINS];
extern uint32_t g_domain_count;
extern volatile uint64_t g_ticks;
extern volatile uint32_t g_cpu_count;
extern volatile uint64_t g_total_memory;

#endif /* __KERNEL64_H__ */
