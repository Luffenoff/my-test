#![no_std]
#![no_main]

mod vga_buffer;
mod memory { include!("memory/memory.rs"); }
mod interrupts;

use memory::MemoryManager;
use interrupts::IDT;

#[no_mangle]
pub extern "C" fn kernel_main() {
    // Инициализация базовых систем
    vga_buffer::init();
    println!("Ядро загружено успешно!");
    
    // Инициализация подсистем
    let memory_manager = init_memory();
    init_interrupts();
    
    // Настройка планировщика задач
    init_scheduler();
    
    // Запуск системных сервисов
    start_system_services();
}

fn init_memory() -> MemoryManager {
    let mut manager = MemoryManager::new();
    manager.init_paging();
    manager.setup_heap();
    manager
}

fn init_interrupts() {
    let mut idt = IDT::new();
    idt.setup_handlers();
    idt.load();
}

fn init_scheduler() {
    // Инициализация планировщика задач
}

fn start_system_services() {
    // Запуск базовых сервисов
} 