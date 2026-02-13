; Interrupt handlers for Operating System OS

BITS 32

global interrupt_handler
global timer_interrupt
global keyboard_interrupt

extern interrupt_handler_c

; Generic interrupt handler
interrupt_handler:
    pusha
    mov eax, [esp + 32]
    call interrupt_handler_c
    popa
    add esp, 4
    iret

; Timer interrupt (IRQ 0)
timer_interrupt:
    pusha
    mov eax, 0
    call interrupt_handler_c
    mov al, 0x20
    out 0x20, al            ; Send EOI to PIC
    popa
    iret

; Keyboard interrupt (IRQ 1)
keyboard_interrupt:
    pusha
    mov eax, 1
    call interrupt_handler_c
    mov al, 0x20
    out 0x20, al            ; Send EOI to PIC
    popa
    iret

; Syscall handler
syscall_handler:
    pusha
    mov eax, [esp + 32]
    call syscall_dispatcher
    popa
    iret
