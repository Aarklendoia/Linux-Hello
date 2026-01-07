fn detect_simple_contrast(
        &self,
        frame_data: &[u8],
        _width: u32,
        _height: u32,
        channels: u32,
        face_x: u32,
        face_y: u32,
        face_width: u32,
        face_height: u32,
    ) -> bool# Plan d'Implémentation: GUI Preview en Direct

## 🎯 Objectif Global

Créer une interface KDE/Wayland pour l'enregistrement de visage avec:

- ✨ Preview en direct (30fps)
- 📦 Détection de bounding box
- 📊 Barre de progression (0-30 frames)

## 📐 Architecture Globale

```
Utilisateur
    ↓ (clique "Enregistrer")
GUI (linux_hello_config)
    ↓ D-Bus: StartCapture(user_id, num_frames=30)
Daemon (hello_daemon)
    ├─ Capture V4L2 (30fps)
    ├─ StubDetector (rapide)
    └─ Émet signal D-Bus: CaptureProgress
         ↓ (30 fois)
GUI (reçoit signal)
    ├─ Affiche frame RGB
    ├─ Dessine bounding box
    ├─ Met à jour barre
    └─ Affiche sur écran
```

## 📋 Tâches dans l'Ordre

### Phase 1: Daemon Streaming (2-3 heures)

#### 1.1 Modifier `hello_daemon/src/camera.rs`

**Ajouter méthode async pour streaming**

```rust
pub struct CaptureSession {
    current_frame: u32,
    total_frames: u32,
    detector: Box<dyn FaceDetector>,
}

impl CameraManager {
    pub async fn start_capture_stream(
        &mut self,
        num_frames: u32,
        on_frame: impl Fn(CaptureFrameEvent),
    ) -> Result<(), CameraError> {
        // Boucle capture
        for frame_num in 0..num_frames {
            // 1. Capturer frame V4L2
            let frame = self.camera.capture(1000)?;
            
            // 2. Détecter visage
            let faces = self.detector.detect(
                &frame.data, frame.width, frame.height, 3
            )?;
            
            // 3. Créer événement
            let event = CaptureFrameEvent {
                frame_number: frame_num,
                total_frames: num_frames,
                frame_data: frame.data,
                width: frame.width,
                height: frame.height,
                face_detected: !faces.is_empty(),
                face_box: faces.first().map(|f| FaceBox {
                    x: f.bounding_box.0,
                    y: f.bounding_box.1,
                    width: f.bounding_box.2,
                    height: f.bounding_box.3,
                    confidence: f.confidence,
                }),
                quality_score: 0.85,
                timestamp_ms: ...,
            };
            
            // 4. Callback/Signal D-Bus
            on_frame(event);
        }
    }
}
```

#### 1.2 Ajouter signaux D-Bus dans `hello_daemon/src/dbus.rs`

```rust
#[dbus_interface(signal)]
async fn capture_progress(
    &self,
    event_json: &str,  // Sérialiser CaptureFrameEvent
) -> zbus::fdo::Result<()>;

// Modifier register_face pour appeler streaming
pub async fn register_face(&self, request_json: &str) -> zbus::fdo::Result<String> {
    // Lors de capture_frames, émettre signals
    self.inner.capture_progress(&json).await?;
}
```

#### 1.3 Tester la partie daemon

```bash
# Attendre les signaux D-Bus
dbus-monitor "interface=com.linuxhello.FaceAuth"

# Depuis CLI, lancer enregistrement
./target/debug/linux-hello enroll 1000
```

---

### Phase 2: Réception D-Bus dans GUI (2 heures)

#### 2.1 Modifier `linux_hello_config/src/main.rs`

```rust
struct LinuxHelloConfig {
    current_screen: Screen,
    dbus_connection: Option<zbus::Connection>,
    current_frame: Option<CaptureFrameEvent>,
}

// Ajouter subscription D-Bus
fn subscription(&self) -> iced::Subscription<Message> {
    if matches!(self.current_screen, Screen::Enrollment) {
        subscribe_to_capture_progress()
            .map(|event| Message::FrameCaptured(event))
    } else {
        iced::Subscription::none()
    }
}
```

#### 2.2 Fonction subscription D-Bus

```rust
fn subscribe_to_capture_progress() -> iced::Subscription<CaptureFrameEvent> {
    iced::Subscription::run_with_id(
        "capture_progress".into(),
        || async {
            // Connecter à D-Bus
            let conn = zbus::Connection::session().await?;
            let proxy = conn.object_server()
                .at("/com/linuxhello/FaceAuth")
                .await?;
            
            // Écouter signaux CaptureProgress
            let mut stream = proxy.match_signal(
                "com.linuxhello.FaceAuth.CaptureProgress"
            ).await?;
            
            while let Some(msg) = stream.next().await {
                let event = parse_event(&msg)?;
                yield event;
            }
        }
    )
}
```

---

### Phase 3: Rendu Preview (3-4 heures)

#### 3.1 Implémenter `linux_hello_config/src/preview.rs`

```rust
pub struct PreviewWidget {
    frame_data: Option<Vec<u8>>,
    width: u32,
    height: u32,
    face_box: Option<FaceBox>,
}

impl PreviewWidget {
    pub fn draw(&self) -> Element<Message> {
        // Utiliser `pixels` pour rendu RGB
        let texture = self.create_texture();
        
        // Dessiner bounding box vert
        if let Some(face) = self.face_box {
            self.draw_box(&texture, face, Color::GREEN, 2);
        }
        
        // Retourner Element
        ...
    }
    
    fn draw_box(&self, texture: &mut [u8], box_: FaceBox, color: Color, thickness: u32) {
        // Bresenham line drawing
        // Haut, bas, gauche, droit du carré
    }
}
```

#### 3.2 Implémenter `view_enrollment()`

```rust
fn view_enrollment(&self) -> Element<Message> {
    Column::new()
        .push(Text::new("Enregistrement de Visage"))
        .push(
            // Preview widget
            self.preview_widget.draw()
        )
        .push(
            // Progression bar
            ProgressBar::new(0.0..=1.0)
                .value((frame_num / total_frames) as f32)
        )
        .push(Text::new(format!("{}/{}", frame_num, total_frames)))
        .push(
            // Buttons
            Row::new()
                .push(Button::new(Text::new("Démarrer")))
                .push(Button::new(Text::new("Arrêter")))
        )
        .into()
}
```

---

### Phase 4: Intégration Complète (2 heures)

#### 4.1 Handler messages pour D-Bus

```rust
Message::FrameCaptured(event) => {
    self.current_frame = Some(event);
    // L'écran se redessine automatiquement
}

Message::StartCapture => {
    // Appeler daemon via D-Bus
    self.dbus_connection.call_method(
        "StartCapture",
        (1000_u32, 30_u32, 120000_u64)
    ).await?;
}
```

#### 4.2 Tests intégration

```bash
# Terminal 1: Lancer daemon
./target/debug/hello-daemon --debug

# Terminal 2: Lancer GUI
./target/release/linux_hello_config

# Terminal 3: Monitor D-Bus
dbus-monitor "interface=com.linuxhello.FaceAuth"
```

---

## 📊 Estimation d'Effort

| Phase | Temps | Compliqué |
|-------|-------|-----------|
| 1. Daemon streaming | 2-3h | Moyen (async, V4L2) |
| 2. Subscription D-Bus | 2h | Moyen (D-Bus async) |
| 3. Rendu preview | 3-4h | Complexe (dessin GPU) |
| 4. Intégration | 2h | Moyen (testing) |
| **Total** | **9-11h** | Faisable en 1-2 jours |

---

## 🛠️ Commandes Utiles

### D-Bus

```bash
# Voir tous les signaux
dbus-monitor --system
dbus-monitor --session

# Appeler méthode D-Bus
busctl call com.linuxhello.FaceAuth /com/linuxhello/FaceAuth \
    com.linuxhello.FaceAuth RegisterFace s '{"user_id": 1000}'

# Inspecter interface
busctl introspect com.linuxhello.FaceAuth /com/linuxhello/FaceAuth
```

### Compilation

```bash
# Build complet
cargo build --release

# Build spécifique
cargo build -p hello_daemon -p linux_hello_config

# Avec logs détaillés
RUST_LOG=debug cargo run -p linux_hello_config
```

### Tests

```bash
# Tous les tests
cargo test --lib

# Tests spécifiques
cargo test -p hello_daemon capture_stream
cargo test -p hello_face_core stub_detector
```

---

## 🎨 Ressources pour Rendu

Pour le rendu de bounding box sur frames RGB:

### Option 1: `pixels` (recommandé)

- ✅ Simple, performant
- ✅ GPU-accelerated
- ✅ Intégration Iced native

```rust
use pixels::Pixels;

let mut pixels = Pixels::new(640, 480, surface)?;
pixels.frame_mut().copy_from_slice(&rgb_data);
// Dessiner box
context.draw_line(x, y, x+w, y, Color::GREEN)?;
// ...
```

### Option 2: `image` crate (fallback)

- ✅ Pure Rust, portable
- ❌ Moins performant

```rust
use image::{RgbImage, Rgb};
let mut img = RgbImage::from_raw(640, 480, rgb_data)?;
// Dessiner box
for x in x1..x2 {
    img.put_pixel(x, y1, Rgb([0, 255, 0]));
}
```

---

## 🚀 Quick Start

Pour démarrer immédiatement:

```bash
# 1. Modifier camera.rs avec streaming
# 2. Ajouter signal D-Bus dans dbus.rs
# 3. Tester avec dbus-monitor

# 4. Ajouter subscription dans main.rs
# 5. Implémenter view_enrollment()

# 6. Tester bout en bout
cargo test --lib && cargo build --release
```

---

## 📌 Points d'Attention

1. **Lifetime D-Bus**: Attention aux async/await, utiliser `.await`
2. **Serialization**: CaptureFrameEvent → JSON → Signal D-Bus
3. **Threading**: GUI thread (Iced) vs D-Bus thread (tokio)
4. **Performance**: Ne pas bloquer GUI pendant capture
5. **Erreurs**: Gérer déconnexion D-Bus, caméra non-disponible

---

## ✅ Checklist Implémentation

- [ ] Phase 1: Daemon streaming OK
  - [ ] CameraManager.start_capture_stream() ajouté
  - [ ] Détecteur intégré
  - [ ] Tests manual avec dbus-monitor
  
- [ ] Phase 2: Subscription D-Bus OK
  - [ ] Connection D-Bus établie
  - [ ] Signal reçu et parsé
  - [ ] Message affichable
  
- [ ] Phase 3: Rendu OK
  - [ ] Frames affichées
  - [ ] Bounding box visibles
  - [ ] Barre progression fonctionne
  
- [ ] Phase 4: Intégration OK
  - [ ] Boutons fonctionnent
  - [ ] Enregistrement complet
  - [ ] Gestion erreurs

---

**Date**: 7 janvier 2026
**Responsable**: Implementation Phase 2-4
**Dépend de**: Compilation réussie + Tests passants ✅
