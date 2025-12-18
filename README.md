# Linux Hello 🔐

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-GPL3-green)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Ubuntu](https://img.shields.io/badge/ubuntu-20.04+-orange)

**Linux Hello** is a secure, AI-powered facial authentication system for Linux. It integrates seamlessly with PAM (Pluggable Authentication Modules) to enable biometric login and sudo authentication using face recognition.

## ✨ Features

- 🎯 **Accurate Face Recognition** - Uses InsightFace deep learning model for reliable identification
- 🔐 **PAM Integration** - Seamless integration with system authentication
- 🌍 **Multi-language Support** - 10 languages: English, Français, Español, Deutsch, Italiano, Português, Русский, 日本語, 中文, العربية
- 📷 **Multi-camera Support** - Automatic detection and selection of cameras
- 🔧 **System Diagnostics** - Built-in health check for troubleshooting
- 🚀 **Daemon Mode** - Background service with systemd integration
- 💾 **Secure Storage** - Facial embeddings stored securely with proper permissions

## 📋 Requirements

- **OS**: Ubuntu 20.04 LTS or later (Debian-based Linux)
- **Python**: 3.12+
- **Camera**: USB or integrated webcam
- **Disk Space**: ~2GB for dependencies
- **RAM**: 4GB minimum

## 🚀 Installation

### From Debian Package (Recommended)

```bash
sudo dpkg -i linux-hello_1.0.0_all.deb
sudo systemctl start linux-hello
```

### From Source

```bash
git clone https://github.com/yourusername/linux-hello.git
cd linux-hello
sudo dpkg-buildpackage -us -uc
sudo dpkg -i ../linux-hello_1.0.0_all.deb
```

## 📖 Usage

### Quick Start

```bash
# Register your face
sudo hello add myusername

# Test recognition
sudo hello test myusername

# List all users
hello list

# View diagnostics
hello doctor
```

### Available Commands

| Command | Description |
|---------|-------------|
| `hello add USER` | Register a new user's face |
| `hello test USER` | Test face recognition for a user |
| `hello list` | Show all registered users |
| `hello remove USER` | Delete a user's face data |
| `hello doctor` | Run system health diagnostics |
| `hello select-camera` | Configure default camera |
| `hello enroll USER` | Alias for `add USER` |

## 🌍 Internationalization

Set the `LANG` environment variable to use different languages:

```bash
# French
LANG=fr_FR.UTF-8 hello doctor

# Spanish
LANG=es_ES.UTF-8 hello doctor

# German
LANG=de_DE.UTF-8 hello doctor

# Japanese
LANG=ja_JP.UTF-8 hello doctor

# Arabic
LANG=ar_AR.UTF-8 hello doctor

# And more: English, Italian, Portuguese, Russian, Chinese
```

## 🔐 PAM Integration

### Enable for Login

Edit `/etc/pam.d/login`:

```bash
sudo nano /etc/pam.d/login
```

Add this line **before** the `pam_unix.so` line:

```
auth    sufficient    pam_exec.so quiet stdout /usr/lib/linux-hello/pam_linux_hello.py
```

Now login using facial recognition!

### Enable for Sudo

Edit `/etc/pam.d/sudo`:

```bash
sudo nano /etc/pam.d/sudo
```

Add the same line at the top:

```
auth    sufficient    pam_exec.so quiet stdout /usr/lib/linux-hello/pam_linux_hello.py
```

### Disable (Revert)

Simply remove the lines added to PAM configuration files:

```bash
sudo nano /etc/pam.d/login
# Remove: auth    sufficient    pam_exec.so quiet stdout /usr/lib/linux-hello/pam_linux_hello.py
```

## 🔧 Configuration

### Configuration Directory
```
/etc/linux-hello/
```

### Face Data Directory
```
/var/lib/linux-hello/faces/
```

### Service Control

```bash
# Start the service
sudo systemctl start linux-hello

# Stop the service
sudo systemctl stop linux-hello

# Enable on boot
sudo systemctl enable linux-hello

# View logs
journalctl -u linux-hello -f

# Check status
systemctl status linux-hello
```

## 🏥 Diagnostics

Run the health check:

```bash
hello doctor
```

Output example:
```
=== Linux Hello Doctor ===
→ Venv present… OK
→ Python in venv present… OK
→ InsightFace importable… OK
→ Daemon active… OK
→ Unix socket present… OK
→ Camera accessible… OK
→ Registered faces… OK

Diagnosis complete.
```

## 📷 Camera Selection

If multiple cameras are available, select the default one:

```bash
hello select-camera
```

The selection is saved to `/etc/linux-hello/config.json`

## 🐛 Troubleshooting

### "Camera inaccessible"
- Check if camera is connected: `ls -la /dev/video*`
- Verify permissions: `sudo usermod -aG video $USER`
- Restart the session for permissions to apply

### "InsightFace not importable"
- Run: `hello doctor`
- Reinstall venv: `sudo /usr/lib/linux-hello/repair_venv.sh`

### "Daemon not active"
- Check status: `systemctl status linux-hello`
- View logs: `journalctl -u linux-hello`
- Restart: `sudo systemctl restart linux-hello`

### "Socket missing"
- Ensure daemon is running: `sudo systemctl start linux-hello`
- Check socket: `ls -la /run/linux-hello.sock`

## 📊 System Architecture

```
┌─────────────────────┐
│  CLI Interface      │  hello add/test/list/doctor
│  (Click Framework)  │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  i18n Module        │  10 Languages Support
│  (gettext)          │
└──────────┬──────────┘
           │
┌──────────▼──────────────┐
│  Face Recognition       │  InsightFace buffalo_l
│  (InsightFace + ONNX)   │  Embeddings storage
└──────────┬──────────────┘
           │
┌──────────▼──────────┐
│  Daemon Service     │  SystemD integration
│  Unix Socket        │  Background processing
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  PAM Module         │  System authentication
│  Login/Sudo         │  pam_exec integration
└─────────────────────┘
```

## 🔄 Development

### Building from Source

```bash
# Install build dependencies
sudo apt install build-essential debhelper python3-pip

# Clone and build
git clone https://github.com/yourusername/linux-hello.git
cd linux-hello
sudo dpkg-buildpackage -us -uc

# Install
sudo dpkg -i ../linux-hello_1.0.0_all.deb
```

### Project Structure

```
linux-hello/
├── src/linux_hello/          # Python source code
│   ├── cli.py               # Click CLI interface
│   ├── doctor.py            # System diagnostics
│   ├── daemon.py            # Background service
│   ├── auth.py              # Authentication logic
│   ├── camera.py            # Camera interface
│   ├── embeddings.py        # Face embeddings
│   ├── i18n.py              # Internationalization
│   └── select_camera.py      # Camera selection
├── debian/                   # Debian packaging
│   ├── rules                # Build rules
│   ├── control              # Package metadata
│   ├── postinst             # Post-install script
│   ├── prerm                # Pre-removal script
│   └── linux-hello.1        # Man page
├── po/                      # Translation files
│   ├── linux-hello.pot      # Translation template
│   ├── fr.po, de.po, ...    # Language-specific translations
│   └── *.mo                 # Compiled translations
└── usr/                     # System files
    ├── bin/                 # Executables
    └── lib/linux-hello/     # Helper scripts & modules
```

## 📝 Translation Guide

To add a new language:

1. Create translation file:
```bash
cp po/linux-hello.pot po/NEW_LANG.po
# Edit po/NEW_LANG.po with translations
```

2. Compile:
```bash
msgfmt po/NEW_LANG.po -o po/NEW_LANG.mo
```

3. Update `debian/rules` to include new language

4. Rebuild package:
```bash
dpkg-buildpackage -us -uc
```

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

- 📖 Check the [man page](debian/linux-hello.1): `man linux-hello`
- 🔍 Run diagnostics: `hello doctor`
- 📋 View logs: `journalctl -u linux-hello`
- 🐛 Report issues on GitHub

## 🎯 Roadmap

- [ ] Multi-face anti-spoofing detection
- [ ] Liveness detection
- [ ] Web interface for administration
- [ ] Backup/restore face database
- [ ] Integration with additional biometric modalities
- [ ] Performance optimizations

## 👥 Authors

- Linux Hello Development Team

## ⭐ Acknowledgments

- [InsightFace](https://github.com/deepinsight/insightface) - Deep learning face recognition
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Debian](https://www.debian.org/) - Package management

---

**Made with ❤️ for secure Linux authentication**
