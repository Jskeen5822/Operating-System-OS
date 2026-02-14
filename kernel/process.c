#include "../include/types.h"
#include "../include/defs.h"
#include "../kernel/kernel.h"



typedef struct {
    uint32_t pid;
    ProcessControlBlock *pcb;
} ProcessDescriptor;

static ProcessDescriptor process_descriptors[MAX_PROCESSES];
static uint32_t descriptor_count = 0;

uint32_t process_fork(void) {
    if (descriptor_count >= MAX_PROCESSES) {
        return -1;
    }
    
    uint32_t new_pid = descriptor_count + 1;
    ProcessDescriptor *desc = &process_descriptors[descriptor_count++];
    desc->pid = new_pid;
    
    return new_pid;
}

uint32_t process_wait(uint32_t pid) {
    for (uint32_t i = 0; i < descriptor_count; i++) {
        if (process_descriptors[i].pid == pid) {
            
            return 0;
        }
    }
    return -1;
}

uint32_t process_exit(int status) {
    if (current_process) {
        current_process->state = PROCESS_TERMINATED;
    }
    return status;
}

void process_list(void) {
    for (uint32_t i = 0; i < descriptor_count; i++) {
        printf("PID: %d\n", process_descriptors[i].pid);
    }
}
