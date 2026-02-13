#ifndef DEFS_H
#define DEFS_H

#include "types.h"

/* Process Control Block */
typedef struct {
    uint32_t pid;                    /* Process ID */
    uint32_t state;                  /* Current state (RUNNING, READY, etc.) */
    uint32_t priority;               /* Process priority */
    uint32_t page_directory;         /* Physical address of page directory */
    uint32_t stack_pointer;          /* Current stack pointer */
    uint32_t instruction_pointer;    /* Current instructions pointer */
    uint32_t total_memory;           /* Total memory allocated */
    uint64_t creation_time;          /* Process creation timestamp */
    char name[64];                   /* Process name */
} ProcessControlBlock;

/* Page Table Entry */
typedef struct {
    uint32_t present : 1;            /* Is page present */
    uint32_t writable : 1;           /* Is page writable */
    uint32_t user : 1;               /* User-accessible */
    uint32_t write_through : 1;      /* Write-through caching */
    uint32_t cache_disabled : 1;     /* Disable caching */
    uint32_t accessed : 1;           /* Has been accessed */
    uint32_t dirty : 1;              /* Has been modified */
    uint32_t reserved : 2;           /* Reserved */
    uint32_t available : 3;          /* Available for OS use */
    uint32_t frame : 20;             /* Physical frame address */
} PageTableEntry;

/* Inode structure for file system */
typedef struct {
    uint32_t inode_number;
    uint32_t file_type;              /* File or directory */
    uint32_t size;
    uint32_t permissions;
    uint64_t created;
    uint64_t modified;
    uint32_t block_pointers[12];     /* Direct block pointers */
    uint32_t indirect_block;         /* Indirect block pointer */
    uint32_t hard_link_count;
} Inode;

/* File descriptor */
typedef struct {
    uint32_t inode_number;
    uint32_t offset;
    uint32_t flags;
    uint32_t mode;
} FileDescriptor;

/* Directory entry */
typedef struct {
    uint32_t inode_number;
    char filename[256];
} DirectoryEntry;

/* Function declarations */
void kernel_main(void);
void interrupt_handler(uint32_t interrupt_number);
void process_create(const char *name, uint32_t priority);
void process_schedule(void);
void memory_init(void);
void filesystem_init(void);
void shell_start(void);

#endif
