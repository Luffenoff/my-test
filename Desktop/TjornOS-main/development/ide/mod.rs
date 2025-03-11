pub struct DevelopmentEnvironment {
    editors: Vec<CodeEditor>,
    debugger: Debugger,
    compiler_manager: CompilerManager,
    git_integration: GitIntegration,
    language_servers: LanguageServerManager,
}

impl DevelopmentEnvironment {
    pub fn new() -> Self {
        DevelopmentEnvironment {
            editors: vec![
                CodeEditor::new("rust"),
                CodeEditor::new("python"),
                CodeEditor::new("cpp"),
            ],
            debugger: Debugger::new(),
            compiler_manager: CompilerManager::new(),
            git_integration: GitIntegration::new(),
            language_servers: LanguageServerManager::new(),
        }
    }

    pub fn setup_project(&self, lang: &str) -> Result<Project, IDEError> {
        // Создание проекта
        let project = Project::new(lang);
        
        // Настройка окружения
        self.setup_environment(&project)?;
        
        // Инициализация git
        self.git_integration.init_repository(&project)?;
        
        Ok(project)
    }
} 