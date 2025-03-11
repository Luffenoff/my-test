use core::ptr::NonNull;

const PAGE_SIZE: usize = 4096;

pub struct PageTable {
    entries: [PageTableEntry; 512],
}

#[repr(transparent)]
pub struct PageTableEntry(u64);

impl PageTableEntry {
    pub fn set_addr(&mut self, addr: u64, flags: PageTableFlags) {
        self.0 = (addr & 0x000fffff_fffff000) | flags.bits();
    }

    pub fn addr(&self) -> u64 {
        self.0 & 0x000fffff_fffff000
    }

    pub fn flags(&self) -> PageTableFlags {
        PageTableFlags::from_bits_truncate(self.0)
    }
}

bitflags! {
    pub struct PageTableFlags: u64 {
        const PRESENT = 1;
        const WRITABLE = 1 << 1;
        const USER_ACCESSIBLE = 1 << 2;
        const WRITE_THROUGH = 1 << 3;
        const NO_CACHE = 1 << 4;
        const HUGE_PAGE = 1 << 7;
    }
}

pub struct MemoryMapper {
    p4: &'static mut PageTable,
    frames: FrameAllocator,
}

impl MemoryMapper {
    pub fn new() -> Self {
        let p4_ptr = 0xffff_ffff_ffff_f000 as *mut PageTable;
        MemoryMapper {
            p4: unsafe { &mut *p4_ptr },
            frames: FrameAllocator::new(),
        }
    }

    pub fn map(&mut self, page: Page, flags: PageTableFlags) -> Result<(), &'static str> {
        let frame = self.frames.allocate()
            .ok_or("нет свободных фреймов")?;
        
        let p3 = self.p4.next_table_create(page.p4_index())?;
        let p2 = p3.next_table_create(page.p3_index())?;
        let p1 = p2.next_table_create(page.p2_index())?;
        
        p1[page.p1_index()].set_addr(frame.start_address(), flags);
        Ok(())
    }
} 