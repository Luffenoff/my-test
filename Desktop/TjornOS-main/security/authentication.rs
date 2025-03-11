use std::sync::Arc;
use crate::crypto::hash::Hash;
use crate::users::UserCredentials;

pub struct AuthenticationManager {
    password_hasher: PasswordHasher,
    token_manager: TokenManager,
    mfa_provider: MultiFactorAuth,
    session_manager: SessionManager,
}

impl AuthenticationManager {
    pub fn new() -> Self {
        AuthenticationManager {
            password_hasher: PasswordHasher::new(HashAlgorithm::Argon2id),
            token_manager: TokenManager::new(),
            mfa_provider: MultiFactorAuth::new(),
            session_manager: SessionManager::new(),
        }
    }

    pub async fn authenticate(&self, credentials: UserCredentials) -> Result<AuthToken, AuthError> {
        // Проверка учетных данных
        self.verify_credentials(&credentials)?;

        // Проверка MFA если включено
        if self.mfa_provider.is_enabled_for_user(&credentials.username) {
            self.mfa_provider.verify_code(&credentials.mfa_code)?;
        }

        // Создание сессии
        let token = self.token_manager.generate_token()?;
        self.session_manager.create_session(&credentials.username, &token)?;

        Ok(token)
    }
} 