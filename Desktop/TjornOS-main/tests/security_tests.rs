use tjorn_security::{SecurityManager, AccessLevel, Encryption};
use anyhow::Result;

#[tokio::test]
async fn test_secure_boot_sequence() -> Result<()> {
    let security = SecurityManager::new()?;
    
    // Проверка цепочки доверия
    assert!(security.verify_boot_chain().await?);
    
    // Проверка целостности компонентов
    assert!(security.verify_kernel_integrity().await?);
    assert!(security.verify_critical_components().await?);
    
    Ok(())
}

#[test]
fn test_memory_encryption() -> Result<()> {
    let security = SecurityManager::new()?;
    let encryption = Encryption::new()?;
    
    // Тест шифрования памяти
    let sensitive_data = b"SECRET_DATA";
    let encrypted = encryption.encrypt_memory(sensitive_data)?;
    assert_ne!(encrypted.as_slice(), sensitive_data);
    
    // Тест дешифрования
    let decrypted = encryption.decrypt_memory(&encrypted)?;
    assert_eq!(decrypted.as_slice(), sensitive_data);
    
    Ok(())
}

#[tokio::test]
async fn test_access_control() -> Result<()> {
    let security = SecurityManager::new()?;
    
    // Тест контроля доступа
    assert!(security.check_access(AccessLevel::Public).await?);
    assert!(!security.check_access(AccessLevel::TopSecret).await?);
    
    Ok(())
} 