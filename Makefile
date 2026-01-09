.PHONY: build test release check clean help install-pam debian deb-build fmt lint audit docs dev-setup

help:
	@echo "Linux Hello - Makefile commands"
	@echo ""
	@echo "Development:"
	@echo "  make build       - Build in debug mode"
	@echo "  make release     - Build optimized release"
	@echo "  make test        - Run all unit tests"
	@echo "  make check       - Run cargo check (fast)"
	@echo "  make fmt         - Format code (cargo fmt)"
	@echo "  make lint        - Check code style (cargo clippy)"
	@echo "  make audit       - Check for security vulnerabilities"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make docs        - Build documentation"
	@echo ""
	@echo "Debian Packaging:"
	@echo "  make debian      - Build Debian packages"
	@echo "  make deb-clean   - Clean Debian build artifacts"
	@echo "  make deb-install - Build and install packages (sudo)"
	@echo ""
	@echo "Testing:"
	@echo "  make daemon      - Run daemon in debug mode"
	@echo "  make camera-test - Test camera capture"
	@echo "  make install-pam - Install PAM module (sudo)"
	@echo ""
	@echo "Setup:"
	@echo "  make dev-setup   - Install development dependencies"
	@echo ""

build:
	cargo build --all

release:
	cargo build --all --release

test:
	cargo test --all --lib

check:
	cargo check --all

clean:
	cargo clean

fmt:
	cargo fmt --all

lint:
	cargo clippy --all -- -D warnings

audit:
	cargo audit

docs:
	cargo doc --no-deps --all --open

debian:
	dpkg-buildpackage -us -uc -b

deb-clean:
	rm -rf debian/tmp debian/.debhelper* debian/*.substvars debian/files
	rm -f ../*.deb ../*.buildinfo ../*.changes

deb-install: debian
	sudo dpkg -i ../*.deb

dev-setup:
	@echo "Installing development dependencies..."
	sudo apt-get update
	sudo apt-get install -y \
		build-essential \
		rustc \
		cargo \
		libssl-dev \
		libpam0g-dev \
		pkg-config \
		debhelper \
		devscripts \
		quilt \
		lintian \
		qt6-base-dev \
		qml6-module-qtcore \
		qml6-module-qtquick \
		qml6-module-qtquick-layouts \
		qml6-module-qtquick-controls \
		libkf6kirigami-dev

daemon:
	cargo run --bin hello-daemon

camera-test:
	cargo run --bin hello-camera --release

install-pam:
	sudo bash install-pam.sh

daemon:
cargo run -p linux_hello_cli -- daemon --debug

camera-test:
cargo run -p linux_hello_cli -- camera --duration 5

install-pam: release
@echo "Installing PAM module..."
sudo cp target/release/libpam_linux_hello.so /lib/security/pam_linux_hello.so
@echo "Done! Module installed at /lib/security/pam_linux_hello.so"
