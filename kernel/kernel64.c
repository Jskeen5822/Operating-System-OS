

#include "../include/types64.h"
#include "../include/kernel64.h"


BootInfo *g_boot_info = NULL;
ProcessTable g_process_table = {0};
MemoryManager g_memory = {0};
FileSystem g_filesystem = {0};


volatile uint64_t g_ticks = 0;
volatile uint32_t g_cpu_count = 0;
volatile uint64_t g_total_memory = 0;


Domain g_domains[MAX_DOMAINS] = {0};
uint32_t g_domain_count = 0;


void kernel_main(BootInfo *boot_info) {
    
    g_boot_info = boot_info;
    g_total_memory = boot_info->total_memory;
    g_cpu_count = boot_info->cpu_count > 3 ? 3 : boot_info->cpu_count;
    
    
    kernel_initialize();
    memory_initialize();
    filesystem_initialize();
    process_initialize();
    domain_initialize();
    
    
    setup_interrupts();
    setup_apic();
    
    
    kernel_ready();
}


void kernel_initialize(void) {
    
    setup_gdt();
    setup_idt();
    setup_paging();
    
    
    g_memory.total_pages = g_total_memory / PAGE_SIZE;
    g_memory.allocated_pages = 0;
    g_memory.page_tables_allocated = 0;
    
    
    g_process_table.count = 0;
    for (int i = 0; i < MAX_PROCESSES; i++) {
        g_process_table.processes[i].pid = 0;
        g_process_table.processes[i].state = PROCESS_FREE;
    }
}


void memory_initialize(void) {
    
    g_memory.page_bitmap_size = g_memory.total_pages / 8;
    g_memory.allocated_pages = 0;
}

uint64_t memory_allocate(uint64_t size) {
    uint64_t pages_needed = (size + PAGE_SIZE - 1) / PAGE_SIZE;
    
    if (g_memory.allocated_pages + pages_needed > g_memory.total_pages) {
        return 0; 
    }
    
    uint64_t address = g_memory.allocated_pages * PAGE_SIZE + KERNEL_VIRT_BASE;
    g_memory.allocated_pages += pages_needed;
    
    return address;
}

void memory_free(uint64_t address, uint64_t size) {
    
    
}

uint64_t memory_get_total_memory(void) {
    return g_total_memory;
}

uint64_t memory_get_allocated(void) {
    return g_memory.allocated_pages * PAGE_SIZE;
}

uint64_t memory_get_free(void) {
    return (g_memory.total_pages - g_memory.allocated_pages) * PAGE_SIZE;
}


void process_initialize(void) {
    g_process_table.count = 1;
    
    
    Process* idle = &g_process_table.processes[0];
    idle->pid = 1;
    idle->state = PROCESS_RUNNING;
    idle->priority = 20;
    idle->parent_pid = 0;
    idle->creation_time = g_ticks;
    idle->memory_pages = 4;
    idle->cpu_time = 0;
    string_copy("idle", idle->name, 64);
    idle->domain = &g_domains[0]; 
}

uint32_t process_create(const char *name, uint32_t domain_id) {
    if (g_process_table.count >= MAX_PROCESSES) {
        return 0;
    }
    
    Process *proc = &g_process_table.processes[g_process_table.count];
    proc->pid = g_process_table.count + 1;
    proc->state = PROCESS_READY;
    proc->priority = 0;
    proc->creation_time = g_ticks;
    proc->memory_pages = 4;
    proc->cpu_time = 0;
    
    if (domain_id < MAX_DOMAINS) {
        proc->domain = &g_domains[domain_id];
    } else {
        proc->domain = &g_domains[0];
    }
    
    string_copy(name, proc->name, 64);
    
    g_process_table.count++;
    return proc->pid;
}

Process* process_get(uint32_t pid) {
    if (pid == 0 || pid > g_process_table.count) {
        return NULL;
    }
    return &g_process_table.processes[pid - 1];
}

void process_schedule(void) {
    
    static uint32_t current_index = 0;
    
    if (g_process_table.count == 0) return;
    
    
    Process *current = &g_process_table.processes[current_index];
    if (current->state == PROCESS_RUNNING) {
        current->state = PROCESS_READY;
        current->cpu_time++;
    }
    
    
    uint32_t next_index = (current_index + 1) % g_process_table.count;
    for (uint32_t i = 0; i < g_process_table.count; i++) {
        uint32_t idx = (current_index + 1 + i) % g_process_table.count;
        if (g_process_table.processes[idx].state == PROCESS_READY ||
            g_process_table.processes[idx].state == PROCESS_RUNNING) {
            next_index = idx;
            break;
        }
    }
    
    
    Process *next = &g_process_table.processes[next_index];
    next->state = PROCESS_RUNNING;
    current_index = next_index;
}


void filesystem_initialize(void) {
    g_filesystem.inode_count = 0;
    g_filesystem.root = NULL;
    
    
    Inode *root = filesystem_create_inode("/", INODE_DIR);
    g_filesystem.root = root;
}

Inode* filesystem_create_inode(const char *name, uint32_t type) {
    if (g_filesystem.inode_count >= MAX_INODES) {
        return NULL;
    }
    
    Inode *inode = &g_filesystem.inodes[g_filesystem.inode_count];
    inode->inode_number = g_filesystem.inode_count;
    inode->type = type;
    inode->size = 0;
    inode->creation_time = g_ticks;
    
    string_copy(name, inode->filename, 256);
    
    g_filesystem.inode_count++;
    return inode;
}

Inode* filesystem_find_by_path(const char *path) {
    
    if (string_compare(path, "/") == 0) {
        return g_filesystem.root;
    }
    
    for (uint32_t i = 0; i < g_filesystem.inode_count; i++) {
        if (string_compare(g_filesystem.inodes[i].filename, path) == 0) {
            return &g_filesystem.inodes[i];
        }
    }
    
    return NULL;
}


void domain_initialize(void) {
    
    Domain *sys_domain = &g_domains[0];
    sys_domain->domain_id = 0;
    sys_domain->color = 0xFF0000; 
    sys_domain->type = DOMAIN_SYSTEM;
    string_copy("sys", sys_domain->name, 64);
    sys_domain->process_count = 1;
    sys_domain->memory_limit = g_total_memory / 2; 
    
    g_domain_count = 1;
    
    
    Domain *user_domain = &g_domains[1];
    user_domain->domain_id = 1;
    user_domain->color = 0x00AA00; 
    user_domain->type = DOMAIN_USER;
    string_copy("personal", user_domain->name, 64);
    user_domain->process_count = 0;
    user_domain->memory_limit = g_total_memory / 4; 
    
    g_domain_count = 2;
}

uint32_t domain_create(const char *name, uint32_t type, uint32_t color) {
    if (g_domain_count >= MAX_DOMAINS) {
        return 0;
    }
    
    Domain *domain = &g_domains[g_domain_count];
    domain->domain_id = g_domain_count;
    domain->color = color;
    domain->type = type;
    domain->process_count = 0;
    domain->memory_limit = g_total_memory / 8;
    
    string_copy(name, domain->name, 64);
    
    g_domain_count++;
    return domain->domain_id;
}

Domain* domain_get(uint32_t domain_id) {
    if (domain_id >= MAX_DOMAINS) {
        return NULL;
    }
    return &g_domains[domain_id];
}


void string_copy(const char *src, char *dst, uint32_t max_len) {
    for (uint32_t i = 0; i < max_len - 1 && src[i] != '\0'; i++) {
        dst[i] = src[i];
    }
    dst[max_len - 1] = '\0';
}

int32_t string_compare(const char *s1, const char *s2) {
    while (*s1 && *s1 == *s2) {
        s1++;
        s2++;
    }
    return (int32_t)(*s1 - *s2);
}

uint32_t string_length(const char *str) {
    uint32_t len = 0;
    while (str[len] != '\0') {
        len++;
    }
    return len;
}

void memory_set(void *ptr, uint8_t value, uint64_t size) {
    uint8_t *p = (uint8_t *)ptr;
    for (uint64_t i = 0; i < size; i++) {
        p[i] = value;
    }
}

void memory_copy(const void *src, void *dst, uint64_t size) {
    const uint8_t *s = (const uint8_t *)src;
    uint8_t *d = (uint8_t *)dst;
    for (uint64_t i = 0; i < size; i++) {
        d[i] = s[i];
    }
}


void setup_gdt(void) {
    
}

void setup_idt(void) {
    
}

void setup_paging(void) {
    
}

void setup_interrupts(void) {
    
}

void setup_apic(void) {
    
}

void kernel_ready(void) {
    
    while (1) {
        process_schedule();
        g_ticks++;
    }
}
