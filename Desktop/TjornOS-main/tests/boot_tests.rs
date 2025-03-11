use std::sync::Arc;

#[test]
fn test_core_subsystems_initialization() {
    // Проверка инициализации ядра
    assert!(tjorn_core::init().is_ok());
    
    // Проверка критических подсистем
    assert!(tjorn_memory::init().is_ok());
    assert!(tjorn_security::init().is_ok());
    assert!(tjorn_fs::init().is_ok());
}

#[tokio::test]
async fn test_system_boot_sequence() {
    // Тест последовательности загрузки
    let boot_result = async {
        // 1. Инициализация базовых компонентов
        tjorn_core::init()?;
        tjorn_memory::init()?;
        
        // 2. Запуск системы безопасности
        tjorn_security::init()?;
        
        // 3. Монтирование файловой системы
        tjorn_fs::init()?;
        
        // 4. Запуск сетевой подсистемы
        tjorn_network::init()?;
        
        Ok::<(), anyhow::Error>(())
    }.await;
    
    assert!(boot_result.is_ok());
}

#[test]
fn test_security_checks() {
    use tjorn_security::SecurityManager;
    
    let security = SecurityManager::new().unwrap();
    
    // Проверка базовых механизмов безопасности
    assert!(security.verify_system_integrity().is_ok());
    assert!(security.check_secure_boot().is_ok());
}

#[test]
fn test_memory_management() {
    use tjorn_memory::MemoryManager;
    
    let memory = MemoryManager::new().unwrap();
    
    // Проверка управления памятью
    assert!(memory.check_available_memory() > 0);
    assert!(memory.verify_memory_protection().is_ok());
} 