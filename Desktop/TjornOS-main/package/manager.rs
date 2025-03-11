use crate::security::SignatureVerifier;
use crate::network::SecureDownloader;

pub struct PackageManager {
    repositories: Vec<Repository>,
    installed_packages: HashMap<String, Package>,
    downloader: SecureDownloader,
    verifier: SignatureVerifier,
}

impl PackageManager {
    pub fn install(&mut self, package_name: &str) -> Result<(), PackageError> {
        // Поиск пакета
        let package = self.find_package(package_name)?;
        
        // Проверка зависимостей
        self.resolve_dependencies(&package)?;
        
        // Безопасная загрузка
        let data = self.downloader.download(&package.url)?;
        
        // Проверка подписи
        self.verifier.verify_package(&data, &package.signature)?;
        
        // Установка
        self.install_package(package, data)
    }
} 