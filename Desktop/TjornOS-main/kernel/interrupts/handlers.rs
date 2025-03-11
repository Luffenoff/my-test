use core::arch::asm;

#[repr(C)]
pub struct InterruptFrame {
    ip: u64,
    cs: u64,
    flags: u64,
    sp: u64,
    ss: u64,
}

#[no_mangle]
pub extern "x86-interrupt" fn keyboard_interrupt_handler(frame: InterruptFrame) {
    unsafe {
        // Чтение скан-кода клавиатуры
        let scancode = inb(0x60);
        
        // Обработка скан-кода
        handle_keyboard(scancode);
        
        // Подтверждение прерывания
        outb(0x20, 0x20);
    }
}

#[no_mangle]
pub extern "x86-interrupt" fn page_fault_handler(frame: InterruptFrame, error_code: u64) {
    let addr: u64;
    unsafe {
        asm!("mov {}, cr2", out(reg) addr);
    }
    
    panic!("ОШИБКА СТРАНИЦЫ\nАдрес: {:#x}\nКод ошибки: {:#x}", addr, error_code);
}

#[no_mangle]
pub extern "x86-interrupt" fn timer_interrupt_handler(frame: InterruptFrame) {
    unsafe {
        // Увеличение счетчика тиков
        TICKS += 1;
        
        // Планировщик
        if TICKS % QUANTUM == 0 {
            schedule();
        }
        
        // Подтверждение прерывания
        outb(0x20, 0x20);
    }
} 