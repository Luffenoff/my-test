use crate::security::security::Permission;

pub struct SystemAPI {
    process_api: ProcessAPI,
    file_api: FileAPI,
    network_api: NetworkAPI,
    device_api: DeviceAPI,
    security: SecurityManager,
}

impl SystemAPI {
    pub fn new() -> Self {
        SystemAPI {
            process_api: ProcessAPI::new(),
            file_api: FileAPI::new(),
            network_api: NetworkAPI::new(),
            device_api: DeviceAPI::new(),
            security: SecurityManager::new(),
        }
    }

    pub fn create_process(&self, config: ProcessConfig) -> Result<ProcessHandle, APIError> {
        // Проверка прав
        self.security.check_permission(Permission::CreateProcess)?;
        
        // Создание процесса
        let process = self.process_api.create(config)?;
        
        // Настройка окружения
        self.setup_process_environment(&process)?;
        
        Ok(process)
    }

    pub fn open_file(&self, path: &str, mode: FileMode) -> Result<FileHandle, APIError> {
        // Проверка прав доступа
        self.security.check_file_access(path, mode)?;
        
        // Открытие файла
        self.file_api.open(path, mode)
    }
} 