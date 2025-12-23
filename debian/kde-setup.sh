#!/bin/bash
# Linux Hello - KDE Integration Setup Script
# Configures PAM module for optimal KDE experience

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Linux Hello - KDE Desktop Integration Setup               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if running on KDE
DESKTOP=$(echo $XDG_CURRENT_DESKTOP | tr '[:upper:]' '[:lower:]')
if [[ ! "$DESKTOP" =~ "kde" && ! "$DESKTOP" =~ "plasma" ]]; then
    echo "⚠️  Warning: Not running on KDE Desktop"
    echo "   Current desktop: $XDG_CURRENT_DESKTOP"
    echo "   This script is optimized for KDE but should work on GNOME/XFCE too."
    echo ""
fi

echo "📋 Checking dependencies..."
echo ""

# Check KDE tools
if command -v kdialog >/dev/null 2>&1; then
    echo "✓ kdialog found (KDE native dialogs)"
else
    echo "⚠ kdialog not found - installing..."
    sudo apt-get update
    sudo apt-get install -y kde-baseapps
fi

# Check Zenity (fallback)
if command -v zenity >/dev/null 2>&1; then
    echo "✓ zenity found (GNOME fallback)"
else
    echo "⚠ zenity not found - installing..."
    sudo apt-get install -y zenity
fi

# Check D-Bus
if command -v dbus-send >/dev/null 2>&1; then
    echo "✓ D-Bus found (notifications)"
else
    echo "⚠ D-Bus not found - installing..."
    sudo apt-get install -y dbus
fi

# Check Python+PySide6
if python3 -c "import PySide6" 2>/dev/null; then
    echo "✓ PySide6 found (fallback GUI)"
else
    echo "⚠ PySide6 not found - installing..."
    sudo apt-get install -y python3-pyside6
fi

echo ""
echo "📦 Verifying PAM module..."

if [ ! -f /lib/x86_64-linux-gnu/security/pam_linux_hello.so ]; then
    echo "❌ PAM module not found!"
    echo "   Install the linux-hello package first:"
    echo "   sudo dpkg -i linux-hello_1.0.0_all.deb"
    exit 1
fi

echo "✓ PAM module found"
echo ""

echo "🔧 Activating PAM services..."
echo ""

# Get list of services
SERVICES=""
for service in sudo login sshd gdm-password lightdm cups; do
    if [ -f /etc/pam.d/$service ]; then
        SERVICES="$SERVICES $service"
    fi
done

echo "Available services: $SERVICES"
echo ""
echo "Which services should use face recognition?"
echo "(Enter service names separated by spaces, or 'all' for all available)"
echo ""

read -p "Services [sudo]: " input_services
SELECTED_SERVICES=${input_services:-sudo}

if [ "$SELECTED_SERVICES" = "all" ]; then
    SELECTED_SERVICES=$SERVICES
fi

echo ""
for service in $SELECTED_SERVICES; do
    if [ -f /etc/pam.d/$service ]; then
        echo "🔐 Activating for $service..."
        sudo /usr/lib/linux-hello/enable-pam-face-recognition.sh $service
    else
        echo "⚠ Service $service not found (skipping)"
    fi
done

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Module:        /lib/x86_64-linux-gnu/security/pam_linux_hello.so"
echo "  Helper:        /usr/lib/linux-hello/linux-hello-pam-confirm.py"
echo "  Activation:    /usr/lib/linux-hello/enable-pam-face-recognition.sh"
echo ""
echo "  Desktop:       $XDG_CURRENT_DESKTOP"
echo "  Preference:    kdialog (KDE) → zenity (GNOME) → PySide6 (fallback)"
echo "  Notifications: D-Bus system notifications"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🧪 Test the module:"
echo ""
echo "   sudo pamtester sudo \$USER authenticate"
echo ""
echo "🔍 View logs:"
echo ""
echo "   sudo journalctl -u pam_linux_hello -f"
echo ""
echo "📚 Documentation:"
echo ""
echo "   /home/ebiton/Linux-Hello/pam_module/KDE_INTEGRATION.md"
echo ""
