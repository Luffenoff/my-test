use crate::graphics::renderer::Compositor;
use crate::gui::window_system::WindowManager;
use crate::gui::theme::ThemeManager;

pub struct DesktopEnvironment {
    window_manager: WindowManager,
    compositor: Compositor,
    panel: Panel,
    dock: Dock,
    app_launcher: AppLauncher,
    theme_manager: ThemeManager,
    notifications: NotificationCenter,
}

impl DesktopEnvironment {
    pub fn new() -> Self {
        DesktopEnvironment {
            window_manager: WindowManager::new(),
            compositor: Compositor::new(),
            panel: Panel::new(),
            dock: Dock::new(),
            app_launcher: AppLauncher::new(),
            theme_manager: ThemeManager::new(),
            notifications: NotificationCenter::new(),
        }
    }

    pub fn launch_application(&mut self, app_id: &str) -> Result<(), DesktopError> {
        // Проверка безопасности
        self.verify_application(app_id)?;
        
        // Создание окна
        let window = self.window_manager.create_window()?;
        
        // Запуск приложения
        self.app_launcher.launch(app_id, window)
    }
} 