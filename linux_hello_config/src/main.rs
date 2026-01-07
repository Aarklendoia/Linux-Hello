//! Linux Hello - Configuration GUI pour KDE/Wayland
//!
//! Interface graphique pour:
//! - Enregistrement de visage avec preview en direct
//! - Configuration des paramètres d'authentification
//! - Gestion des visages enregistrés

use iced::widget::{Container, Row, Text};
use iced::{executor, Application, Command, Element, Length};

mod config;
mod dbus_client;
mod preview;
mod streaming;
mod ui;

use streaming::CaptureFrame;
use ui::Screen;

pub fn main() -> iced::Result {
    LinuxHelloConfig::run(Default::default())
}

/// Application principale
struct LinuxHelloConfig {
    current_screen: Screen,
    current_frame: Option<CaptureFrame>,
    frame_count: u32,
    total_frames: u32,
    capture_active: bool,
}

#[derive(Debug, Clone)]
enum Message {
    // Navigation
    GoToHome,
    GoToEnroll,
    GoToSettings,
    GoToManageFaces,

    // Enrollment
    StartCapture,
    StopCapture,
    FrameCaptured(Vec<u8>),

    // D-Bus Streaming
    CaptureProgressReceived(String), // JSON event from daemon
    CaptureCompleted(u32),           // user_id
    CaptureError(String),            // error message

    // Settings
    SettingChanged(String, String),

    // General
    WindowClosed,
}

impl Application for LinuxHelloConfig {
    type Message = Message;
    type Executor = executor::Default;
    type Theme = iced::Theme;
    type Flags = ();

    fn new(_flags: ()) -> (Self, Command<Message>) {
        (
            Self {
                current_screen: Screen::Home,
                current_frame: None,
                frame_count: 0,
                total_frames: 0,
                capture_active: false,
            },
            Command::none(),
        )
    }

    fn title(&self) -> String {
        "Linux Hello - Configuration".to_string()
    }

    fn update(&mut self, message: Message) -> Command<Message> {
        match message {
            Message::GoToHome => {
                self.current_screen = Screen::Home;
                self.capture_active = false;
            }
            Message::GoToEnroll => {
                self.current_screen = Screen::Enrollment;
            }
            Message::GoToSettings => {
                self.current_screen = Screen::Settings;
            }
            Message::GoToManageFaces => {
                self.current_screen = Screen::ManageFaces;
            }
            Message::StartCapture => {
                self.capture_active = true;
                self.frame_count = 0;
                self.total_frames = 30;
                // TODO: Lancer la capture via D-Bus
            }
            Message::StopCapture => {
                self.capture_active = false;
                // TODO: Arrêter la capture
            }
            Message::FrameCaptured(_data) => {
                // TODO: Afficher la frame
            }
            Message::CaptureProgressReceived(json) => {
                // Parser le JSON et mettre à jour current_frame
                if let Ok(frame) = serde_json::from_str::<CaptureFrame>(&json) {
                    self.frame_count = frame.frame_number + 1;
                    self.total_frames = frame.total_frames;
                    self.current_frame = Some(frame);
                }
            }
            Message::CaptureCompleted(user_id) => {
                tracing::info!("Capture complétée pour user_id={}", user_id);
                self.capture_active = false;
            }
            Message::CaptureError(err) => {
                tracing::error!("Erreur capture: {}", err);
                self.capture_active = false;
            }
            Message::SettingChanged(_key, _value) => {
                // TODO: Sauvegarder le paramètre
            }
            Message::WindowClosed => {
                // TODO: Cleanup
            }
        }
        Command::none()
    }

    fn view(&self) -> Element<Message> {
        let content = match self.current_screen {
            Screen::Home => self.view_home(),
            Screen::Enrollment => self.view_enrollment(),
            Screen::Settings => self.view_settings(),
            Screen::ManageFaces => self.view_manage_faces(),
        };

        Container::new(content)
            .width(Length::Fill)
            .height(Length::Fill)
            .center_x()
            .center_y()
            .into()
    }

    fn subscription(&self) -> iced::Subscription<Message> {
        // TODO: S'abonner aux signaux D-Bus pour les frames
        iced::Subscription::none()
    }
}

impl LinuxHelloConfig {
    fn view_home(&self) -> Element<Message> {
        Row::new()
            .push(
                Container::new(Text::new("Accueil"))
                    .width(Length::Fill)
                    .center_x(),
            )
            .into()
    }

    fn view_enrollment(&self) -> Element<Message> {
        Row::new()
            .push(
                Container::new(Text::new("Enregistrement"))
                    .width(Length::Fill)
                    .center_x(),
            )
            .into()
    }

    fn view_settings(&self) -> Element<Message> {
        Row::new()
            .push(
                Container::new(Text::new("Paramètres"))
                    .width(Length::Fill)
                    .center_x(),
            )
            .into()
    }

    fn view_manage_faces(&self) -> Element<Message> {
        Row::new()
            .push(
                Container::new(Text::new("Gérer les visages"))
                    .width(Length::Fill)
                    .center_x(),
            )
            .into()
    }
}
