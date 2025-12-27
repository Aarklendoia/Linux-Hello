# Setup Compilation et Tests - Linux Hello

## ✅ Installation Complète

### Dépendances Système Installées
```bash
✓ python3-dev
✓ python3-pip
✓ python3-setuptools
✓ python3-setuptools-scm
✓ python3-opencv
✓ python3-numpy
✓ rustc 1.85.1
✓ cargo 1.85.1
✓ build-essential
✓ debhelper
✓ dh-python
✓ libpam0g-dev
✓ python3-click
```

### Dépendances Python Installées
```bash
✓ insightface              - Reconnaissance faciale
✓ onnxruntime-cpu         - Exécution de modèles ONNX
✓ numpy                   - Calculs numériques
✓ opencv (python3-opencv) - Traitement d'images
✓ click                   - CLI
✓ pytest                  - Tests unitaires
✓ pytest-cov              - Couverture de tests
```

### Module PAM Compilé
```bash
✓ libpam_linux_hello.so   - 407 KB
  Localisation: pam_module/target/release/libpam_linux_hello.so
  Compilé avec: cargo 1.85.1 (release profile optimisé)
```

### Package Python Installé
```bash
✓ linux-hello 1.0.0.post24+ga2b1de9f4
  Environnement: /home/edtech/Documents/linux-hello/.venv/
  Python: 3.13.7
```

## 🚀 Prêt pour les Tests

### Environnement Python
```bash
# Activer l'environnement virtuel
source /home/edtech/Documents/linux-hello/.venv/bin/activate

# Ou utiliser directement
/home/edtech/Documents/linux-hello/.venv/bin/python
/home/edtech/Documents/linux-hello/.venv/bin/pip
```

### Tests Disponibles
```bash
# Vérifier l'installation complète
/home/edtech/Documents/linux-hello/.venv/bin/python test_pam.py

# Tester le package Python (si des tests existent)
cd /home/edtech/Documents/linux-hello
.venv/bin/python -m pytest

# Utiliser le CLI
.venv/bin/hello --help
.venv/bin/hello doctor
```

### Compilation du Module PAM
```bash
cd /home/edtech/Documents/linux-hello/pam_module
cargo build --release  # Mode optimisé (déjà compilé)
cargo test            # Tests Rust
```

## 📋 Fichiers Importants

### Configuration Build
- `pyproject.toml` - ✅ Corrigé (version_scheme: post-release)
- `setup.py` - Configuration setuptools
- `Makefile` - Actuellement vide

### Module PAM Rust
- `pam_module/Cargo.toml` - Dépendances Rust
- `pam_module/src/lib.rs` - Implémentation PAM
- `pam_module/target/release/libpam_linux_hello.so` - Binaire compilé

### Scripts de Test
- `test_pam.py` - ✅ Créé - Script de vérification d'installation

## 🔧 Dépannage

Si vous avez besoin de réinstaller quelque chose:

```bash
# Venv Python
/home/edtech/Documents/linux-hello/.venv/bin/pip install --upgrade -r requirements.txt

# Module PAM
cd /home/edtech/Documents/linux-hello/pam_module
cargo clean
cargo build --release

# Package principal
cd /home/edtech/Documents/linux-hello
.venv/bin/pip install -e .
```

## 📝 Notes

- ✅ La compilation Rust a produit 16 avertissements sur des constantes non utilisées - c'est normal pour cette version
- ✅ `setuptools_scm` a été configuré avec `version_scheme = "post-release"` au lieu de `guess-next-simple` (obsolète)
- ✅ Le virtualenv Python 3.13.7 est bien configuré
- ✅ Toutes les dépendances critiques pour compilation et test sont installées

## 🎯 Prochaines Étapes

1. **Tester la compilation du binaire debian**:
   ```bash
   cd /home/edtech/Documents/linux-hello
   dpkg-buildpackage -us -uc
   ```

2. **Exécuter les tests de reconnaissance faciale**:
   ```bash
   .venv/bin/hello doctor
   ```

3. **Tester l'intégration PAM** (si cibles test disponibles):
   ```bash
   cd pam_module
   cargo test
   ```
