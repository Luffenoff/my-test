use alloc::string::String;
use crate::security::SecureInput;

pub struct Terminal {
    history: CommandHistory,
    input_handler: SecureInput,
    shell: Shell,
    themes: TerminalThemes,
    plugins: PluginManager,
}

impl Terminal {
    pub fn new() -> Self {
        Terminal {
            history: CommandHistory::new(),
            input_handler: SecureInput::new(),
            shell: Shell::new(),
            themes: TerminalThemes::default(),
            plugins: PluginManager::new(),
        }
    }

    pub fn execute_command(&mut self, command: &str) -> Result<(), TerminalError> {
        // Проверка безопасности команды
        self.input_handler.validate_input(command)?;
        
        // Парсинг и выполнение
        match command.split_whitespace().next() {
            Some("apt") => self.package_manager.handle_apt(command),
            Some("run") => self.execute_program(command),
            Some("script") => self.run_script(command),
            _ => self.shell.execute(command),
        }
    }
} 