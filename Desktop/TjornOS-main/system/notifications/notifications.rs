use crate::ui::NotificationUI;
use crate::audio::SoundEffect;

pub struct NotificationSystem {
    queue: NotificationQueue,
    ui: NotificationUI,
    sounds: SoundEffects,
    rules: NotificationRules,
    history: NotificationHistory,
}

impl NotificationSystem {
    pub fn new() -> Self {
        NotificationSystem {
            queue: NotificationQueue::new(),
            ui: NotificationUI::new(),
            sounds: SoundEffects::new(),
            rules: NotificationRules::default(),
            history: NotificationHistory::new(),
        }
    }

    pub fn show_notification(&mut self, notification: Notification) -> Result<(), NotificationError> {
        // Проверка правил отображения
        if !self.rules.should_show(&notification) {
            return Ok(());
        }
        
        // Добавление в очередь
        self.queue.push(notification.clone())?;
        
        // Воспроизведение звука
        if notification.sound_enabled {
            self.sounds.play(&notification.sound_type)?;
        }
        
        // Отображение UI
        self.ui.display(&notification)?;
        
        // Сохранение в историю
        self.history.add(notification);
        
        Ok(())
    }
} 