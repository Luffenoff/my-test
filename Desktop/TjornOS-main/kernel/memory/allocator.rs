use core::alloc::{GlobalAlloc, Layout};
use spin::Mutex;

pub struct KernelAllocator {
    heap: Mutex<Heap>,
}

impl KernelAllocator {
    pub const fn new() -> Self {
        KernelAllocator {
            heap: Mutex::new(Heap::new()),
        }
    }
}

unsafe impl GlobalAlloc for KernelAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let mut heap = self.heap.lock();
        
        let addr = heap.allocate(layout)
            .ok()
            .map_or(0 as *mut u8, |addr| addr as *mut u8);
            
        addr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        let mut heap = self.heap.lock();
        heap.deallocate(ptr as usize, layout);
    }
}

struct Heap {
    start: usize,
    size: usize,
    used: usize,
    first_free: Option<&'static mut FreeBlock>,
}

struct FreeBlock {
    size: usize,
    next: Option<&'static mut FreeBlock>,
} 