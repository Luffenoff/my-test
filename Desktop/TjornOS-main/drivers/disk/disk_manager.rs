use core::ptr;
use crate::system::devices::DiskError;

#[repr(C)]
pub struct AtaDisk {
    sectors: u64,
    sector_size: u32,
}

impl AtaDisk {
    pub fn new() -> Self {
        // Инициализация диска
        AtaDisk {
            sectors: 0,
            sector_size: 512,
        }
    }

    pub fn read_sector(&self, lba: u32, buffer: &mut [u8]) -> Result<(), DiskError> {
        if buffer.len() != self.sector_size as usize {
            return Err(DiskError::InvalidBufferSize);
        }

        unsafe {
            extern "C" {
                fn ata_read_sectors(lba: u32, count: u8, buffer: *mut u8);
            }
            ata_read_sectors(lba, 1, buffer.as_mut_ptr());
        }
        Ok(())
    }
} 