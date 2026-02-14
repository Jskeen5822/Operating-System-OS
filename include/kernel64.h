

#ifndef __KERNEL64_H__
#define __KERNEL64_H__

#include "types64.h"


typedef struct {
    uint64_t total_memory;      
    uint32_t cpu_count;         
    uint64_t boot_time;         
    uint32_t video_width;       
    uint32_t video_height;      
    uint64_t rsdp_address;      
    uint64_t bootloader_id;     
} BootInfo;




#define PROCESS_FREE        0
#define PROCESS_READY       1
#define PROCESS_RUNNING     2
#define PROCESS_BLOCKED     3
#define PROCESS_TERMINATED  4

typedef struct Domain Domain;

typedef struct {
    uint32_t pid;               
    uint32_t parent_pid;        
    uint32_t state;             
    uint32_t priority;          
    uint64_t creation_time;     
    uint64_t cpu_time;          
    uint32_t memory_pages;      
    char name[64];              
    Domain *domain;             
    uint64_t page_table;        
} Process;

typedef struct {
    Process processes[MAX_PROCESSES];
    uint32_t count;
    uint32_t current;
} ProcessTable;



typedef struct {
    uint64_t total_pages;           
    uint64_t allocated_pages;       
    uint64_t page_tables_allocated; 
    uint64_t page_bitmap_size;      
} MemoryManager;



#define INODE_FILE          1
#define INODE_DIR           2
#define INODE_SYMLINK       3

typedef struct {
    uint32_t inode_number;      
    uint32_t type;              
    uint32_t permissions;       
    uint32_t uid;               
    uint32_t gid;               
    uint64_t size;              
    uint64_t creation_time;     
    uint64_t modification_time; 
    uint64_t access_time;       
    char filename[256];         
    uint64_t direct_blocks[12]; 
    uint64_t indirect_block;    
} Inode;

typedef struct {
    Inode inodes[MAX_INODES];
    uint32_t inode_count;
    Inode *root;
} FileSystem;




#define DOMAIN_SYSTEM       0   
#define DOMAIN_USER         1   
#define DOMAIN_NETWORK      2   
#define DOMAIN_STORAGE      3   
#define DOMAIN_USB          4   


#define COLOR_RED           0xFF0000    
#define COLOR_GREEN         0x00AA00    
#define COLOR_BLUE          0x0066FF    
#define COLOR_YELLOW        0xFFAA00    
#define COLOR_PURPLE        0xFF00FF    

typedef struct Domain {
    uint32_t domain_id;         
    uint32_t type;              
    uint32_t color;             
    char name[64];              
    uint32_t process_count;     
    uint64_t memory_limit;      
    uint64_t memory_used;       
    bool is_isolated;           
    bool has_network;           
    bool has_usb;               
} Domain;




void kernel_main(BootInfo *boot_info);
void kernel_initialize(void);
void kernel_ready(void);


void memory_initialize(void);
uint64_t memory_allocate(uint64_t size);
void memory_free(uint64_t address, uint64_t size);
uint64_t memory_get_total_memory(void);
uint64_t memory_get_allocated(void);
uint64_t memory_get_free(void);


void process_initialize(void);
uint32_t process_create(const char *name, uint32_t domain_id);
Process* process_get(uint32_t pid);
void process_schedule(void);


void filesystem_initialize(void);
Inode* filesystem_create_inode(const char *name, uint32_t type);
Inode* filesystem_find_by_path(const char *path);


void domain_initialize(void);
uint32_t domain_create(const char *name, uint32_t type, uint32_t color);
Domain* domain_get(uint32_t domain_id);


void string_copy(const char *src, char *dst, uint32_t max_len);
int32_t string_compare(const char *s1, const char *s2);
uint32_t string_length(const char *str);
void memory_set(void *ptr, uint8_t value, uint64_t size);
void memory_copy(const void *src, void *dst, uint64_t size);


void setup_gdt(void);
void setup_idt(void);
void setup_paging(void);
void setup_interrupts(void);
void setup_apic(void);


extern BootInfo *g_boot_info;
extern ProcessTable g_process_table;
extern MemoryManager g_memory;
extern FileSystem g_filesystem;
extern Domain g_domains[MAX_DOMAINS];
extern uint32_t g_domain_count;
extern volatile uint64_t g_ticks;
extern volatile uint32_t g_cpu_count;
extern volatile uint64_t g_total_memory;

#endif 
