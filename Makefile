

CC = gcc
AS = nasm
LD = ld
CFLAGS = -m32 -ffreestanding -nostdlib -fno-pie -fno-stack-protector -O2 -Wall
ASFLAGS = -f elf32
LDFLAGS = -m elf_i386 -Ttext 0x1000 --entry=kernel_main


BUILD_DIR = build
BIN_DIR = $(BUILD_DIR)/bin


KERNEL_SOURCES = kernel/kernel.c kernel/process.c kernel/memory.c kernel/filesystem.c
KERNEL_OBJECTS = $(KERNEL_SOURCES:%.c=$(BUILD_DIR)/%.o)

SHELL_SOURCES = shell/shell.c
SHELL_OBJECTS = $(SHELL_SOURCES:%.c=$(BUILD_DIR)/%.o)

ASM_SOURCES = bootloader/boot.asm
ASM_OBJECTS = $(ASM_SOURCES:%.asm=$(BUILD_DIR)/%.o)

ALL_OBJECTS = $(KERNEL_OBJECTS) $(SHELL_OBJECTS) $(ASM_OBJECTS)


.PHONY: all clean build run

all: build

build: $(BIN_DIR)/os.bin

$(BIN_DIR)/os.bin: $(ALL_OBJECTS)
	@mkdir -p $(BIN_DIR)
	$(LD) $(LDFLAGS) -o $@ $^
	@echo "Built: $@"

$(BUILD_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -I. -c $< -o $@
	@echo "Compiled: $<"

$(BUILD_DIR)/%.o: %.asm
	@mkdir -p $(dir $@)
	$(AS) $(ASFLAGS) $< -o $@
	@echo "Assembled: $<"

clean:
	rm -rf $(BUILD_DIR)
	@echo "Clean complete"

run: build
	@echo "To run in QEMU: qemu-system-i386 -kernel $(BIN_DIR)/os.bin"

help:
	@echo "Operating System OS - Build Targets:"
	@echo "  make build   - Build the OS"
	@echo "  make clean   - Remove build artifacts"
	@echo "  make run     - Display run instructions"
	@echo "  make help    - Show this message"

.PRECIOUS: $(BUILD_DIR)/%.o
