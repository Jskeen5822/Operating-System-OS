

#ifndef __TYPES64_H__
#define __TYPES64_H__


typedef unsigned char       uint8_t;
typedef signed char         int8_t;
typedef unsigned short      uint16_t;
typedef signed short        int16_t;
typedef unsigned int        uint32_t;
typedef signed int          int32_t;
typedef unsigned long long  uint64_t;
typedef signed long long    int64_t;


typedef uint64_t size_t;
typedef int64_t ssize_t;


typedef uint64_t paddr_t;  
typedef uint64_t vaddr_t;  


typedef int bool;
#define true  1
#define false 0


#ifndef NULL
#define NULL ((void *)0)
#endif


#define PAGE_SIZE           0x1000          
#define PAGE_SHIFT          12
#define PAGE_MASK           0xFFF

#define KERNEL_VIRT_BASE    0xFFFF800000000000ULL  


#define MAX_PROCESSES       256
#define MAX_INODES          512
#define MAX_FILES           1024
#define MAX_DOMAINS         16
#define MAX_CPU_CORES       3


#define ARCH_X86_64         1
#define LONG_MODE           1
#define BITS_64             1


#define KB(x)   ((x) * 1024ULL)
#define MB(x)   ((x) * 1024 * 1024ULL)
#define GB(x)   ((x) * 1024 * 1024 * 1024ULL)

#define MAX_MEMORY          GB(8)           
#define MIN_MEMORY          MB(256)         


#define TIMER_FREQUENCY     1000            

#endif 
