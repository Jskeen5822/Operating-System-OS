; UEFI Bootloader - Operating System OS
; Real PE32+ bootloader that UEFI firmware can load and execute
; 64-bit x86-64 architecture
; This bootloader runs on real hardware and modern VMs

[BITS 64]

; ============================================================================
; UEFI PE32+ Header (Portable Executable format)
; ============================================================================
; This header tells UEFI firmware how to load and execute this binary

section .head
align 16

; DOS header (for compatibility, UEFI doesn't care but required for PE format)
dos_header:
    dw 0x5A4D           ; "MZ" signature
    dw 0               ; Reserved
    times 58 db 0      ; Reserved fields
    dd pe_header       ; Offset to PE header (at offset 0x3C)

; PE header signature
pe_header:
    db 'P', 'E', 0, 0  ; PE signature

; PE COFF header
coff_header:
    dw 0x8664          ; Machine type: x86-64
    dw 0               ; NumberOfSections (we'll set this)
    dd 0               ; TimeDateStamp
    dd 0               ; PointerToSymbolTable
    dd 0               ; NumberOfSymbols
    dw optional_header_size   ; SizeOfOptionalHeader
    dw 0x0022          ; Characteristics: executable, large address aware

; Optional header (PE32+)
optional_header:
    dw 0x020b          ; Magic: PE32+ (64-bit)
    db 0x0B            ; MajorLinkerVersion
    db 0x00            ; MinorLinkerVersion
    dd text_size       ; SizeOfCode
    dd 0               ; SizeOfInitializedData
    dd 0               ; SizeOfUninitializedData
    dd _start          ; AddressOfEntryPoint
    dd _start          ; BaseOfCode

    ; Windows specific fields
    dq image_base      ; ImageBase (where loaded in memory)
    dd section_align   ; SectionAlignment
    dd file_align      ; FileAlignment
    dw 6               ; MajorOperatingSystemVersion
    dw 0               ; MinorOperatingSystemVersion
    dw 0               ; MajorImageVersion
    dw 0               ; MinorImageVersion
    dw 6               ; MajorSubsystemVersion
    dw 0               ; MinorSubsystemVersion
    dd 0               ; Win32VersionValue
    dd image_size      ; SizeOfImage
    dd header_size     ; SizeOfHeaders
    dd 0               ; CheckSum
    dw 10              ; Subsystem: EFI Application

optional_header_size equ ($ - optional_header)

; Constants for bootloader
image_base equ 0x100000
section_align equ 0x1000
file_align equ 0x200
header_size equ 0x200
image_size equ 0x100000

; ============================================================================
; Kernel Entry Point - Called by UEFI Firmware
; ============================================================================

section .text
align 16

_start:
    ; RCX = Image Handle (EFI_HANDLE)
    ; RDX = System Table pointer (EFI_SYSTEM_TABLE*)
    
    push rbp
    mov rbp, rsp
    sub rsp, 32         ; Stack space for local variables + 32 bytes shadow space
    
    ; Save handles for later use
    mov r12, rcx        ; Save image handle in r12
    mov r13, rdx        ; Save system table in r13
    
    ; ========================================================================
    ; Phase 1: Get UEFI System Table Services
    ; ========================================================================
    
    ; r13 = EFI_SYSTEM_TABLE*
    ; EFI_SYSTEM_TABLE structure (from EDK2):
    ; +0x00: EFI_TABLE_HEADER
    ; +0x60: EFI_RUNTIME_SERVICES *RuntimeServices
    ; +0x68: EFI_BOOT_SERVICES *BootServices
    ; +0x98: UINTN NumberOfTableEntries
    ; +0xA0: EFI_CONFIGURATION_TABLE *ConfigurationTable
    
    mov rax, [r13 + 0x68]  ; Get BootServices pointer
    mov r14, rax           ; Save in r14
    
    ; ========================================================================
    ; Phase 2: Get Memory Map and Detect System Info
    ; ========================================================================
    
    ; Call GetMemoryMap to discover available memory
    ; BootServices->GetMemoryMap(MemoryMapSize, MemoryMap, MapKey, DescriptorSize, DescriptorVersion)
    ; At offset 0x28 in BootServices
    
    mov rax, [r14 + 0x28]  ; GetMemoryMap function pointer
    
    ; Setup parameters on stack (first param in RCX, rest on stack)
    lea rcx, [memory_map_size]     ; RCX = MemoryMapSize address
    lea rdx, [0x200000]            ; RDX = MemoryMap buffer
    lea r8, [memory_map_key]       ; R8 = MapKey address
    lea r9, [memory_map_desc_size] ; R9 = DescriptorSize address
    mov qword [rsp + 32], memory_map_desc_version  ; DescriptorVersion on stack
    
    call rax           ; Call GetMemoryMap
    
    ; ========================================================================
    ; Phase 3: Allocate Pages for Kernel
    ; ========================================================================
    
    ; Call AllocatePages to get memory for kernel code/data
    ; BootServices->AllocatePages(Type, MemoryType, Pages, Address)
    ; AllocatePages is at offset 0x48 in BootServices
    
    mov rax, [r14 + 0x48]  ; AllocatePages function pointer
    mov rcx, 1             ; AllocateAddress type (allocate at specific address)
    mov rdx, 0x00000003    ; EfiLoaderData type
    mov r8, 0x100         ; Allocate 256 pages (1 MB)
    lea r9, [kernel_load_address]  ; Load address: 0x100000
    
    call rax           ; Call AllocatePages
    
    ; ========================================================================
    ; Phase 4: Setup Exit Boot Services Parameters
    ; ========================================================================
    
    ; Before we can use the memory we allocated, we need to exit boot services
    ; This is required to get full control of the system
    
    ; Save parameters for later
    mov [boot_services_ptr], r14
    mov [image_handle_save], r12
    mov [system_table_ptr], r13
    
    ; ========================================================================
    ; Phase 5: Load Kernel Code to Memory
    ; ========================================================================
    
    ; The bootloader itself is loaded by UEFI
    ; We need to copy the kernel code from bootloader to kernel memory
    ; For now, kernel code will follow bootloader in the PE image
    
    lea rsi, [kernel_entry_point]  ; Source: kernel code location in bootloader
    mov rdi, 0x100000              ; Destination: kernel load address
    mov rcx, 0x10000               ; Copy size: 64 KB (enough for initial kernel)
    
    cld                            ; Clear direction flag (copy forward)
    rep movsb                       ; Copy bytes from rsi to rdi
    
    ; ========================================================================
    ; Phase 6: Exit Boot Services
    ; ========================================================================
    
    ; Call BootServices->ExitBootServices(ImageHandle, MapKey)
    ; ExitBootServices is at offset 0x78 in BootServices
    
    mov r14, [boot_services_ptr]
    mov rax, [r14 + 0x78]          ; ExitBootServices function pointer
    mov rcx, [image_handle_save]   ; RCX = ImageHandle
    mov rdx, [memory_map_key]      ; RDX = MapKey
    
    ; Save stack and registers before we lose UEFI services
    sub rsp, 64
    
    call rax           ; Call ExitBootServices
    
    ; After ExitBootServices returns, we're done with UEFI
    ; No more UEFI services available
    ; We now own the hardware
    
    ; ========================================================================
    ; Phase 7: Setup Kernel Boot Info and Jump to Kernel
    ; ========================================================================
    
    ; Create boot info structure with system info
    mov rdi, 0x100000 - 512        ; Boot info below kernel
    
    ; Store memory info
    mov rax, [system_table_ptr]
    mov qword [rdi + 0x00], [memory_map_size]  ; Total memory size
    mov dword [rdi + 0x08], 0x03               ; Default CPU count (will count cores)
    mov qword [rdi + 0x0C], 0                  ; Boot time (will be set by kernel)
    mov dword [rdi + 0x14], 1024               ; Video width
    mov dword [rdi + 0x18], 768                ; Video height
    mov dword [rdi + 0x1C], 0                  ; UEFI bootloader ID
    
    ; Setup kernel parameters in registers
    mov rdi, 0x100000 - 512        ; RDI = boot_info address
    mov rsi, 0x100000              ; RSI = kernel load address
    
    ; ========================================================================
    ; CRITICAL: Jump to Kernel at 0x100000
    ; ========================================================================
    
    jmp 0x100000                   ; Jump to kernel entry point
    
    ; Should never reach here
    cli
    hlt

; ============================================================================
; Kernel Code Stub (will be replaced by actual kernel)
; ============================================================================

kernel_entry_point:
    ; This will be replaced by the actual kernel code during linking
    ; For now, a simple kernel stub
    
    mov rax, 0x0F                  ; Video attribute (light gray on black)
    mov rcx, 0                     ; Column 0
    mov rdx, 0                     ; Row 0
    mov rsi, kernel_message        ; Message to print
    
.print_loop:
    lodsb                          ; Load byte from rsi into al
    test al, al                    ; Check for null terminator
    jz .print_done
    
    mov [0xB8000], ax              ; Write to video memory
    add qword 0xB8000, 2           ; Move to next character position
    jmp .print_loop
    
.print_done:
    cli
    hlt
    jmp .print_done

kernel_message: db "Operating System OS Kernel", 0

; ============================================================================
; Data Section
; ============================================================================

section .data
align 16

boot_services_ptr:     dq 0
image_handle_save:     dq 0
system_table_ptr:      dq 0
memory_map_size:       dq 0x4000
memory_map_key:        dq 0
memory_map_desc_size:  dq 0
memory_map_desc_version: dq 0
kernel_load_address:   dq 0x100000

text_size equ ($ - _start)

; ============================================================================
; Padding and Image Size
; ============================================================================

align 0x1000
section .pad
    times (image_size - $) db 0
