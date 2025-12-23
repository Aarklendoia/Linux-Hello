use anyhow::{Result, Context};
use tokio::net::{UnixListener, UnixStream};
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use std::path::{Path, PathBuf};
use serde_json::{json, Value};
use log::{info, error, debug};
use crate::config::Config;
use crate::embeddings::Embeddings;

pub struct Server {
    socket_path: PathBuf,
    config: Config,
    embeddings: Embeddings,
}

impl Server {
    pub fn new(socket_path: PathBuf, config: Config) -> Result<Self> {
        let embeddings = Embeddings::new(&config)?;
        
        Ok(Self {
            socket_path,
            config,
            embeddings,
        })
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
            let embeddings = Embeddings::new(&config)?;

            tokio::spawn(async move {
                if let Err(e) = handle_client(socket, config, embeddings).await {
                    error!("Client handling error: {}", e);
                }
            });
        }
    }
}

async fn handle_client(
    mut socket: UnixStream,
    config: Config,
    embeddings: Embeddings,
) -> Result<()> {
    let mut buffer = vec![0; 4096];
    let n = socket.read(&mut buffer).await?;

    if n == 0 {
        return Ok(());
    }

    let request_str = String::from_utf8_lossy(&buffer[..n]);
    debug!("Received request: {}", request_str);

    let response = match process_request(&request_str, &config, &embeddings).await {
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

async fn process_request(
    request: &str,
    config: &Config,
    embeddings: &Embeddings,
) -> Result<Value> {
    let req: Value = serde_json::from_str(request)
        .context("Invalid request JSON")?;

    let action = req.get("action")
        .and_then(|v| v.as_str())
        .context("Missing action field")?;

    match action {
        "authenticate" => authenticate_user(request, config, embeddings).await,
        "status" => status_request(config, embeddings),
        "enroll" => enroll_user(request, config, embeddings).await,
        _ => Err(anyhow::anyhow!("Unknown action: {}", action)),
    }
}

async fn authenticate_user(
    request: &str,
    config: &Config,
    embeddings: &Embeddings,
) -> Result<Value> {
    let req: Value = serde_json::from_str(request)?;
    
    let username = req.get("user")
        .and_then(|v| v.as_str())
        .unwrap_or("unknown");

    info!("Authenticating user: {}", username);

    // TODO: Implement full authentication flow:
    // 1. Initialize ONNX embeddings engine
    // 2. Open camera device
    // 3. Capture frame
    // 4. Extract embedding from frame using ONNX model
    // 5. Load user embeddings from ~/.linux-hello/faces/{user}/
    // 6. Compare similarities with all stored embeddings
    // 7. Return best match score
    
    // For now, return placeholder response
    let similarity = 0.42;  // Dummy value
    let matched = embeddings.matches_threshold(similarity);

    Ok(json!({
        "status": if matched { "OK" } else { "FAIL" },
        "user": username,
        "similarity": similarity,
        "threshold": embeddings.threshold(),
        "message": if matched {
            "Authentication successful"
        } else {
            "Face not recognized"
        }
    }))
}

async fn enroll_user(
    request: &str,
    _config: &Config,
    _embeddings: &Embeddings,
) -> Result<Value> {
    let req: Value = serde_json::from_str(request)?;
    
    let username = req.get("user")
        .and_then(|v| v.as_str())
        .unwrap_or("unknown");

    info!("Enrolling user: {}", username);

    // TODO: Implement enrollment flow:
    // 1. Capture multiple frames from camera
    // 2. Extract embeddings
    // 3. Save to ~/.linux-hello/faces/{user}/*.npy
    // 4. Return status

    Ok(json!({
        "status": "OK",
        "message": "Enrollment not yet implemented",
        "user": username
    }))
}

fn status_request(
    config: &Config,
    embeddings: &Embeddings,
) -> Result<Value> {
    let model_exists = embeddings.model_path().exists();
    
    Ok(json!({
        "status": "running",
        "version": "1.0.0",
        "daemon": "rust",
        "backend": "onnx-runtime",
        "threshold": embeddings.threshold(),
        "model": {
            "path": embeddings.model_path().to_string_lossy(),
            "exists": model_exists
        },
        "camera": {
            "device": format!("/dev/video{}", config.camera_device)
        }
    }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_status_request() {
        let config = Config::default();
        let response = status_request(&config, &Embeddings::new(&config).unwrap());
        assert_eq!(response["status"], "running");
    }
}
