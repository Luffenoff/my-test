use crate::network::security::AdvancedFirewall;
use crate::network::security::VPNManager;
use crate::network::security::SSLInspector;
use crate::network::security::DNSSecurity;

pub struct NetworkSecurity {
    firewall: AdvancedFirewall,
    vpn_manager: VPNManager,
    ssl_inspector: SSLInspector,
    dns_security: DNSSecurity,
}

impl NetworkSecurity {
    pub fn new() -> Self {
        NetworkSecurity {
            firewall: AdvancedFirewall::new(),
            vpn_manager: VPNManager::new(),
            ssl_inspector: SSLInspector::new(),
            dns_security: DNSSecurity::new(),
        }
    }

    pub fn secure_connection(&self, connection: &mut Connection) -> Result<(), SecurityError> {
        // Проверка SSL/TLS
        self.ssl_inspector.verify_certificate(&connection)?;
        
        // Настройка DNS over HTTPS
        self.dns_security.enable_secure_dns(connection)?;
        
        // Применение правил файрвола
        self.firewall.apply_rules(connection)?;
        
        // Маршрутизация через VPN если необходимо
        self.vpn_manager.route_if_needed(connection)
    }
} 