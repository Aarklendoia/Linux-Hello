use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use anyhow::{Result, Context};
use std::env;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub threshold: f32,
    pub models_dir: PathBuf,
    pub camera_device: i32,
    pub log_level: String,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            threshold: 0.35,
            models_dir: PathBuf::from("/opt/linux-hello/models"),
            camera_device: 0,
            log_level: "info".to_string(),
        }
    }
}

impl Config {
    pub fn load() -> Result<Self> {
        let config_path = Self::config_path();
        
        if config_path.exists() {
            let content = fs::read_to_string(&config_path)
                .context("Failed to read config file")?;
            let config: Self = serde_json::from_str(&content)
                .context("Failed to parse config JSON")?;
            Ok(config)
        } else {
            log::info!("Config not found, using defaults");
            Ok(Self::default())
        }
    }

    pub fn save(&self) -> Result<()> {
        let config_path = Self::config_path();
        if let Some(parent) = config_path.parent() {
            fs::create_dir_all(parent)?;
        }
        let content = serde_json::to_string_pretty(self)?;
        fs::write(&config_path, content)?;
        Ok(())
    }

    fn config_path() -> PathBuf {
        if let Ok(home) = env::var("HOME") {
            PathBuf::from(home)
                .join(".linux-hello")
                .join("config.json")
        } else {
            PathBuf::from("/etc/linux-hello/config.json")
        }
    }

    pub fn recognition_model_path(&self) -> PathBuf {
        self.models_dir.join("recognition.onnx")
    }

    pub fn detection_model_path(&self) -> PathBuf {
        self.models_dir.join("detection.onnx")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = Config::default();
        assert_eq!(config.threshold, 0.35);
    }
}
