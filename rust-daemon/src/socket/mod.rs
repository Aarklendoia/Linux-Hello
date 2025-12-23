use anyhow::{Result, Context};
use tokio::net::{UnixListener, UnixStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use std::path::PathBuf;
use serde_json::{json, Value};
use log::{info, error, debug};
use crate::config::Config;

pub struct Server {
    socket_path: PathBuf,
    config: Config,
}

impl Server {
    pub fn new(socket_path: PathBuf, config: Config) -> Result<Self> {
        Ok(Self { socket_path, config })
    }

    pub fn socket_path(&self) -> &PathBuf {
        &self.socket_path
    }

    pub async fn run(&mut self) -> Result<()> {
        // Remove old socket if exists
        if self.socket_path.exists() {
            std::fs::remove_file(&self.socket_path)?;
        }

        let listener = UnixListener::bind(&self.socket_path)
            .context("Failed to bind Unix socket")?;

        info!("Listening on {:?}", self.socket_path);

        loop {
            let (socket, _) = listener.accept().await?;
            let config = self.config.clone();

            tokio::spawn(async move {
                if let Err(e) = handle_client(socket, config).await {
                    error!("Client handling error: {}", e);
                }
            });
        }
    }
}

async fn handle_client(mut socket: UnixStream, config: Config) -> Result<()> {
    let mut buffer = vec![0; 4096];
    let n = socket.read(&mut buffer).await?;

    if n == 0 {
        return Ok(());
    }

    let request_str = String::from_utf8_lossy(&buffer[..n]);
    debug!("Received request: {}", request_str);

    let response = match process_request(&request_str, &config).await {
        Ok(resp) => resp,
        Err(e) => {
            error!("Request processing error: {}", e);
            json!({"status": "ERROR", "message": e.to_string()})
        }
    };

    let response_str = response.to_string();
    socket.write_all(response_str.as_bytes()).await?;

    Ok(())
}

async fn process_request(request: &str, _config: &Config) -> Result<Value> {
    let req: Value = serde_json::from_str(request)
        .context("Invalid request JSON")?;

    let action = req.get("action")
        .and_then(|v| v.as_str())
        .context("Missing action field")?;

    match action {
        "authenticate" => {
            let username = req.get("user")
                .and_then(|v| v.as_str())
                .unwrap_or("unknown");

            info!("Authenticating user: {}", username);

            // TODO: Implement full authentication flow:
            // 1. Initialize ONNX embeddings engine
            // 2. Open camera device
            // 3. Capture frame
            // 4. Extract embedding from frame
            // 5. Load user embeddings from ~/.linux-hello/faces/{user}/
            // 6. Compare similarities
            // 7. Return result

            // For now, return placeholder response
            Ok(json!({
                "status": "OK",
                "message": "Authentication successful (placeholder)",
                "user": username
            }))
        }
        "status" => {
            Ok(json!({
                "status": "running",
                "version": "1.0.0",
                "daemon": "rust",
                "backend": "onnx-runtime"
            }))
        }
        _ => {
            anyhow::bail!("Unknown action: {}", action)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_status_request() {
        let config = Config::default();
        let request = r#"{"action": "status"}"#;
        let response = process_request(request, &config).await;
        assert!(response.is_ok());
    }
}
