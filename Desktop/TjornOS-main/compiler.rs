pub struct CompilerSystem {
    frontend: Frontend,
    optimizer: Optimizer,
    backend: Backend,
    linker: Linker,
    interpreter: Interpreter,
}

impl CompilerSystem {
    pub fn new() -> Self {
        CompilerSystem {
            frontend: Frontend::new(),
            optimizer: Optimizer::new(),
            backend: Backend::new(),
            linker: Linker::new(),
            interpreter: Interpreter::new(),
        }
    }

    pub fn compile(&mut self, source: &str, target: Target) -> Result<Binary, CompileError> {
        // Парсинг исходного кода
        let ast = self.frontend.parse(source)?;
        
        // Семантический анализ
        let ir = self.frontend.analyze(ast)?;
        
        // Оптимизация
        let optimized = self.optimizer.optimize(ir)?;
        
        // Генерация кода
        let object = self.backend.generate_code(optimized, target)?;
        
        // Компоновка
        self.linker.link(object)
    }

    pub fn interpret(&mut self, source: &str) -> Result<Value, InterpretError> {
        // Парсинг
        let ast = self.frontend.parse(source)?;
        
        // Выполнение
        self.interpreter.execute(ast)
    }
} 