; Operating System OS - Minimal bootloader (ELF32 format)
; This bootloader initializes the kernel

[BITS 32]

global _start
section .text

_start:
    ; Initialize stack
    mov esp, 0x90000
    
    ; Clear registers
    xor eax, eax
    xor ebx, ebx
    xor ecx, ecx
    xor edx, edx
    
    ; Return 0
    ret

; Boot signature and padding (for compatibility)
; In real bootloader, this would be a 16-bit real mode loader
; For now, we're linking as ELF32 kernel directly
