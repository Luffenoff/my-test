pub struct GamingSubsystem {
    vulkan_support: VulkanRenderer,
    opengl_support: OpenGLRenderer,
    controller_manager: ControllerManager,
    game_mode: GameMode,
}

impl GamingSubsystem {
    pub fn new() -> Self {
        GamingSubsystem {
            vulkan_support: VulkanRenderer::new(),
            opengl_support: OpenGLRenderer::new(),
            controller_manager: ControllerManager::new(),
            game_mode: GameMode::new(),
        }
    }

    pub fn enable_game_mode(&mut self) -> Result<(), GameError> {
        // Оптимизация CPU
        self.game_mode.optimize_cpu_scheduling()?;
        
        // Приоритет GPU
        self.game_mode.set_gpu_priority(Priority::High)?;
        
        // Отключение ненужных сервисов
        self.game_mode.disable_background_services()?;
        
        Ok(())
    }
} 