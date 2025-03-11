pub mod tcp;
pub mod udp;
pub mod dns;
pub mod http;
pub mod quic;
pub mod vpn;

pub use tcp::TcpStack;
pub use udp::UdpStack;
pub use http::HttpServer;

pub fn init() {
    println!("Initializing {}", "tjorn-network");
}
