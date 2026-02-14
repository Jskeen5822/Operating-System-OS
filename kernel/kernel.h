#ifndef KERNEL_H
#define KERNEL_H

#include "../include/types.h"
#include "../include/defs.h"


void kernel_init(void);
void setup_interrupts(void);
void setup_memory(void);
void setup_filesystem(void);


extern ProcessControlBlock *current_process;
extern ProcessControlBlock process_table[MAX_PROCESSES];
extern uint32_t process_count;


extern uint32_t *page_directory;
extern uint8_t memory_bitmap[MAX_PAGES / 8];


typedef struct {
    Inode inode_table[MAX_FILES];
    uint8_t block_bitmap[MAX_BLOCKS / 8];
    uint32_t total_blocks;
    uint32_t free_blocks;
} FileSystem;

extern FileSystem fs;


extern uint64_t system_ticks;
extern uint32_t schedule_interval;


uint32_t sys_fork(void);
uint32_t sys_exit(int status);
uint32_t sys_wait(uint32_t pid);
uint32_t sys_exec(const char *path);
uint32_t sys_open(const char *filename, uint32_t flags);
uint32_t sys_close(uint32_t fd);
uint32_t sys_read(uint32_t fd, void *buffer, uint32_t count);
uint32_t sys_write(uint32_t fd, const void *buffer, uint32_t count);


void panic(const char *message);
void printf(const char *format, ...);
void memset(void *dest, uint8_t value, size_t count);
void memcpy(void *dest, const void *src, size_t count);
int strcmp(const char *str1, const char *str2);
int strncmp(const char *str1, const char *str2, size_t n);
size_t strlen(const char *str);
char *strcpy(char *dest, const char *src);
char *strncpy(char *dest, const char *src, size_t n);

#endif
