//! Button builder with state-aware styling

use crate::button_state::ButtonState;
use crate::Message;
use iced::widget::{Button, Text};
use iced::{Element, Length};

/// Build a styled button with state-aware effects
pub fn styled_button<'a>(
    _button_id: &'a str,
    label: &'a str,
    _state: ButtonState,
    on_press: Option<Message>,
) -> Element<'a, Message> {
    // For now, create a simple button with optional message
    let button = match on_press {
        Some(msg) => Button::new(Text::new(label))
            .on_press(msg)
            .padding(10)
            .width(Length::Fill),
        None => Button::new(Text::new(label))
            .padding(10)
            .width(Length::Fill),
    };

    // TODO: Apply opacity and scale based on button state
    // Currently buttons are not interactive from UI perspective

    button.into()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_button_opacity_value() {
        let opacity_normal = ButtonState::Normal.opacity();
        let opacity_hover = ButtonState::Hover.opacity();
        let opacity_pressed = ButtonState::Pressed.opacity();
        let opacity_disabled = ButtonState::Disabled.opacity();

        assert!(opacity_normal < opacity_hover);
        assert!(opacity_pressed < opacity_normal);
        assert!(opacity_disabled < opacity_pressed);
    }

    #[test]
    fn test_button_scale_value() {
        let scale_normal = ButtonState::Normal.scale();
        let scale_hover = ButtonState::Hover.scale();
        let scale_pressed = ButtonState::Pressed.scale();

        assert!(scale_normal < scale_hover);
        assert!(scale_pressed < scale_normal);
    }
}
