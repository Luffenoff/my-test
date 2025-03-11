use std::process::{Command, Stdio};
use crate::security::Sandbox;

pub struct BashTerminal {
    history: CommandHistory,
    environment: Environment,
    completion: TabCompletion,
    scripting: ScriptEngine,
    sandbox: Sandbox,
}

impl BashTerminal {
    pub fn new() -> Self {
        BashTerminal {
            history: CommandHistory::with_capacity(1000),
            environment: Environment::new(),
            completion: TabCompletion::new(),
            scripting: ScriptEngine::new(),
            sandbox: Sandbox::new(SandboxConfig::terminal()),
        }
    }

    pub fn execute_command(&mut self, command: &str) -> Result<(), TerminalError> {
        // Парсинг команды
        let parsed = self.parse_command(command)?;
        
        match parsed.command {
            "apt" | "apt-get" => self.handle_package_command(parsed),
            "bash" => self.execute_script(parsed),
            _ => {
                // Выполнение в песочнице
                let output = self.sandbox.run(Command::new(&parsed.command)
                    .args(&parsed.args)
                    .env_clear()
                    .envs(&self.environment.vars)
                    .stdout(Stdio::piped()))?;
                
                self.handle_output(output)
            }
        }
    }
} 