use crate::network::security::SecureDownloader;
use crate::package::manager::PackageManager;

pub struct AppStore {
    package_manager: PackageManager,
    downloader: SecureDownloader,
    categories: Vec<Category>,
    search_engine: SearchEngine,
    reviews: ReviewSystem,
    updates: UpdateManager,
}

impl AppStore {
    pub fn new() -> Self {
        AppStore {
            package_manager: PackageManager::new(),
            downloader: SecureDownloader::new(),
            categories: Category::defaults(),
            search_engine: SearchEngine::new(),
            reviews: ReviewSystem::new(),
            updates: UpdateManager::new(),
        }
    }

    pub fn install_application(&mut self, app_id: &str) -> Result<(), StoreError> {
        // Поиск приложения
        let app = self.search_engine.find_app(app_id)?;
        
        // Проверка совместимости
        self.check_compatibility(&app)?;
        
        // Проверка зависимостей
        let dependencies = self.resolve_dependencies(&app)?;
        
        // Загрузка и установка
        self.download_and_install(app, dependencies)
    }

    pub fn search_applications(&self, query: &str) -> Vec<Application> {
        self.search_engine.search(query, &self.categories)
    }

    pub fn check_updates(&self) -> Vec<Update> {
        self.updates.check_available_updates()
    }
} 