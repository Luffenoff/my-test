use crate::terminal::terminal::Terminal;
use crate::development::git::GitIntegration;

pub struct IDE {
    project_manager: ProjectManager,
    editor: Editor,
    debugger: Debugger,
    compiler: CompilerManager,
    terminal: Terminal,
    git: GitIntegration,
}

impl IDE {
    pub fn new() -> Self {
        IDE {
            project_manager: ProjectManager::new(),
            editor: Editor::new(),
            debugger: Debugger::new(),
            compiler: CompilerManager::new(),
            terminal: Terminal::new(),
            git: GitIntegration::new(),
        }
    }

    pub fn create_project(&mut self, config: ProjectConfig) -> Result<Project, IDEError> {
        // Создание структуры проекта
        let project = self.project_manager.create_project(config)?;
        
        // Инициализация git репозитория
        self.git.init_repository(&project)?;
        
        // Настройка окружения сборки
        self.compiler.setup_environment(&project)?;
        
        // Создание конфигурации отладки
        self.debugger.create_config(&project)?;
        
        Ok(project)
    }

    pub fn debug_project(&mut self, project: &Project) -> Result<(), DebugError> {
        // Сборка проекта в режиме отладки
        self.compiler.build_debug(project)?;
        
        // Запуск отладчика
        self.debugger.start(project)?;
        
        // Установка точек останова
        self.debugger.set_breakpoints(&project.breakpoints)?;
        
        Ok(())
    }
} 