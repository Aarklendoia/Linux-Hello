//! Gestion du streaming de capture depuis le daemon
//!
//! Module pour recevoir et traiter les frames en temps réel

use serde::{Deserialize, Serialize};

/// Événement de frame reçu du daemon
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CaptureFrame {
    /// Numéro de la frame (0-indexed)
    pub frame_number: u32,

    /// Nombre total de frames attendues
    pub total_frames: u32,

    /// Données RGB brutes (640×480×3 ou autre)
    pub frame_data: Vec<u8>,

    /// Largeur de l'image
    pub width: u32,

    /// Hauteur de l'image
    pub height: u32,

    /// Un visage a-t-il été détecté?
    pub face_detected: bool,

    /// Bounding box si visage détecté
    pub face_box: Option<FaceBox>,

    /// Score de qualité (0.0-1.0)
    pub quality_score: f32,

    /// Timestamp de capture (ms)
    pub timestamp_ms: u64,
}

/// Bounding box d'un visage détecté
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FaceBox {
    /// Position X en pixels
    pub x: u32,
    /// Position Y en pixels
    pub y: u32,
    /// Largeur du box en pixels
    pub width: u32,
    /// Hauteur du box en pixels
    pub height: u32,
    /// Score de confiance (0.0-1.0)
    pub confidence: f32,
}

impl FaceBox {
    /// Vérifier si un point est dans le bounding box
    pub fn contains(&self, px: u32, py: u32) -> bool {
        px >= self.x && px < self.x + self.width && py >= self.y && py < self.y + self.height
    }

    /// Retourner le centre du bounding box
    pub fn center(&self) -> (u32, u32) {
        (
            self.x + self.width / 2,
            self.y + self.height / 2,
        )
    }

    /// Calculer le pourcentage de completion basé sur la frame
    pub fn completion_percent(&self, frame_num: u32, total_frames: u32) -> f32 {
        if total_frames == 0 {
            0.0
        } else {
            (frame_num as f32 / total_frames as f32) * 100.0
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_face_box_contains() {
        let face_box = FaceBox {
            x: 100,
            y: 100,
            width: 200,
            height: 200,
            confidence: 0.9,
        };

        assert!(face_box.contains(150, 150)); // Center
        assert!(face_box.contains(100, 100)); // Top-left corner
        assert!(!face_box.contains(99, 100)); // Outside left
        assert!(!face_box.contains(300, 150)); // Outside right
    }

    #[test]
    fn test_face_box_center() {
        let face_box = FaceBox {
            x: 100,
            y: 100,
            width: 200,
            height: 200,
            confidence: 0.9,
        };

        let (cx, cy) = face_box.center();
        assert_eq!(cx, 200);
        assert_eq!(cy, 200);
    }

    #[test]
    fn test_completion_percent() {
        let face_box = FaceBox {
            x: 0,
            y: 0,
            width: 100,
            height: 100,
            confidence: 0.9,
        };

        let percent = face_box.completion_percent(10, 30);
        assert!((percent - 33.33).abs() < 0.1);
    }
}
