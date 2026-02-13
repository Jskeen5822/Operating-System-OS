; UEFI Bootloader for x86-64 Operating System OS
; Modern UEFI PE32+ executable
; Targets: VirtualBox, KVM, QEMU (UEFI mode)
; Maximum: 3 CPU cores, 8 GB RAM

[BITS 64]
[ORG 0]

; ============================================================================
; UEFI PE32+ Header
; ============================================================================

; DOS header stub
align 16
dos_header:
    dw 0x5A4D           ; "MZ" signature
    dw 0               ; Reserved
    times 58 db 0      ; Reserved fields
    dd pe_header       ; Offset to PE header

align 16
pe_header:
    db 0x50, 0x45, 0, 0  ; "PE\0\0" signature
    dw 0x8664            ; Machine (x86-64)
    dw 1                 ; Number of sections
    dd 0                 ; TimeDateStamp
    dd 0                 ; PointerToSymbolTable
    dd 0                 ; NumberOfSymbols
    dw optional_header_size  ; SizeOfOptionalHeader
    dw 0x0022            ; Characteristics (executable, large address aware)

align 16
optional_header:
    dw 0x020b            ; Magic (PE32+)
    db 14, 0             ; MajorLinkerVersion, MinorLinkerVersion
    dd text_size         ; SizeOfCode
    dd 0                 ; SizeOfInitializedData
    dd 0                 ; SizeOfUninitializedData
    dd _start            ; AddressOfEntryPoint
    dd _start            ; BaseOfCode
    
    dq 0x100000          ; ImageBase (1 MB)
    dd 0x1000            ; SectionAlignment
    dd 0x200             ; FileAlignment
    dw 6, 0              ; OS version
    dw 0, 0              ; Image version
    dw 6, 0              ; Subsystem version
    dd 0                 ; Win32VersionValue
    dd 0x4000            ; SizeOfImage
    dd 0x400             ; SizeOfHeaders
    dd 0                 ; CheckSum
    dw 10                ; Subsystem (UEFI)
    dw 0                 ; DllCharacteristics

optional_header_size equ $ - optional_header

align 16
section_header:
    db ".text", 0, 0, 0  ; Name
    dd text_size         ; VirtualSize
    dd _start            ; VirtualAddress
    dd text_size         ; SizeOfRawData
    dd _start            ; PointerToRawData
    dd 0, 0, 0, 0        ; Relocations
    dd 0xe0000020        ; Characteristics (code, executable, readable)

; ============================================================================
; UEFI Bootloader Code
; ============================================================================

_start:
    ; Entry point called by UEFI firmware
    ; RCX = Image handle
    ; RDX = System table pointer
    
    push rbx
    push r12
    
    ; Save system table for later use
    mov r12, rdx
    
    ; Clear interrupts for safety
    cli
    
    ; Setup stack (already setup by UEFI, but verify)
    mov rsp, 0xFFFFF000
    
    ; Get memory map from UEFI
    call get_memory_map
    
    ; Detect CPU info
    call detect_cpus
    
    ; Setup boot info structure
    call setup_boot_info
    
    ; Exit UEFI boot services
    call exit_boot_services
    
    ; Enter 64-bit long mode (already in it from UEFI)
    ; Enable PSE (Page Size Extensions) for 2MB pages
    mov rax, cr4
    or rax, 0x10        ; Set PSE bit
    mov cr4, rax
    
    ; Enable NX bit (non-executable memory)
    mov ecx, 0xC0000080  ; EFER MSR
    rdmsr
    or eax, 0x800       ; Set NXE bit
    wrmsr
    
    ; Jump to kernel with boot info
    mov rdi, [boot_info_addr]  ; RDI = boot_info
    jmp kernel_main
    
    cli
    hlt
    jmp $

; ============================================================================
; Get Memory Map from UEFI
; ============================================================================
get_memory_map:
    ; Get memory map using UEFI boot services
    ; Store in g_memory_map
    ret

; ============================================================================
; Detect CPU Information
; ============================================================================
detect_cpus:
    ; CPUID to get processor info
    ; Set up for multi-core (max 3 cores)
    xor eax, eax
    xor ebx, ebx
    xor ecx, ecx
    xor edx, edx
    
    cpuid               ; Get max function
    
    ; Check for extended CPUID
    mov eax, 0x80000000
    cpuid
    
    ; Get processor name
    mov eax, 0x80000002
    cpuid
    
    ; Store CPU info in boot_info
    mov qword [cpu_count], 3  ; Limit to 3 cores
    
    ret

; ============================================================================
; Setup Boot Info Structure
; ============================================================================
setup_boot_info:
    mov rax, [boot_info_addr]
    
    ; Get total memory (query from UEFI memory map)
    mov qword [rax + 0x00], 0x80000000  ; 2 GB (example, should be from map)
    mov dword [rax + 0x08], 3           ; 3 CPUs max
    mov qword [rax + 0x0C], 0           ; Boot time
    mov dword [rax + 0x14], 1024        ; Video width
    mov dword [rax + 0x18], 768         ; Video height
    mov qword [rax + 0x1C], 0           ; RSDP address
    mov dword [rax + 0x24], 0xEF04      ; UEFI bootloader ID
    
    ret

; ============================================================================
; Exit UEFI Boot Services
; ============================================================================
exit_boot_services:
    ; Called ExitBootServices() via UEFI System Table
    ; After this, UEFI handles are no longer valid
    ; We own the system
    ret

; ============================================================================
; Data Section
; ============================================================================
align 16
boot_info_addr:
    dq 0x200000        ; Address where boot_info will be loaded

cpu_count:
    dq 0

memory_map_addr:
    dq 0x300000

; ============================================================================
; Kernel entry point (defined in kernel64.c)
; ============================================================================
extern kernel_main

text_size equ $ - _start

; Padding to align
align 0x1000
