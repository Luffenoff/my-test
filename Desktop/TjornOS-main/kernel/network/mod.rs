use alloc::vec::Vec;
use spin::Mutex;
use crate::security::Encryption;

pub struct NetworkStack {
    interfaces: Vec<NetworkInterface>,
    firewall: Firewall,
    encryption: Encryption,
    connection_pool: Mutex<ConnectionPool>,
}

#[derive(Clone)]
pub struct Packet {
    header: PacketHeader,
    payload: Vec<u8>,
    signature: [u8; 32], // SHA-256 подпись
}

struct PacketHeader {
    version: u8,
    source: [u8; 16],      // IPv6 адрес
    destination: [u8; 16], // IPv6 адрес
    protocol: Protocol,
    flags: PacketFlags,
}

impl NetworkStack {
    pub fn new() -> Self {
        NetworkStack {
            interfaces: Vec::new(),
            firewall: Firewall::new(),
            encryption: Encryption::new(),
            connection_pool: Mutex::new(ConnectionPool::new()),
        }
    }

    pub fn send_packet(&self, packet: Packet) -> Result<(), NetError> {
        // Проверка пакета файрволом
        self.firewall.check_packet(&packet)?;
        
        // Шифрование данных
        let encrypted = self.encryption.encrypt_packet(packet)?;
        
        // Отправка через сетевой интерфейс
        if let Some(interface) = self.get_best_interface() {
            interface.send(encrypted)
        } else {
            Err(NetError::NoInterface)
        }
    }

    pub fn receive_packet(&self) -> Result<Packet, NetError> {
        let raw_packet = self.await_packet()?;
        
        // Проверка целостности
        if !self.verify_packet_integrity(&raw_packet) {
            return Err(NetError::InvalidPacket);
        }
        
        // Расшифровка
        let decrypted = self.encryption.decrypt_packet(raw_packet)?;
        
        // Проверка файрволом
        self.firewall.check_packet(&decrypted)?;
        
        Ok(decrypted)
    }
} 