#![no_std]
#![no_main]

use core::arch::asm;

#[no_mangle]
pub extern "C" fn stage2_main() -> ! {
    // 1. Проверка A20 линии
    enable_a20();

    // 2. Загрузка GDT
    load_gdt();

    // 3. Переход в защищенный режим
    enter_protected_mode();

    // 4. Загрузка ядра
    load_kernel();

    loop {}
}

fn enable_a20() {
    unsafe {
        // Быстрый метод через порт 0x92
        asm!(
            "in al, 0x92",
            "or al, 2",
            "out 0x92, al"
        );
    }
}

fn load_gdt() {
    // Минимальная GDT с двумя дескрипторами
    static GDT: [u64; 3] = [
        0x0000000000000000, // Нулевой дескриптор
        0x00CF9A000000FFFF, // Код
        0x00CF92000000FFFF, // Данные
    ];

    unsafe {
        asm!(
            "lgdt [{}]",
            in(reg) &GDT
        );
    }
}

fn enter_protected_mode() {
    unsafe {
        asm!(
            "mov eax, cr0",
            "or eax, 1",
            "mov cr0, eax"
        );
    }
} 