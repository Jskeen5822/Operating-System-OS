/* Linker script for 64-bit Operating System OS kernel */

ENTRY(_start)

SECTIONS {
    . = 0x100000;
    
    .boot : AT(0x100000) {
        *(.boot)
    }
    
    .text : AT(0x101000) {
        *(.text)
        *(.text.*)
        *(.rodata)
        *(.rodata.*)
    }
    
    .data : {
        *(.data)
        *(.data.*)
        *(.bss)
        *(.bss.*)
        *(COMMON)
    }
    
    /DISCARD/ : {
        *(.note.GNU-stack)
        *(.gnu_debuglink)
        *(.gnu.lto_*)
    }
}
