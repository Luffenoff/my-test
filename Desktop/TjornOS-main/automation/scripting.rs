use crate::security::sandbox::ScriptSandbox;

pub struct ScriptingSystem {
    interpreters: HashMap<String, Interpreter>,
    sandbox: ScriptSandbox,
    scheduler: TaskScheduler,
    variables: VariableStore,
}

impl ScriptingSystem {
    pub fn new() -> Self {
        let mut interpreters = HashMap::new();
        interpreters.insert("bash".to_string(), Interpreter::bash());
        interpreters.insert("python".to_string(), Interpreter::python());
        interpreters.insert("rust".to_string(), Interpreter::rust());

        ScriptingSystem {
            interpreters,
            sandbox: ScriptSandbox::new(),
            scheduler: TaskScheduler::new(),
            variables: VariableStore::new(),
        }
    }

    pub fn execute_script(&mut self, path: &str) -> Result<(), ScriptError> {
        // Определение типа скрипта
        let script_type = self.detect_script_type(path)?;
        
        // Получение интерпретатора
        let interpreter = self.interpreters.get(&script_type)
            .ok_or(ScriptError::UnsupportedType)?;
        
        // Проверка безопасности
        self.sandbox.verify_script(path)?;
        
        // Выполнение
        interpreter.execute(path, &self.variables)
    }

    pub fn schedule_script(&mut self, path: &str, schedule: Schedule) -> Result<TaskId, ScriptError> {
        self.scheduler.add_task(path, schedule)
    }
} 