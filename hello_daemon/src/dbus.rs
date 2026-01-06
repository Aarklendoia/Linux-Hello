//! Surface D-Bus pour FaceAuthDaemon
//!
//! Wrapper qui expose les opérations du daemon via D-Bus

use crate::{DaemonConfig, FaceAuthDaemon};
use crate::dbus_interface::{
    DeleteFaceRequest, RegisterFaceRequest, VerifyRequest,
};
use std::sync::Arc;
use tracing::{debug, info, error};
use zbus::dbus_interface;
use tokio::sync::RwLock;

/// Wrapper D-Bus autour du daemon
pub struct FaceAuthInterface {
    daemon: Arc<RwLock<FaceAuthDaemon>>,
    version: String,
    storage_path: String,
}

impl FaceAuthInterface {
    pub fn new(daemon: FaceAuthDaemon) -> Self {
        let storage_path = daemon.config().storage_path.to_string_lossy().into_owned();
        Self {
            daemon: Arc::new(RwLock::new(daemon)),
            version: env!("CARGO_PKG_VERSION").to_string(),
            storage_path,
        }
    }
}

#[dbus_interface(name = "com.linuxhello.FaceAuth")]
impl FaceAuthInterface {
    /// Enregistrer un nouveau visage pour un utilisateur
    ///
    /// # Arguments
    /// * `request_json` - JSON string de RegisterFaceRequest
    ///
    /// # Returns
    /// JSON string de RegisterFaceResponse ou erreur
    pub async fn register_face(&self, request_json: &str) -> zbus::fdo::Result<String> {
        debug!("D-Bus call: register_face");

        let request: RegisterFaceRequest = match serde_json::from_str(request_json) {
            Ok(r) => r,
            Err(e) => {
                error!("JSON parse error: {}", e);
                return Err(zbus::fdo::Error::Failed(format!("JSON parse error: {}", e)));
            }
        };

        let daemon = self.daemon.write().await;
        let response = daemon.register_face(request).await;

        match response {
            Ok(response_json) => {
                info!("register_face succeeded");
                Ok(response_json)
            }
            Err(e) => {
                error!("register_face failed: {}", e);
                Err(zbus::fdo::Error::Failed(e.to_string()))
            }
        }
    }

    /// Supprimer un ou tous les visages
    ///
    /// # Arguments
    /// * `request_json` - JSON string de DeleteFaceRequest
    pub async fn delete_face(&self, request_json: &str) -> zbus::fdo::Result<()> {
        debug!("D-Bus call: delete_face");

        let request: DeleteFaceRequest = match serde_json::from_str(request_json) {
            Ok(r) => r,
            Err(e) => {
                error!("JSON parse error: {}", e);
                return Err(zbus::fdo::Error::Failed(format!("JSON parse error: {}", e)));
            }
        };

        let daemon = self.daemon.write().await;
        let response = daemon.delete_face(request).await;

        match response {
            Ok(_) => {
                info!("delete_face succeeded");
                Ok(())
            }
            Err(e) => {
                error!("delete_face failed: {}", e);
                Err(zbus::fdo::Error::Failed(e.to_string()))
            }
        }
    }

    /// Vérifier l'identité d'un utilisateur
    ///
    /// # Arguments
    /// * `request_json` - JSON string de VerifyRequest
    ///
    /// # Returns
    /// JSON string de VerifyResult
    pub async fn verify(&self, request_json: &str) -> zbus::fdo::Result<String> {
        debug!("D-Bus call: verify");

        let request: VerifyRequest = match serde_json::from_str(request_json) {
            Ok(r) => r,
            Err(e) => {
                error!("JSON parse error: {}", e);
                return Err(zbus::fdo::Error::Failed(format!("JSON parse error: {}", e)));
            }
        };

        let daemon = self.daemon.write().await;
        let result = daemon.verify(request).await;

        match result {
            Ok(result) => {
                let result_json = match serde_json::to_string(&result) {
                    Ok(j) => j,
                    Err(e) => {
                        error!("JSON serialize error: {}", e);
                        return Err(zbus::fdo::Error::Failed(e.to_string()));
                    }
                };
                info!("verify succeeded");
                Ok(result_json)
            }
            Err(e) => {
                error!("verify failed: {}", e);
                Err(zbus::fdo::Error::Failed(e.to_string()))
            }
        }
    }

    /// Lister les visages enregistrés pour un utilisateur
    ///
    /// # Arguments
    /// * `user_id` - UID de l'utilisateur
    ///
    /// # Returns
    /// JSON array de FaceRecord
    pub async fn list_faces(&self, user_id: u32) -> zbus::fdo::Result<String> {
        debug!("D-Bus call: list_faces for user_id={}", user_id);

        let daemon = self.daemon.write().await;
        let result = daemon.list_faces(user_id).await;

        match result {
            Ok(faces_json) => {
                info!("list_faces succeeded");
                Ok(faces_json)
            }
            Err(e) => {
                error!("list_faces failed: {}", e);
                Err(zbus::fdo::Error::Failed(e.to_string()))
            }
        }
    }

    /// Test de connexion
    pub async fn ping(&self) -> zbus::fdo::Result<String> {
        Ok("pong".to_string())
    }

    /// Version du daemon
    #[dbus_interface(property)]
    pub fn version(&self) -> String {
        self.version.clone()
    }

    /// Vérifier si une caméra est disponible
    #[dbus_interface(property)]
    pub fn camera_available(&self) -> bool {
        // On utilise try_read pour ne pas bloquer
        // En cas d'erreur, on suppose que c'est disponible
        self.daemon
            .try_read()
            .map(|daemon| daemon.is_camera_available())
            .unwrap_or(true)
    }

    /// Mode root ou user
    #[dbus_interface(property)]
    pub fn root_mode(&self) -> bool {
        self.daemon
            .try_read()
            .map(|daemon| daemon.config().root_mode)
            .unwrap_or(false)
    }

    /// Chemin de stockage
    #[dbus_interface(property)]
    pub fn storage_path(&self) -> String {
        self.storage_path.clone()
    }
}
