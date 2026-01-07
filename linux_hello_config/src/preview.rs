//! Module Preview - affichage de la caméra en direct
//!
//! Responsable de:
//! - Afficher les frames RGB en temps réel
//! - Dessiner la bounding box autour du visage détecté
//! - Afficher la barre de progression

pub struct PreviewState {
    pub current_frame: Option<Vec<u8>>,
    pub width: u32,
    pub height: u32,
}

impl PreviewState {
    pub fn new(width: u32, height: u32) -> Self {
        Self {
            current_frame: None,
            width,
            height,
        }
    }
}
