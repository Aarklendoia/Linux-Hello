//! Abstraction caméra pour le daemon
//!
//! Fournit une interface simple pour capturer des frames
//! et les passer au moteur de reconnaissance

use hello_camera::Frame;
use hello_face_core::Embedding;
use std::time::Duration;
use thiserror::Error;
use tracing::{debug, info};

/// Erreurs caméra
#[derive(Debug, Error)]
pub enum CameraError {
    #[error("Caméra non disponible")]
    NotAvailable,

    #[error("Timeout capture")]
    Timeout,

    #[error("Erreur capture: {0}")]
    CaptureError(String),

    #[error("Erreur extraction: {0}")]
    ExtractionError(String),
}

/// Résultat d'une capture caméra
pub struct CaptureResult {
    /// Frames capturées
    pub frames: Vec<Frame>,

    /// Embeddings extraits
    pub embeddings: Vec<Embedding>,

    /// Score de qualité moyen
    pub quality_score: f32,
}

/// Gestionnaire caméra pour le daemon
pub struct CameraManager {
    /// Timeout par défaut pour les captures (ms)
    default_timeout_ms: u64,
}

impl CameraManager {
    /// Créer un nouveau gestionnaire caméra
    pub fn new(default_timeout_ms: u64) -> Self {
        Self {
            default_timeout_ms,
        }
    }

    /// Vérifier si une caméra est disponible
    pub fn is_available(&self) -> bool {
        // Pour MVP: toujours true (implémentation réelle plus tard)
        true
    }

    /// Capturer N frames et extraire les embeddings
    ///
    /// # Arguments
    /// * `num_frames` - Nombre de frames à capturer
    /// * `timeout_ms` - Timeout en millisecondes (0 = utiliser default)
    ///
    /// # Returns
    /// CaptureResult avec frames et embeddings, ou CameraError
    pub async fn capture_frames(
        &self,
        num_frames: u32,
        timeout_ms: u64,
    ) -> Result<CaptureResult, CameraError> {
        let timeout = if timeout_ms == 0 {
            Duration::from_millis(self.default_timeout_ms)
        } else {
            Duration::from_millis(timeout_ms)
        };

        info!(
            "Capture de {} frames avec timeout {:?}",
            num_frames, timeout
        );

        // Pour MVP: génération de données de test
        // En production: utiliser hello_camera pour acquisition réelle
        let mut frames = Vec::new();
        let mut embeddings = Vec::new();

        for i in 0..num_frames {
            // Simulation frame
            let frame = Frame {
                data: vec![0; 1920 * 1080 * 3], // RGB dummy
                width: 1920,
                height: 1080,
                format: hello_camera::FrameFormat::Rgb8,
                timestamp_ms: i as u64 * 100,
            };

            // Simulation extraction embedding
            // En prod: utiliser hello_face_core::FaceDetector + extract_embedding
            let embedding = hello_face_core::Embedding {
                vector: (0..128).map(|j| (i as f32 + j as f32) / 1000.0).collect(),
                metadata: hello_face_core::EmbeddingMetadata {
                    model: "sim_model".to_string(),
                    model_version: "0.1.0".to_string(),
                    extracted_at: std::time::SystemTime::now()
                        .duration_since(std::time::UNIX_EPOCH)
                        .unwrap()
                        .as_secs(),
                    quality_score: 0.85,
                },
            };

            frames.push(frame);
            embeddings.push(embedding);

            debug!("Frame {}/{} capturée et embeddings extraits", i + 1, num_frames);
        }

        // Calculer score de qualité moyen
        let quality_score = 0.85; // À implémenter avec vraie logique

        Ok(CaptureResult {
            frames,
            embeddings,
            quality_score,
        })
    }

    /// Capturer une seule frame de test
    pub async fn test_capture(&self) -> Result<Vec<u8>, CameraError> {
        info!("Capture test");

        // Dummy image RGB 640x480
        Ok(vec![0; 640 * 480 * 3])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_camera_manager_available() {
        let camera = CameraManager::new(5000);
        assert!(camera.is_available());
    }

    #[tokio::test]
    async fn test_capture_frames() {
        let camera = CameraManager::new(5000);
        let result = camera.capture_frames(3, 0).await.unwrap();

        assert_eq!(result.frames.len(), 3);
        assert_eq!(result.embeddings.len(), 3);
        assert_eq!(result.embeddings[0].vector.len(), 128);
    }
}

