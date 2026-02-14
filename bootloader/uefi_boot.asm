



bits 64





global _start
extern kernel_main

section .boot
    align 16

_start:
    
    cli
    cld
    
    
    mov rsp, 0x90000
    
    
    xor rax, rax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    
    
    jmp kernel_main
    
    
    cli
    hlt
    jmp $ - 2
