#!/bin/bash
set -e

echo "Creating bootable TjornOS image..."

# Создаем директории
mkdir -p build/iso/boot/grub

# Копируем ядро
cp target/x86_64-unknown-none/release/tjornos build/iso/boot/kernel.bin

# Создаем конфиг GRUB
cat > build/iso/boot/grub/grub.cfg << EOF
set timeout=0
set default=0

menuentry "TjornOS" {
    multiboot /boot/kernel.bin
    boot
}
EOF

# Создаем ISO образ
grub-mkrescue -o target/x86_64-unknown-none/release/tjornos.iso build/iso

echo "Bootable image created successfully" 