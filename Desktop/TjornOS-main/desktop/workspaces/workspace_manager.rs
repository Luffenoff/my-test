use crate::graphics::renderer::Compositor;
use crate::gui::window_system::WindowManager;

pub struct WorkspaceManager {
    workspaces: Vec<Workspace>,
    current: WorkspaceId,
    compositor: Compositor,
    window_manager: WindowManager,
    effects: WorkspaceEffects,
}

impl WorkspaceManager {
    pub fn new() -> Self {
        WorkspaceManager {
            workspaces: vec![Workspace::new(WorkspaceId(0))],
            current: WorkspaceId(0),
            compositor: Compositor::new(),
            window_manager: WindowManager::new(),
            effects: WorkspaceEffects::new(),
        }
    }

    pub fn create_workspace(&mut self) -> WorkspaceId {
        let id = WorkspaceId(self.workspaces.len());
        let workspace = Workspace::new(id);
        self.workspaces.push(workspace);
        id
    }

    pub fn switch_to(&mut self, id: WorkspaceId) -> Result<(), WorkspaceError> {
        // Сохранение состояния текущего рабочего стола
        self.save_current_state()?;
        
        // Анимация перехода
        self.effects.transition_start()?;
        
        // Переключение композитора
        self.compositor.switch_workspace(id)?;
        
        // Обновление окон
        self.window_manager.update_workspace(id)?;
        
        // Завершение анимации
        self.effects.transition_end()?;
        
        self.current = id;
        Ok(())
    }

    pub fn move_window_to_workspace(&mut self, window_id: WindowId, workspace_id: WorkspaceId) -> Result<(), WorkspaceError> {
        // Проверка существования рабочего стола
        self.validate_workspace(workspace_id)?;
        
        // Перемещение окна
        self.window_manager.move_to_workspace(window_id, workspace_id)?;
        
        // Обновление композиции
        self.compositor.update()?;
        
        Ok(())
    }
} 