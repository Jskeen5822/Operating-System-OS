; Simple 64-bit Bootloader - Operating System OS
; Minimal bootloader entry point for x86-64 ELF64
; This code will be linked at 0x100000 by the linker script

bits 64

; ============================================================================
; Bootloader Entry Point
; ============================================================================

global _start
extern kernel_main

section .boot
    align 16

_start:
    ; Disable interrupts and clear flags
    cli
    cld
    
    ; Setup stack pointer below kernel code (at 0x90000)
    mov rsp, 0x90000
    
    ; Clear segment registers for clean state
    xor rax, rax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    
    ; Jump to kernel main
    jmp kernel_main
    
    ; If we return (we shouldn't), halt forever
    cli
    hlt
    jmp $ - 2
