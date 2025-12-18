# Contributing to Linux Hello

Thank you for your interest in contributing to Linux Hello!

## Development Workflow

### 1. Setup Local Development

```bash
git clone https://github.com/yourusername/linux-hello.git
cd linux-hello
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 2. Making Changes

Create a feature branch:
```bash
git checkout -b feature/my-feature
```

Make your changes and test locally:
```bash
# Run CLI commands
hello doctor

# Test in different languages
LANG=fr_FR.UTF-8 hello test

# Check man pages
man linux-hello
```

### 3. Committing Changes

Use conventional commits:
```bash
git commit -m "feat: Add new camera support"
git commit -m "fix: Correct face embedding calculation"
git commit -m "docs: Update installation guide"
git commit -m "test: Add unit tests for authentication"
```

Supported prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvement
- `chore:` - Build, CI/CD

### 4. Creating a Release

Use the semantic versioning helper script:

```bash
# View current version and next versions
./scripts/version.sh show

# Bump patch version (1.0.0 → 1.0.1)
./scripts/version.sh patch

# Bump minor version (1.0.0 → 1.1.0)
./scripts/version.sh minor

# Bump major version (1.0.0 → 2.0.0)
./scripts/version.sh major

# Create a specific version (1.0.0 → 1.5.3)
./scripts/version.sh 1.5.3
```

This will:
1. Create a signed git tag with semantic version
2. Push to GitHub
3. GitHub Actions automatically builds and creates a release

### 5. Automated Build & Release

When you push a tag matching semantic versioning (`1.0.0`, `1.2.3`, etc.):

1. **GitHub Actions triggers** the release workflow
2. **Builds the Debian package** on Ubuntu latest
3. **Creates a GitHub Release** with:
   - Auto-generated release notes
   - Debian package (.deb) attached
   - Signed tag reference

See `.github/workflows/release.yml` for details.

### 6. CI/CD for Every Push

For every push to `main` or `develop`:
- Lint checks run (flake8)
- Package builds successfully
- Syntax verification

See `.github/workflows/ci.yml` for details.

## Package Build Locally

### Prerequisites

```bash
sudo apt-get install build-essential debhelper-compat \
  python3-setuptools python3-setuptools-scm gettext
```

### Build Process

```bash
cd linux-hello
dpkg-buildpackage -us -uc
```

This generates:
- `../linux-hello_*.deb` - Debian package
- `../linux-hello_*.buildinfo` - Build info
- `../linux-hello_*.changes` - Changes file

### Install & Test

```bash
sudo dpkg -i ../linux-hello_1.0.0_all.deb
hello doctor
```

## Version Management

### How Versioning Works

1. **Source of truth**: Git tags (e.g., `1.0.0`, `1.2.3`)
2. **Dynamic version**: setuptools_scm generates version from tags
3. **Development version**: Between tags, versions like `1.0.1.dev0+gabcdef1`
4. **Package version**: Matches the tag when building from tag

### Version Format

Follows **Semantic Versioning 2.0.0**:
```
MAJOR.MINOR.PATCH
 ↓     ↓      ↓
 1  .  2   .  3
```

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes

## Testing

### Manual Testing

```bash
# Test registration
sudo hello add testuser

# Test recognition
sudo hello test testuser

# Test in different languages
LANG=de_DE.UTF-8 hello test testuser
LANG=ja_JP.UTF-8 hello doctor

# View man pages
man linux-hello
man -L fr linux-hello
man -L es linux-hello-daemon
```

### Daemon Testing

```bash
# Start daemon
sudo systemctl start linux-hello

# Check logs
journalctl -u linux-hello -f

# Test daemon health
hello doctor
```

## Documentation

### Code Documentation

- Add docstrings to all functions
- Use type hints in function signatures
- Include examples in docstrings

### Man Pages

Located in `debian/man/{lang}/`:
- `linux-hello.1` - User commands
- `linux-hello-daemon.8` - Daemon administration
- `pam_linux_hello.8` - PAM module

Update all language versions when making changes.

## Translation (i18n)

The project supports 10 languages:
- English (en)
- Français (fr)
- Español (es)
- Deutsch (de)
- Italiano (it)
- Português (pt)
- Русский (ru)
- 日本語 (ja)
- 中文 (zh_CN)
- العربية (ar)

### Adding Translation

1. Edit `po/LANG.po` file
2. Update translation strings
3. Compile: `msgfmt po/LANG.po -o po/LANG.mo`
4. Test: `LANG=LANG_COUNTRY.UTF-8 hello command`

## Code Style

Follow PEP 8 with a 120-character line limit:
```bash
flake8 src/linux_hello --max-line-length=120
```

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0.

## Need Help?

- 📖 Check [README.md](README.md) for usage
- 🐛 Run `hello doctor` for diagnostics
- 📋 View logs: `journalctl -u linux-hello`
- 🔍 Search existing issues on GitHub
- 💬 Open a discussion or issue

---

**Thank you for contributing to Linux Hello! 🎉**
