section .boot
global start
bits 32

start:
    ; Установка стека
    mov esp, stack_top
    
    ; Проверка мультизагрузки
    cmp eax, 0x36d76289
    jne .no_multiboot
    
    ; Вызов основного загрузчика на Rust
    extern rust_main
    call rust_main
    
    ; Бесконечный цикл
    jmp $

.no_multiboot:
    ; Обработка ошибки
    mov dword [0xb8000], 0x4f524f45
    mov dword [0xb8004], 0x4f3a4f52
    mov dword [0xb8008], 0x4f204f20
    jmp $

section .multiboot
header_start:
    dd 0xe85250d6                ; Магическое число
    dd 0                         ; Архитектура 0 (protected mode i386)
    dd header_end - header_start ; Длина заголовка
    dd 0x100000000 - (0xe85250d6 + 0 + (header_end - header_start))
    dw 0    ; Тип
    dw 0    ; Флаги
    dd 8    ; Размер
header_end:

section .text
global _start
_start:
    ; Настройка стека
    mov esp, stack_top
    
    ; Вызов Rust-кода
    extern kernel_main
    call kernel_main
    
    ; Бесконечный цикл
    cli
.hang:
    hlt
    jmp .hang

section .bss
align 4096
stack_bottom:
    resb 16384 ; 16 КБ для стека
stack_top: 