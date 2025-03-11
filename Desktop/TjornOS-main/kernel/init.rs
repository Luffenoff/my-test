use crate::memory::MemoryManager;
use crate::interrupts::IDT;

pub fn kernel_init() {
    // 1. Инициализация базовых подсистем
    init_serial();
    init_vga();
    
    // 2. Настройка прерываний
    let idt = IDT::new();
    idt.install();
    
    // 3. Инициализация памяти
    let mut mm = MemoryManager::new();
    mm.init();
    
    // 4. Настройка планировщика
    init_scheduler();
    
    println!("Ядро инициализировано успешно!");
}

fn init_serial() {
    // Инициализация последовательного порта для отладки
    const COM1: u16 = 0x3F8;
    unsafe {
        // Настройка COM1
        outb(COM1 + 1, 0x00); // Отключить прерывания
        outb(COM1 + 3, 0x80); // Включить DLAB
        outb(COM1 + 0, 0x03); // Делитель = 3 (38400 бод)
        outb(COM1 + 1, 0x00); // Старший байт делителя
        outb(COM1 + 3, 0x03); // 8 бит, без четности, 1 стоп-бит
        outb(COM1 + 2, 0xC7); // FIFO, очистка, 14-байтовый порог
    }
}

fn init_vga() {
    // Инициализация текстового режима VGA
    let vga_buffer = 0xB8000 as *mut u8;
    unsafe {
        for i in 0..(80 * 25 * 2) {
            *vga_buffer.offset(i) = 0;
        }
    }
} 