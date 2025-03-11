use aes_gcm::{Aes256Gcm, Key, Nonce};
use rand_core::OsRng;

pub struct Encryption {
    keys: KeyManager,
    rng: OsRng,
}

struct KeyManager {
    current_key: Key<Aes256Gcm>,
    previous_keys: Vec<Key<Aes256Gcm>>,
    rotation_interval: Duration,
    last_rotation: Instant,
}

impl Encryption {
    pub fn new() -> Self {
        Encryption {
            keys: KeyManager::new(),
            rng: OsRng,
        }
    }

    pub fn encrypt_packet(&self, packet: Packet) -> Result<EncryptedPacket, CryptoError> {
        // Генерация случайного nonce
        let nonce = self.generate_nonce();
        
        // Шифрование AES-GCM
        let cipher = Aes256Gcm::new(&self.keys.current_key);
        let encrypted = cipher.encrypt(&nonce, packet.as_ref())?;
        
        // Добавление цифровой подписи
        let signature = self.sign_packet(&encrypted);
        
        Ok(EncryptedPacket {
            data: encrypted,
            nonce,
            signature,
        })
    }

    pub fn decrypt_packet(&self, packet: EncryptedPacket) -> Result<Packet, CryptoError> {
        // Проверка подписи
        if !self.verify_signature(&packet) {
            return Err(CryptoError::InvalidSignature);
        }
        
        // Расшифровка
        let cipher = Aes256Gcm::new(&self.keys.current_key);
        let decrypted = cipher.decrypt(&packet.nonce, packet.data.as_ref())?;
        
        Ok(Packet::from_bytes(decrypted))
    }
} 