#include "shell.h"
#include "../kernel/kernel.h"


static char command_buffer[256];
static char *command_argv[32];
static uint32_t command_argc;


typedef struct {
    const char *name;
    void (*handler)(uint32_t argc, char *argv[]);
    const char *description;
} ShellCommand;


static void cmd_help(uint32_t argc, char *argv[]);
static void cmd_ps(uint32_t argc, char *argv[]);
static void cmd_exit(uint32_t argc, char *argv[]);
static void cmd_clear(uint32_t argc, char *argv[]);
static void cmd_echo(uint32_t argc, char *argv[]);
static void cmd_ls(uint32_t argc, char *argv[]);
static void cmd_pwd(uint32_t argc, char *argv[]);
static void cmd_uptime(uint32_t argc, char *argv[]);
static void cmd_meminfo(uint32_t argc, char *argv[]);
static void cmd_mkdir(uint32_t argc, char *argv[]);
static void cmd_touch(uint32_t argc, char *argv[]);
static void cmd_exec(uint32_t argc, char *argv[]);


static ShellCommand commands[] = {
    {"help", cmd_help, "Display available commands"},
    {"ps", cmd_ps, "List running processes"},
    {"exit", cmd_exit, "Exit the shell"},
    {"clear", cmd_clear, "Clear the screen"},
    {"echo", cmd_echo, "Echo text to the screen"},
    {"ls", cmd_ls, "List directory contents"},
    {"pwd", cmd_pwd, "Print working directory"},
    {"uptime", cmd_uptime, "Display system uptime"},
    {"meminfo", cmd_meminfo, "Display memory information"},
    {"mkdir", cmd_mkdir, "Create a directory"},
    {"touch", cmd_touch, "Create an empty file"},
    {"exec", cmd_exec, "Execute a new process"},
    {NULL, NULL, NULL}
};

static char current_directory[256] = "/";
static bool shell_running = true;

void shell_start(void) {
    printf("========================================\n");
    printf("  Operating System OS Shell v1.0\n");
    printf("  Type 'help' for available commands\n");
    printf("========================================\n\n");

    while (shell_running) {
        printf("> ");
        shell_read_command();
        
        if (command_argc > 0) {
            shell_execute_command();
        }
    }
}

static void shell_read_command(void) {
    command_argc = 0;
    memset(command_buffer, 0, sizeof(command_buffer));
    
    
    
    strcpy(command_buffer, "help");
    
    
    shell_parse_command();
}

static void shell_parse_command(void) {
    command_argc = 0;
    char *token = command_buffer;
    
    
    while (*token && command_argc < 32) {
        
        while (*token && *token == ' ') token++;
        
        if (*token) {
            command_argv[command_argc++] = token;
            
            
            while (*token && *token != ' ') token++;
            
            if (*token) {
                *token++ = '\0';
            }
        }
    }
}

static void shell_execute_command(void) {
    const char *cmd_name = command_argv[0];
    
    
    for (uint32_t i = 0; commands[i].name != NULL; i++) {
        if (strcmp(commands[i].name, cmd_name) == 0) {
            commands[i].handler(command_argc, command_argv);
            return;
        }
    }
    
    printf("Unknown command: %s\n", cmd_name);
}


static void cmd_help(uint32_t argc, char *argv[]) {
    printf("\nAvailable Commands:\n");
    printf("------------------\n");
    
    for (uint32_t i = 0; commands[i].name != NULL; i++) {
        printf("  %-12s - %s\n", commands[i].name, commands[i].description);
    }
    printf("\n");
}

static void cmd_ps(uint32_t argc, char *argv[]) {
    printf("\nRunning Processes:\n");
    printf("------------------\n");
    printf("PID\tName\t\tState\tPriority\n");
    printf("---\t----\t\t-----\t--------\n");
    
    extern ProcessControlBlock process_table[];
    extern uint32_t process_count;
    
    for (uint32_t i = 0; i < process_count; i++) {
        const char *state_str = "UNKNOWN";
        switch (process_table[i].state) {
            case PROCESS_READY: state_str = "READY"; break;
            case PROCESS_RUNNING: state_str = "RUNNING"; break;
            case PROCESS_WAITING: state_str = "WAITING"; break;
            case PROCESS_BLOCKED: state_str = "BLOCKED"; break;
            case PROCESS_TERMINATED: state_str = "TERM"; break;
        }
        
        printf("%d\t%-15s\t%-6s\t%d\n", 
               process_table[i].pid, 
               process_table[i].name,
               state_str,
               process_table[i].priority);
    }
    printf("\n");
}

static void cmd_exit(uint32_t argc, char *argv[]) {
    shell_running = false;
    printf("Exiting shell...\n");
}

static void cmd_clear(uint32_t argc, char *argv[]) {
    
    printf("\n\n\n\n\n\n\n\n\n\n");
}

static void cmd_echo(uint32_t argc, char *argv[]) {
    for (uint32_t i = 1; i < argc; i++) {
        printf("%s ", argv[i]);
    }
    printf("\n");
}

static void cmd_ls(uint32_t argc, char *argv[]) {
    printf("\nDirectory: %s\n", current_directory);
    printf("Files:\n");
    printf("  .\n");
    printf("  ..\n");
    printf("  system.bin\n");
    printf("  kernel.bin\n");
    printf("  shell.bin\n");
    printf("\n");
}

static void cmd_pwd(uint32_t argc, char *argv[]) {
    printf("%s\n", current_directory);
}

static void cmd_uptime(uint32_t argc, char *argv[]) {
    extern uint64_t system_ticks;
    uint64_t seconds = system_ticks / 100;  
    uint64_t minutes = seconds / 60;
    uint64_t hours = minutes / 60;
    
    printf("System uptime: %lld hours, %lld minutes, %lld seconds\n", 
           hours, minutes % 60, seconds % 60);
}

static void cmd_meminfo(uint32_t argc, char *argv[]) {
    printf("\nMemory Information:\n");
    printf("-------------------\n");
    printf("Total Memory: %d KB\n", MAX_PAGES * PAGE_SIZE / 1024);
    printf("Kernel Space: 256 pages\n");
    printf("Available: %d pages\n", MAX_PAGES - 256);
    printf("Page Size: %d bytes\n\n", PAGE_SIZE);
}

static void cmd_mkdir(uint32_t argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: mkdir <directory_name>\n");
        return;
    }
    printf("Created directory: %s\n", argv[1]);
}

static void cmd_touch(uint32_t argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: touch <filename>\n");
        return;
    }
    printf("Created file: %s\n", argv[1]);
}

static void cmd_exec(uint32_t argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: exec <process_name> [priority]\n");
        return;
    }
    
    extern void process_create(const char *name, uint32_t priority);
    uint32_t priority = (argc > 2) ? 1 : 0;
    process_create(argv[1], priority);
}
