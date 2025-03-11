#![no_std]
#![no_main]

use core::panic::PanicInfo;
use crate::memory::MemoryMap;
use crate::hardware::ACPI;

// Константы для VGA-буфера
const VGA_BUFFER: *mut u8 = 0xb8000 as *mut u8;
const VGA_WIDTH: usize = 80;
const VGA_HEIGHT: usize = 25;

// Цвета текста
const COLOR_WHITE: u8 = 0x0F;

#[repr(C, packed)]
pub struct BootInfo {
    memory_map: MemoryMap,
    acpi_tables: ACPI,
    framebuffer: FramebufferInfo,
    kernel_base: u64,
}

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    print_string("ПАНИКА: Загрузчик остановлен");
    loop {}
}

#[no_mangle]
pub extern "C" fn bootloader_main() -> ! {
    // Инициализация базового оборудования
    init_cpu();
    init_memory_map();
    
    // Загрузка ядра
    let kernel_binary = load_kernel()?;
    verify_kernel_signature(&kernel_binary)?;
    
    // Подготовка окружения
    let boot_info = prepare_boot_info();
    
    // Переход к ядру
    jump_to_kernel(kernel_binary, boot_info);
    
    loop {}
}

fn init_cpu() {
    // Проверка поддержки необходимых функций CPU
    check_cpu_features();
    
    // Настройка защищенного режима
    enable_protected_mode();
    
    // Настройка длинного режима
    enable_long_mode();
}

fn clear_screen() {
    for i in 0..VGA_HEIGHT * VGA_WIDTH * 2 {
        unsafe {
            *VGA_BUFFER.offset(i) = 0;
        }
    }
}

fn print_string(s: &str) {
    let mut offset = 0;
    for byte in s.bytes() {
        unsafe {
            *VGA_BUFFER.offset(offset) = byte;
            *VGA_BUFFER.offset(offset + 1) = COLOR_WHITE;
        }
        offset += 2;
    }
}

fn check_a20() {
    // Проверка включения A20 линии
    // Это позволит использовать память выше 1 МБ
}

fn load_gdt() {
    // Загрузка таблицы глобальных дескрипторов
    // Необходима для защищенного режима
}

fn jump_to_kernel(kernel_binary: &[u8], boot_info: BootInfo) {
    // Переход к точке входа ядра
} 