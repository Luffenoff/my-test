use std::sync::{Arc, RwLock};
use crate::users::User;
use crate::permissions::Permission;

pub struct AccessControl {
    policies: RwLock<Vec<SecurityPolicy>>,
    role_manager: RoleManager,
    permission_cache: PermissionCache,
}

impl AccessControl {
    pub fn new() -> Self {
        AccessControl {
            policies: RwLock::new(Vec::new()),
            role_manager: RoleManager::new(),
            permission_cache: PermissionCache::new(),
        }
    }

    pub fn check_permission(&self, user: &User, permission: Permission) -> Result<(), SecurityError> {
        // Проверка в кэше
        if let Some(result) = self.permission_cache.get(user, permission) {
            return result;
        }

        // Проверка политик
        let policies = self.policies.read().map_err(|_| SecurityError::LockError)?;
        for policy in policies.iter() {
            if policy.matches(user, permission) {
                return Ok(());
            }
        }

        Err(SecurityError::AccessDenied)
    }
} 