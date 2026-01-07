//! Types et structures pour le streaming de capture en direct
//!
//! Fournit les événements et structures pour afficher une preview
//! en temps réel avec détection de visage

use serde::{Deserialize, Serialize};

/// Événement d'une frame capturée pendant l'enregistrement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CaptureFrameEvent {
    /// Numéro de la frame (0-indexed)
    pub frame_number: u32,

    /// Nombre total de frames à capturer
    pub total_frames: u32,

    /// Données brutes RGB (640×480×3)
    /// Note: Pour transmission D-Bus, peut être compressée en JPEG
    pub frame_data: Vec<u8>,

    /// Largeur de l'image
    pub width: u32,

    /// Hauteur de l'image
    pub height: u32,

    /// Un visage a-t-il été détecté?
    pub face_detected: bool,

    /// Bounding box du visage détecté (x, y, width, height)
    /// None si aucun visage
    pub face_box: Option<FaceBox>,

    /// Score de qualité de cette frame (0.0-1.0)
    pub quality_score: f32,

    /// Timestamp de capture (ms depuis début)
    pub timestamp_ms: u64,
}

impl CaptureFrameEvent {
    /// Créer un nouvel événement de frame
    pub fn new(frame_number: u32, total_frames: u32, width: u32, height: u32) -> Self {
        Self {
            frame_number,
            total_frames,
            frame_data: Vec::new(),
            width,
            height,
            face_detected: false,
            face_box: None,
            quality_score: 0.0,
            timestamp_ms: 0,
        }
    }

    /// Progres en pourcentage (0-100)
    pub fn progress_percent(&self) -> u32 {
        if self.total_frames == 0 {
            return 0;
        }
        ((self.frame_number + 1) * 100) / self.total_frames
    }

    /// Est-ce la dernière frame?
    pub fn is_last_frame(&self) -> bool {
        self.frame_number + 1 >= self.total_frames
    }
}

/// Bounding box d'un visage détecté
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq)]
pub struct FaceBox {
    /// Position X du coin supérieur gauche
    pub x: u32,

    /// Position Y du coin supérieur gauche
    pub y: u32,

    /// Largeur du rectangle
    pub width: u32,

    /// Hauteur du rectangle
    pub height: u32,

    /// Confiance de la détection (0.0-1.0)
    pub confidence: f32,
}

impl FaceBox {
    /// Créer une nouvelle bounding box
    pub fn new(x: u32, y: u32, width: u32, height: u32, confidence: f32) -> Self {
        Self {
            x,
            y,
            width,
            height,
            confidence,
        }
    }

    /// Centrer la box dans une image
    pub fn center(&self) -> (u32, u32) {
        (self.x + self.width / 2, self.y + self.height / 2)
    }

    /// Vérifier si un point est dans la box
    pub fn contains(&self, px: u32, py: u32) -> bool {
        px >= self.x && px < self.x + self.width && py >= self.y && py < self.y + self.height
    }
}

/// État d'une session de capture
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CaptureState {
    /// Session non initialisée
    Idle,

    /// En attente de placement de la caméra
    Waiting,

    /// Capture en cours
    Capturing,

    /// Capture terminée avec succès
    Completed,

    /// Erreur pendant la capture
    Failed,

    /// Capture annulée par l'utilisateur
    Cancelled,
}

impl std::fmt::Display for CaptureState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CaptureState::Idle => write!(f, "Inactif"),
            CaptureState::Waiting => write!(f, "En attente"),
            CaptureState::Capturing => write!(f, "Capture en cours"),
            CaptureState::Completed => write!(f, "Terminé"),
            CaptureState::Failed => write!(f, "Erreur"),
            CaptureState::Cancelled => write!(f, "Annulé"),
        }
    }
}

/// Configuration pour une session de capture
#[derive(Debug, Clone)]
pub struct CaptureConfig {
    /// Nombre de frames à capturer
    pub num_frames: u32,

    /// Timeout total en millisecondes (0 = infini)
    pub timeout_ms: u64,

    /// Seuil de confiance minimum pour détection (0.0-1.0)
    pub detection_confidence_threshold: f32,

    /// Seuil de qualité minimum (0.0-1.0)
    pub quality_threshold: f32,

    /// Accepter les frames sans visage?
    pub accept_no_face: bool,
}

impl Default for CaptureConfig {
    fn default() -> Self {
        Self {
            num_frames: 30,
            timeout_ms: 120000, // 2 minutes
            detection_confidence_threshold: 0.6,
            quality_threshold: 0.5,
            accept_no_face: true,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_capture_frame_event_progress() {
        let mut event = CaptureFrameEvent::new(5, 30, 640, 480);
        assert_eq!(event.progress_percent(), 20); // (5+1)*100/30 = 20

        event.frame_number = 29;
        assert_eq!(event.progress_percent(), 100);
    }

    #[test]
    fn test_face_box_contains() {
        let face = FaceBox::new(100, 100, 50, 50, 0.9);
        assert!(face.contains(125, 125));
        assert!(!face.contains(50, 50));
        assert!(!face.contains(150, 150));
    }

    #[test]
    fn test_face_box_center() {
        let face = FaceBox::new(100, 100, 50, 50, 0.9);
        assert_eq!(face.center(), (125, 125));
    }
}
