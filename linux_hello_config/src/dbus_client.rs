//! Client D-Bus pour la GUI
//!
//! Gère la connexion et l'écoute des signaux D-Bus du daemon

#[allow(unused_imports)]
use std::sync::Arc;
#[allow(unused_imports)]
use tokio::sync::Mutex;
use tracing::info;

/// Client D-Bus pour la GUI
pub struct DBusClient {
    // Future: zbus::Connection
}

impl DBusClient {
    /// Créer un nouveau client D-Bus
    pub fn new() -> Self {
        Self {}
    }

    /// Établir la connexion au daemon
    pub async fn connect(&mut self) -> Result<(), String> {
        info!("Connexion au daemon D-Bus...");
        // TODO: Implémenter la connexion zbus
        Ok(())
    }

    /// S'abonner aux signaux de capture
    pub async fn subscribe_to_capture(&self) -> Result<(), String> {
        info!("Abonnement aux signaux de capture...");
        // TODO: Écouter CaptureProgress, CaptureCompleted, CaptureError
        Ok(())
    }

    /// Démarrer une session de capture
    pub async fn start_capture(&self, user_id: u32, num_frames: u32) -> Result<(), String> {
        info!(
            "Démarrage capture: user_id={}, frames={}",
            user_id, num_frames
        );
        // TODO: Appeler daemon via D-Bus
        Ok(())
    }
}

impl Default for DBusClient {
    fn default() -> Self {
        Self::new()
    }
}
