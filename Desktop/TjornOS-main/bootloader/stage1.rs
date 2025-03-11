#![no_std]
#![no_main]

use core::arch::asm;

#[link_section = ".boot.data"]
static BOOT_MSG: &[u8] = b"Загрузка МояОС...";

#[no_mangle]
pub extern "C" fn _start() -> ! {
    // 1. Инициализация сегментных регистров
    unsafe {
        asm!(
            "xor ax, ax",
            "mov ds, ax",
            "mov es, ax",
            "mov ss, ax",
        );
    }

    // 2. Настройка стека
    unsafe {
        asm!(
            "mov sp, 0x7c00",
        );
    }

    // 3. Вывод сообщения о загрузке
    print_string(BOOT_MSG);

    // 4. Загрузка второй стадии загрузчика
    load_stage2();

    loop {}
}

fn print_string(msg: &[u8]) {
    for &byte in msg {
        print_char(byte);
    }
}

fn print_char(c: u8) {
    unsafe {
        asm!(
            "mov ah, 0x0e",
            "int 0x10",
            in("al") c,
        );
    }
}

fn load_stage2() {
    // Загрузка второй стадии с диска
    unsafe {
        asm!(
            "mov ah, 0x02",    // Чтение секторов
            "mov al, 0x01",    // Количество секторов
            "mov ch, 0x00",    // Цилиндр 0
            "mov cl, 0x02",    // Сектор 2
            "mov dh, 0x00",    // Головка 0
            "mov dl, 0x80",    // Жесткий диск
            "mov bx, 0x7e00",  // Адрес загрузки
            "int 0x13",        // BIOS прерывание
        );
    }
} 