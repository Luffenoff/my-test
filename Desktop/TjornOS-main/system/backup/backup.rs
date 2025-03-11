use crate::security::Encryption;
use crate::storage::StorageManager;

pub struct BackupSystem {
    storage: StorageManager,
    encryption: Encryption,
    scheduler: BackupScheduler,
    snapshot_manager: SnapshotManager,
    cloud_sync: CloudSync,
}

impl BackupSystem {
    pub fn new() -> Self {
        BackupSystem {
            storage: StorageManager::new(),
            encryption: Encryption::new(),
            scheduler: BackupScheduler::new(),
            snapshot_manager: SnapshotManager::new(),
            cloud_sync: CloudSync::new(),
        }
    }

    pub fn create_backup(&mut self, config: BackupConfig) -> Result<BackupId, BackupError> {
        // Создание снапшота системы
        let snapshot = self.snapshot_manager.create_snapshot()?;
        
        // Шифрование данных
        let encrypted = self.encryption.encrypt_data(&snapshot)?;
        
        // Сохранение локально
        let backup_id = self.storage.store_backup(encrypted)?;
        
        // Синхронизация с облаком если настроено
        if config.cloud_sync {
            self.cloud_sync.upload_backup(backup_id)?;
        }
        
        Ok(backup_id)
    }

    pub fn restore_from_backup(&mut self, backup_id: BackupId) -> Result<(), BackupError> {
        // Загрузка бэкапа
        let encrypted = self.storage.load_backup(backup_id)?;
        
        // Расшифровка
        let snapshot = self.encryption.decrypt_data(&encrypted)?;
        
        // Восстановление системы
        self.snapshot_manager.restore_snapshot(&snapshot)
    }
} 