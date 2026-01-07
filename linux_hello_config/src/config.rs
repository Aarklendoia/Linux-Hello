//! Module Config - gestion de la configuration
//!
//! Responsable de:
//! - Paramètres d'enregistrement (nombre frames, timeouts)
//! - Paramètres de détection (seuils, modèles)
//! - Stockage de la configuration

use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use dirs;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GuiConfig {
    /// Nombre de frames à capturer pour l'enregistrement
    pub enrollment_frame_count: u32,

    /// Timeout maximum pour l'enregistrement (secondes)
    pub enrollment_timeout_secs: u64,

    /// Seuil de confiance minimum pour détection
    pub detection_confidence_threshold: f32,

    /// Seuil de qualité minimum
    pub quality_threshold: f32,

    /// Device caméra (ex: /dev/video0)
    pub camera_device: String,

    /// Répertoire de stockage des embeddings
    pub storage_path: PathBuf,
}

impl Default for GuiConfig {
    fn default() -> Self {
        Self {
            enrollment_frame_count: 30,
            enrollment_timeout_secs: 120,
            detection_confidence_threshold: 0.6,
            quality_threshold: 0.5,
            camera_device: "/dev/video0".to_string(),
            storage_path: dirs::config_dir()
                .unwrap_or_default()
                .join("linux-hello"),
        }
    }
}

impl GuiConfig {
    pub fn load() -> anyhow::Result<Self> {
        // TODO: Charger depuis fichier de config
        Ok(Self::default())
    }

    pub fn save(&self) -> anyhow::Result<()> {
        // TODO: Sauvegarder dans fichier de config
        Ok(())
    }
}
