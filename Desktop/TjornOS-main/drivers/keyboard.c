#include "keyboard.h"
#include <stdint.h>

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

void keyboard_init() {
    // Инициализация контроллера клавиатуры
    while (inb(KEYBOARD_STATUS_PORT) & 2);
    outb(KEYBOARD_DATA_PORT, 0xF4);
}

uint8_t keyboard_read_scan_code() {
    if (inb(KEYBOARD_STATUS_PORT) & 1) {
        return inb(KEYBOARD_DATA_PORT);
    }
    return 0;
} 