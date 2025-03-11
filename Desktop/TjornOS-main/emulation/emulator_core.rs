use crate::hardware::cpu::CPUEmulator;
use crate::hardware::memory::MemoryEmulator;

pub struct Emulator {
    cpu: CPUEmulator,
    memory: MemoryEmulator,
    devices: DeviceEmulator,
    state: EmulatorState,
    debugger: EmulatorDebugger,
}

impl Emulator {
    pub fn new(config: EmulatorConfig) -> Self {
        Emulator {
            cpu: CPUEmulator::new(config.cpu_type),
            memory: MemoryEmulator::new(config.memory_size),
            devices: DeviceEmulator::new(),
            state: EmulatorState::new(),
            debugger: EmulatorDebugger::new(),
        }
    }

    pub fn load_image(&mut self, image: &[u8]) -> Result<(), EmulatorError> {
        // Проверка формата
        self.validate_image(image)?;
        
        // Загрузка в память
        self.memory.load(image)?;
        
        // Инициализация состояния CPU
        self.cpu.init_state()?;
        
        // Настройка устройств
        self.devices.setup()?;
        
        Ok(())
    }

    pub fn run(&mut self) -> Result<(), EmulatorError> {
        while self.state.is_running() {
            // Выполнение инструкции
            let instruction = self.cpu.fetch()?;
            self.cpu.execute(instruction)?;
            
            // Обработка прерываний
            self.handle_interrupts()?;
            
            // Обновление состояния устройств
            self.devices.update()?;
            
            // Проверка точек останова
            self.debugger.check_breakpoints()?;
        }
        Ok(())
    }
} 