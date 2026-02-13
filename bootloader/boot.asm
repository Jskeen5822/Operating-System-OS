; Operating System OS - Bootloader
; Simple x86 bootloader for 32-bit kernel

BITS 16
ORG 0x7C00

start:
    ; Initialize stack pointer
    mov bp, 0x9000
    mov sp, bp

    ; Display boot message
    mov si, boot_msg
    call print_string

    ; Load kernel from disk (simplified)
    ; In a real OS, this would load the kernel into memory
    mov ah, 0x02           ; Read sector function
    mov al, 1              ; Number of sectors to read
    mov ch, 0              ; Cylinder
    mov cl, 2              ; Sector
    mov dh, 0              ; Head
    mov dl, 0x80           ; Drive (0x80 = first hard disk)
    mov bx, 0x1000         ; Buffer address
    int 0x13               ; BIOS disk read interrupt

    ; Check for errors
    jc disk_error

    ; Display load success
    mov si, load_msg
    call print_string

    ; Switch to protected mode
    cli                    ; Disable interrupts
    
    ; Load GDT
    lgdt [gdt_descriptor]

    ; Set control register
    mov eax, cr0
    or eax, 0x1            ; Set protected mode bit
    mov cr0, eax

    ; Far jump to protected mode code
    jmp 0x08:protected_mode_init

disk_error:
    mov si, error_msg
    call print_string
    jmp $                  ; Halt

; Print string function
print_string:
    lodsb                  ; Load byte at ds:si
    test al, al            ; Check if null terminator
    jz .done
    mov ah, 0x0E           ; Teletype output
    mov bh, 0
    int 0x10               ; BIOS video interrupt
    jmp print_string
.done:
    ret

; Messages
boot_msg: db "Operating System OS - Booting...", 0x0D, 0x0A, 0
load_msg: db "Kernel loaded! Entering protected mode...", 0x0D, 0x0A, 0
error_msg: db "Disk read error!", 0x0D, 0x0A, 0

; GDT (Global Descriptor Table)
gdt:
    ; Null descriptor
    dq 0x0

    ; Code descriptor
    dw 0xFFFF              ; Limit
    dw 0x0                 ; Base (low)
    db 0x0                 ; Base (mid)
    db 10011010b           ; Access
    db 11001111b           ; Granularity
    db 0x0                 ; Base (high)

    ; Data descriptor
    dw 0xFFFF              ; Limit
    dw 0x0                 ; Base (low)
    db 0x0                 ; Base (mid)
    db 10010010b           ; Access
    db 11001111b           ; Granularity
    db 0x0                 ; Base (high)

gdt_descriptor:
    dw 0x17                ; Size of GDT
    dd gdt                 ; Address of GDT

BITS 32
protected_mode_init:
    ; Set up segment registers
    mov ax, 0x10           ; Data segment
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax

    ; Set up stack in protected mode
    mov esp, 0x90000

    ; Jump to kernel
    call 0x1000:0

    jmp $                  ; Halt

; Boot sector padding
times 510 - ($-start) db 0
dw 0xAA55              ; Boot signature
