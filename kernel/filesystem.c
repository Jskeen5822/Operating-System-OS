#include "../include/types.h"
#include "../include/defs.h"

/* File system implementation */

#define FILE_BLOCK_SIZE 4096
#define MAX_INODES 512

typedef struct {
    uint32_t total_blocks;
    uint32_t free_blocks;
    uint32_t total_inodes;
    uint32_t free_inodes;
    uint32_t block_size;
} Superblock;

static Superblock superblock = {0};
static Inode inode_table[MAX_INODES] = {0};
static uint8_t block_bitmap[MAX_BLOCKS / 8] = {0};
static uint8_t inode_bitmap[MAX_INODES / 8] = {0};

void filesystem_init(void) {
    /* Initialize superblock */
    superblock.total_blocks = MAX_BLOCKS;
    superblock.free_blocks = MAX_BLOCKS - 1;
    superblock.total_inodes = MAX_INODES;
    superblock.free_inodes = MAX_INODES - 1;
    superblock.block_size = FILE_BLOCK_SIZE;
    
    /* Initialize root directory inode */
    inode_table[0].inode_number = 0;
    inode_table[0].file_type = 1;  /* Directory */
    inode_table[0].size = 0;
    inode_table[0].permissions = 0755;
    inode_table[0].hard_link_count = 1;
    inode_bitmap[0] |= 1;  /* Mark root as allocated */
}

uint32_t filesystem_create_file(const char *filename, uint32_t permissions) {
    /* Find free inode */
    uint32_t inode_num = 0;
    for (uint32_t i = 1; i < MAX_INODES; i++) {
        uint32_t byte_idx = i / 8;
        uint32_t bit_idx = i % 8;
        
        if ((inode_bitmap[byte_idx] & (1 << bit_idx)) == 0) {
            inode_num = i;
            inode_bitmap[byte_idx] |= (1 << bit_idx);
            break;
        }
    }
    
    if (inode_num == 0) {
        return -1;  /* No free inodes */
    }
    
    /* Initialize inode */
    inode_table[inode_num].inode_number = inode_num;
    inode_table[inode_num].file_type = 0;  /* Regular file */
    inode_table[inode_num].size = 0;
    inode_table[inode_num].permissions = permissions;
    inode_table[inode_num].hard_link_count = 1;
    
    return inode_num;
}

uint32_t filesystem_create_directory(const char *dirname, uint32_t permissions) {
    /* Find free inode */
    uint32_t inode_num = 0;
    for (uint32_t i = 1; i < MAX_INODES; i++) {
        uint32_t byte_idx = i / 8;
        uint32_t bit_idx = i % 8;
        
        if ((inode_bitmap[byte_idx] & (1 << bit_idx)) == 0) {
            inode_num = i;
            inode_bitmap[byte_idx] |= (1 << bit_idx);
            break;
        }
    }
    
    if (inode_num == 0) {
        return -1;  /* No free inodes */
    }
    
    /* Initialize directory inode */
    inode_table[inode_num].inode_number = inode_num;
    inode_table[inode_num].file_type = 1;  /* Directory */
    inode_table[inode_num].size = 0;
    inode_table[inode_num].permissions = permissions;
    inode_table[inode_num].hard_link_count = 2;  /* . and .. */
    
    return inode_num;
}

uint32_t filesystem_allocate_block(void) {
    for (uint32_t i = 0; i < MAX_BLOCKS; i++) {
        uint32_t byte_idx = i / 8;
        uint32_t bit_idx = i % 8;
        
        if ((block_bitmap[byte_idx] & (1 << bit_idx)) == 0) {
            block_bitmap[byte_idx] |= (1 << bit_idx);
            superblock.free_blocks--;
            return i;
        }
    }
    
    return -1;  /* No free blocks */
}

void filesystem_free_block(uint32_t block_num) {
    uint32_t byte_idx = block_num / 8;
    uint32_t bit_idx = block_num % 8;
    
    block_bitmap[byte_idx] &= ~(1 << bit_idx);
    superblock.free_blocks++;
}

void filesystem_print_stats(void) {
    printf("File System Statistics:\n");
    printf("Total blocks: %d\n", superblock.total_blocks);
    printf("Free blocks: %d\n", superblock.free_blocks);
    printf("Total inodes: %d\n", superblock.total_inodes);
    printf("Free inodes: %d\n", superblock.free_inodes);
    printf("Block size: %d bytes\n", superblock.block_size);
}

uint32_t filesystem_list_directory(uint32_t inode_num) {
    if (inode_num >= MAX_INODES) {
        return -1;
    }
    
    Inode *dir = &inode_table[inode_num];
    if (dir->file_type != 1) {  /* Not a directory */
        return -1;
    }
    
    return dir->size;  /* Number of entries */
}

uint32_t filesystem_get_file_info(uint32_t inode_num, Inode *out) {
    if (inode_num >= MAX_INODES) {
        return -1;
    }
    
    *out = inode_table[inode_num];
    return 0;
}
