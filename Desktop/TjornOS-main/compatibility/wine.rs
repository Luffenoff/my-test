use crate::security::sandbox::Sandbox;

pub struct WineSubsystem {
    sandbox: Sandbox,
    dll_manager: DLLManager,
    registry_emulator: RegistryEmulator,
    directx_wrapper: DirectXWrapper,
}

impl WineSubsystem {
    pub fn new() -> Self {
        WineSubsystem {
            sandbox: Sandbox::new(SandboxConfig::wine()),
            dll_manager: DLLManager::new(),
            registry_emulator: RegistryEmulator::new(),
            directx_wrapper: DirectXWrapper::new(),
        }
    }

    pub fn run_exe(&self, path: &str) -> Result<(), WineError> {
        // Проверка файла на вредоносный код
        self.security_scan(path)?;
        
        // Подготовка окружения
        let env = self.prepare_environment()?;
        
        // Запуск в песочнице
        self.sandbox.execute(path, env)
    }
} 