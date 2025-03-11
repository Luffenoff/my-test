pub struct Kernel {
    memory: MemoryManager,
    scheduler: TaskScheduler,
    devices: DeviceManager,
    fs: FileSystem,
    network: NetworkStack,
    security: SecurityManager,
}

impl Kernel {
    pub fn new(boot_info: &BootInfo) -> Self {
        // Инициализация базовых подсистем
        let memory = MemoryManager::new(boot_info.memory_map);
        let scheduler = TaskScheduler::new();
        let devices = DeviceManager::new();
        
        Kernel {
            memory,
            scheduler,
            devices,
            fs: FileSystem::new(),
            network: NetworkStack::new(),
            security: SecurityManager::new(),
        }
    }

    pub fn start(&mut self) -> ! {
        // Инициализация прерываний
        self.init_interrupts();
        
        // Запуск планировщика
        self.scheduler.start();
        
        // Монтирование корневой файловой системы
        self.fs.mount_root();
        
        // Запуск системных сервисов
        self.start_system_services();
        
        // Передача управления планировщику
        self.scheduler.run()
    }
} 