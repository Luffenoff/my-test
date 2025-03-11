#include <stdint.h>

// Порты IDE контроллера
#define ATA_DATA        0x1F0
#define ATA_FEATURES    0x1F1
#define ATA_SECTOR_CNT  0x1F2
#define ATA_LBA_LOW     0x1F3
#define ATA_LBA_MID     0x1F4
#define ATA_LBA_HIGH    0x1F5
#define ATA_DRIVE       0x1F6
#define ATA_COMMAND     0x1F7
#define ATA_STATUS      0x1F7

// Команды ATA
#define ATA_CMD_READ  0x20
#define ATA_CMD_WRITE 0x30

void ata_read_sectors(uint32_t lba, uint8_t sector_count, void* buffer) {
    // Выбор главного диска
    outb(ATA_DRIVE, 0xE0 | ((lba >> 24) & 0x0F));
    
    // Отправка параметров
    outb(ATA_SECTOR_CNT, sector_count);
    outb(ATA_LBA_LOW, lba & 0xFF);
    outb(ATA_LBA_MID, (lba >> 8) & 0xFF);
    outb(ATA_LBA_HIGH, (lba >> 16) & 0xFF);
    
    // Команда чтения
    outb(ATA_COMMAND, ATA_CMD_READ);
    
    // Чтение данных
    uint16_t* buf = (uint16_t*)buffer;
    for(int i = 0; i < sector_count * 256; i++) {
        // Ожидание готовности данных
        while(!(inb(ATA_STATUS) & 0x08));
        buf[i] = inw(ATA_DATA);
    }
} 