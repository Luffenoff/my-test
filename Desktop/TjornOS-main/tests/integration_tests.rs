use anyhow::Result;

#[tokio::test]
async fn test_full_system_integration() -> Result<()> {
    // Тестирование полной интеграции системы
    
    // 1. Загрузка ядра
    tjorn_core::init()?;
    
    // 2. Проверка подсистем
    let subsystems = vec![
        "tjorn-memory",
        "tjorn-security", 
        "tjorn-fs",
        "tjorn-network",
        "tjorn-gui",
        "tjorn-audio"
    ];
    
    for subsystem in subsystems {
        println!("Testing subsystem: {}", subsystem);
        assert!(test_subsystem(subsystem).is_ok());
    }
    
    // 3. Проверка взаимодействия компонентов
    test_component_interaction().await?;
    
    Ok(())
}

fn test_subsystem(name: &str) -> Result<()> {
    match name {
        "tjorn-memory" => tjorn_memory::init()?,
        "tjorn-security" => tjorn_security::init()?,
        "tjorn-fs" => tjorn_fs::init()?,
        "tjorn-network" => tjorn_network::init()?,
        "tjorn-gui" => tjorn_gui::init()?,
        "tjorn-audio" => tjorn_audio::init()?,
        _ => panic!("Unknown subsystem: {}", name),
    }
    Ok(())
}

async fn test_component_interaction() -> Result<()> {
    // Тест взаимодействия между компонентами
    let security = tjorn_security::SecurityManager::new()?;
    let memory = tjorn_memory::MemoryManager::new()?;
    
    // Проверка безопасного выделения памяти
    let protected_memory = security.allocate_secure_memory(&memory, 1024)?;
    assert!(protected_memory.len() == 1024);
    
    Ok(())
} 