




[BITS 64]
[ORG 0]






align 16
dos_header:
    dw 0x5A4D           
    dw 0               
    times 58 db 0      
    dd pe_header       

align 16
pe_header:
    db 0x50, 0x45, 0, 0  
    dw 0x8664            
    dw 1                 
    dd 0                 
    dd 0                 
    dd 0                 
    dw optional_header_size  
    dw 0x0022            

align 16
optional_header:
    dw 0x020b            
    db 14, 0             
    dd text_size         
    dd 0                 
    dd 0                 
    dd _start            
    dd _start            
    
    dq 0x100000          
    dd 0x1000            
    dd 0x200             
    dw 6, 0              
    dw 0, 0              
    dw 6, 0              
    dd 0                 
    dd 0x4000            
    dd 0x400             
    dd 0                 
    dw 10                
    dw 0                 

optional_header_size equ $ - optional_header

align 16
section_header:
    db ".text", 0, 0, 0  
    dd text_size         
    dd _start            
    dd text_size         
    dd _start            
    dd 0, 0, 0, 0        
    dd 0xe0000020        





_start:
    
    
    
    
    push rbx
    push r12
    
    
    mov r12, rdx
    
    
    cli
    
    
    mov rsp, 0xFFFFF000
    
    
    call get_memory_map
    
    
    call detect_cpus
    
    
    call setup_boot_info
    
    
    call exit_boot_services
    
    
    
    mov rax, cr4
    or rax, 0x10        
    mov cr4, rax
    
    
    mov ecx, 0xC0000080  
    rdmsr
    or eax, 0x800       
    wrmsr
    
    
    mov rdi, [boot_info_addr]  
    jmp kernel_main
    
    cli
    hlt
    jmp $




get_memory_map:
    
    
    ret




detect_cpus:
    
    
    xor eax, eax
    xor ebx, ebx
    xor ecx, ecx
    xor edx, edx
    
    cpuid               
    
    
    mov eax, 0x80000000
    cpuid
    
    
    mov eax, 0x80000002
    cpuid
    
    
    mov qword [cpu_count], 3  
    
    ret




setup_boot_info:
    mov rax, [boot_info_addr]
    
    
    mov qword [rax + 0x00], 0x80000000  
    mov dword [rax + 0x08], 3           
    mov qword [rax + 0x0C], 0           
    mov dword [rax + 0x14], 1024        
    mov dword [rax + 0x18], 768         
    mov qword [rax + 0x1C], 0           
    mov dword [rax + 0x24], 0xEF04      
    
    ret




exit_boot_services:
    
    
    
    ret




align 16
boot_info_addr:
    dq 0x200000        

cpu_count:
    dq 0

memory_map_addr:
    dq 0x300000




extern kernel_main

text_size equ $ - _start


align 0x1000
