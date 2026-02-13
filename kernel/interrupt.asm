; Interrupt handlers for Operating System OS
; Simplified handlers for ELF32 compilation

[BITS 32]

global interrupt_handler
global timer_interrupt
global keyboard_interrupt

section .text

; Generic interrupt handler
interrupt_handler:
    ; Return immediately (placeholder)
    ret

; Timer interrupt (IRQ 0)
timer_interrupt:
    ; Return immediately (placeholder)
    ret

; Keyboard interrupt (IRQ 1)
keyboard_interrupt:
    ; Return immediately (placeholder)
    ret
