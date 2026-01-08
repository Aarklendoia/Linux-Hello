//! Linux Hello - Configuration GUI pour KDE/Wayland
//!
//! Interface graphique QML native avec thème Breeze pour:
//! - Enregistrement de visage avec preview en direct
//! - Configuration des paramètres d'authentification
//! - Gestion des visages enregistrés
//!
//! La logique métier communique via D-Bus avec hello_daemon

use std::env;
use std::path::PathBuf;
use std::process::Command;

fn main() {
    // Lance l'application QML avec Kirigami
    // Les fichiers QML sont dans le répertoire 'qml/'
    
    let manifest_dir = env::var("CARGO_MANIFEST_DIR")
        .unwrap_or_else(|_| ".".to_string());
    
    let qml_path = PathBuf::from(&manifest_dir)
        .join("qml")
        .join("main.qml")
        .to_string_lossy()
        .to_string();
    
    // Configuration pour VM/graphics virtuel
    let mut cmd = Command::new("qml");
    cmd.arg(&qml_path)
        // Wayland avec fallback X11/offscreen
        .env("QT_QPA_PLATFORM", "wayland;xcb;offscreen")
        // Force le style Breeze KDE
        .env("QT_STYLE_OVERRIDE", "org.kde.desktop")
        // XCB avec GPU si possible
        .env("QT_XCB_GL_INTEGRATION", "xcb_egl,none")
        // Désactive les avertissements de driver
        .env("QT_DEBUG_PLUGINS", "0")
        // Path pour les modules QML
        .env("QML_IMPORT_TRACE", "0");
    
    match cmd.spawn() {
        Ok(mut child) => {
            let _ = child.wait();
        }
        Err(e) => {
            eprintln!("Erreur lors du lancement de l'application QML : {}", e);
            eprintln!("Vérifie que 'qml' est installé : sudo apt install qml");
            std::process::exit(1);
        }
    }
}

