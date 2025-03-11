use core::arch::asm;

// Структура для записи в IDT
#[repr(C, packed)]
pub struct IdtEntry {
    offset_low: u16,
    segment: u16,
    flags: u16,
    offset_mid: u16,
    offset_high: u32,
    reserved: u32,
}

pub struct IDT {
    entries: [IdtEntry; 256],
}

impl IDT {
    pub fn new() -> Self {
        IDT {
            entries: [IdtEntry {
                offset_low: 0,
                segment: 0,
                flags: 0,
                offset_mid: 0,
                offset_high: 0,
                reserved: 0,
            }; 256],
        }
    }

    pub fn set_handler(&mut self, index: usize, handler: extern "x86-interrupt" fn()) {
        let addr = handler as usize;
        self.entries[index] = IdtEntry {
            offset_low: (addr & 0xFFFF) as u16,
            segment: 0x08, // Код сегмент
            flags: 0x8E00, // Присутствует, Ring 0, прерывание
            offset_mid: ((addr >> 16) & 0xFFFF) as u16,
            offset_high: (addr >> 32) as u32,
            reserved: 0,
        };
    }

    pub fn load(&self) {
        let ptr = IdtPointer {
            limit: (core::mem::size_of::<IDT>() - 1) as u16,
            base: self as *const _ as u64,
        };

        unsafe {
            asm!("lidt [{}]", in(reg) &ptr);
        }
    }
}

#[repr(C, packed)]
struct IdtPointer {
    limit: u16,
    base: u64,
} 