#ifndef DEFS_H
#define DEFS_H

#include "types.h"


typedef struct {
    uint32_t pid;                    
    uint32_t state;                  
    uint32_t priority;               
    uint32_t page_directory;         
    uint32_t stack_pointer;          
    uint32_t instruction_pointer;    
    uint32_t total_memory;           
    uint64_t creation_time;          
    char name[64];                   
} ProcessControlBlock;


typedef struct {
    uint32_t present : 1;            
    uint32_t writable : 1;           
    uint32_t user : 1;               
    uint32_t write_through : 1;      
    uint32_t cache_disabled : 1;     
    uint32_t accessed : 1;           
    uint32_t dirty : 1;              
    uint32_t reserved : 2;           
    uint32_t available : 3;          
    uint32_t frame : 20;             
} PageTableEntry;


typedef struct {
    uint32_t inode_number;
    uint32_t file_type;              
    uint32_t size;
    uint32_t permissions;
    uint64_t created;
    uint64_t modified;
    uint32_t block_pointers[12];     
    uint32_t indirect_block;         
    uint32_t hard_link_count;
} Inode;


typedef struct {
    uint32_t inode_number;
    uint32_t offset;
    uint32_t flags;
    uint32_t mode;
} FileDescriptor;


typedef struct {
    uint32_t inode_number;
    char filename[256];
} DirectoryEntry;


void kernel_main(void);
void interrupt_handler(uint32_t interrupt_number);
void process_create(const char *name, uint32_t priority);
void process_schedule(void);
void memory_init(void);
void filesystem_init(void);
void shell_start(void);

#endif
