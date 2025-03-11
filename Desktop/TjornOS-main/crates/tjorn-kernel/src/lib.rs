#![no_std]
#![no_main]

pub mod device;
pub mod fs;
pub mod memory;
pub mod process;
pub mod scheduler;
pub mod syscall;

pub use memory::MemoryManager;
pub use process::ProcessManager;
pub use scheduler::Scheduler;

pub fn init() {
    // Инициализация ядра
}
