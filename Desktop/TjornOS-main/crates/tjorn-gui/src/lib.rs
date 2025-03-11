pub mod compositor;
pub mod input;
pub mod render;
pub mod theme;
pub mod widget;
pub mod window;

pub use compositor::Compositor;
pub use render::Renderer;
pub use window::WindowManager;

use std::sync::Arc;
use vulkano::instance::Instance;
use winit::event_loop::EventLoop;

pub struct TjornGUI {
    window_system: WindowSystem,
    renderer: Renderer,
    compositor: Compositor,
    theme_manager: ThemeManager,
    widget_factory: WidgetFactory,
}

impl TjornGUI {
    pub fn new() -> Result<Self, GUIError> {
        let instance = Instance::new(None, &vulkano::instance::InstanceExtensions::none())?;

        Ok(Self {
            window_system: WindowSystem::new()?,
            renderer: Renderer::new(instance)?,
            compositor: Compositor::new()?,
            theme_manager: ThemeManager::new()?,
            widget_factory: WidgetFactory::new()?,
        })
    }

    pub fn run(self) -> Result<(), GUIError> {
        let event_loop = EventLoop::new();
        self.window_system.run(event_loop)
    }
}

pub fn init() {
    println!("Initializing {}", "tjorn-gui");
}
