#include "../include/types.h"
#include "../include/defs.h"



#define MEMORY_BLOCKS (MAX_PAGES / 8)
static uint8_t memory_bitmap[MEMORY_BLOCKS] = {0};

uint32_t memory_allocate(uint32_t size) {
    uint32_t pages_needed = (size + PAGE_SIZE - 1) / PAGE_SIZE;
    uint32_t pages_found = 0;
    uint32_t start_page = 0;
    
    
    for (uint32_t i = 256; i < MAX_PAGES; i++) {
        uint32_t byte_idx = i / 8;
        uint32_t bit_idx = i % 8;
        
        if ((memory_bitmap[byte_idx] & (1 << bit_idx)) == 0) {
            if (pages_found == 0) {
                start_page = i;
            }
            pages_found++;
            
            if (pages_found == pages_needed) {
                
                for (uint32_t j = 0; j < pages_needed; j++) {
                    uint32_t page = start_page + j;
                    uint32_t b_idx = page / 8;
                    uint32_t bit = page % 8;
                    memory_bitmap[b_idx] |= (1 << bit);
                }
                return start_page * PAGE_SIZE;
            }
        } else {
            pages_found = 0;
        }
    }
    
    return 0;  
}

void memory_free(uint32_t address, uint32_t size) {
    uint32_t page = address / PAGE_SIZE;
    uint32_t pages_needed = (size + PAGE_SIZE - 1) / PAGE_SIZE;
    
    for (uint32_t i = 0; i < pages_needed; i++) {
        uint32_t p = page + i;
        if (p < MAX_PAGES) {
            uint32_t byte_idx = p / 8;
            uint32_t bit_idx = p % 8;
            memory_bitmap[byte_idx] &= ~(1 << bit_idx);
        }
    }
}

uint32_t memory_get_free_pages(void) {
    uint32_t free_pages = 0;
    
    for (uint32_t i = 0; i < MEMORY_BLOCKS; i++) {
        for (uint32_t j = 0; j < 8; j++) {
            if ((memory_bitmap[i] & (1 << j)) == 0) {
                free_pages++;
            }
        }
    }
    
    return free_pages;
}

uint32_t memory_get_total_free(void) {
    return memory_get_free_pages() * PAGE_SIZE;
}

void memory_print_stats(void) {
    uint32_t free_pages = memory_get_free_pages();
    uint32_t total_free = memory_get_total_free();
    uint32_t used_pages = MAX_PAGES - free_pages;
    
    printf("Memory Statistics:\n");
    printf("Total: %d KB (%d pages)\n", MAX_PAGES * PAGE_SIZE / 1024, MAX_PAGES);
    printf("Used: %d KB (%d pages)\n", used_pages * PAGE_SIZE / 1024, used_pages);
    printf("Free: %d KB (%d pages)\n", total_free / 1024, free_pages);
}
