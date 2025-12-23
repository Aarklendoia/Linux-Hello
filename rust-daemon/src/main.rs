mod config;
mod embeddings;
mod camera;
mod socket;

use anyhow::Result;
use log::{info, error};
use std::path::PathBuf;
use tokio::signal;

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::Builder::from_default_env()
        .filter_level(log::LevelFilter::Info)
        .init();

    info!("Linux Hello Daemon starting (Rust)");

    // Load configuration
    let config = config::Config::load()?;
    info!("Configuration loaded: threshold={}", config.threshold);

    // Initialize ONNX runtime for embeddings
    let _embeddings = embeddings::Embeddings::new(&config)?;
    info!("ONNX model loaded");

    // Check camera availability
    if let Err(e) = camera::Camera::test() {
        error!("Camera check failed: {}", e);
    } else {
        info!("Camera available");
    }

    // Start socket server
    let socket_path = PathBuf::from("/run/linux-hello/daemon.sock");
    
    // Ensure socket directory exists
    if let Some(parent) = socket_path.parent() {
        std::fs::create_dir_all(parent)?;
    }

    let mut server = socket::Server::new(socket_path, config)?;
    info!("Socket server starting on {:?}", server.socket_path());

    // Handle shutdown signals
    let ctrl_c = signal::ctrl_c();
    tokio::pin!(ctrl_c);

    tokio::select! {
        result = server.run() => {
            match result {
                Ok(_) => info!("Socket server stopped"),
                Err(e) => error!("Socket server error: {}", e),
            }
        }
        _ = &mut ctrl_c => {
            info!("Received SIGINT, shutting down");
        }
    }

    Ok(())
}
