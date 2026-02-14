#ifndef TYPES_H
#define TYPES_H


typedef unsigned char uint8_t;
typedef signed char int8_t;
typedef unsigned short uint16_t;
typedef signed short int16_t;
typedef unsigned int uint32_t;
typedef signed int int32_t;
typedef unsigned long uint64_t;
typedef signed long int64_t;

typedef unsigned int size_t;
typedef signed int ssize_t;


typedef uint32_t bool;
#define true 1
#define false 0


#ifndef NULL
#define NULL ((void *)0)
#endif


#define PROCESS_READY 0
#define PROCESS_RUNNING 1
#define PROCESS_WAITING 2
#define PROCESS_BLOCKED 3
#define PROCESS_TERMINATED 4


#define PAGE_SIZE 4096
#define MAX_PROCESSES 256
#define MAX_PAGES 65536
#define KERNEL_SPACE 0xC0000000


#define MAX_FILES 512
#define MAX_FILENAME 256
#define INODE_SIZE 128
#define BLOCK_SIZE 4096
#define MAX_BLOCKS 8192

#endif
