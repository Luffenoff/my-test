use std::sync::Arc;
use rand::Rng;
use crate::hardware::quantum::QuantumDevice;

pub struct QuantumEncryption {
    quantum_device: Arc<QuantumDevice>,
    entropy_pool: EntropyPool,
    key_distillation: KeyDistillation,
}

impl QuantumEncryption {
    pub fn new(quantum_device: Arc<QuantumDevice>) -> Self {
        QuantumEncryption {
            quantum_device,
            entropy_pool: EntropyPool::new(),
            key_distillation: KeyDistillation::new(),
        }
    }

    pub async fn generate_quantum_key(&mut self, length: usize) -> Result<QuantumKey, QuantumError> {
        // Получение квантовых случайных чисел
        let raw_qubits = self.quantum_device.generate_qubits(length * 2)?;
        
        // Измерение состояний и получение сырых битов
        let raw_bits = self.measure_qubits(&raw_qubits)?;
        
        // Очистка ключа через квантовую дистилляцию
        let clean_bits = self.key_distillation.distill(raw_bits)?;
        
        // Формирование финального ключа
        Ok(QuantumKey::new(clean_bits))
    }

    pub async fn establish_quantum_channel(&mut self, peer: &QuantumPeer) -> Result<SecureChannel, QuantumError> {
        // Квантовое распределение ключей
        let shared_key = self.quantum_key_distribution(peer).await?;
        
        // Проверка нарушений в квантовом канале
        self.verify_channel_security(peer)?;
        
        // Создание защищенного канала
        Ok(SecureChannel::new(shared_key))
    }
} 