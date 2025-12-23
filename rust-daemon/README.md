# Linux Hello Daemon - Rust Implementation

**Status**: Exploration branch (`rust/daemon-onnx`)

## Overview

Experimental rewrite of the Linux Hello daemon in Rust with ONNX Runtime for face recognition, replacing the Python + InsightFace stack.

## Architecture

```
+-------+          +------------------+          +----------------+
| PAM   |          | Rust Daemon      |          | ONNX Models    |
| Module| -------> | (Unix Socket)    | -------> | (recognition   |
+-------+          | - Camera         |          |  detection)    |
                   | - Embeddings     |          +----------------+
                   | - Authentication |
                   +------------------+
```

## Modules

### `config.rs`
- Load/save configuration from `~/.linux-hello/config.json`
- Settings: `threshold`, `models_dir`, `camera_device`, `log_level`

### `camera.rs`
- Camera device access (currently: minimal v4l2 check)
- TODO: Full frame capture via v4l2 or OpenCV binding
- Frame preprocessing (resize, normalize)

### `embeddings.rs`
- ONNX Runtime session management
- Embedding computation from image frames
- Cosine similarity matching
- TODO: Load actual ONNX models

### `socket.rs`
- Unix socket server (async with Tokio)
- Request handling: `authenticate`, `status`
- JSON RPC protocol compatible with Python PAM module

## Implementation Roadmap

### Phase 1: Foundation ✅
- [x] Project structure
- [x] Basic Tokio socket server
- [x] Configuration loading
- [x] JSON RPC protocol skeleton
- [ ] Test suite

### Phase 2: ONNX Integration 🔄
- [ ] Export InsightFace model to ONNX
- [ ] Integrate ort-rs (ONNX Runtime)
- [ ] Embedding computation from frames
- [ ] Model caching/lazy loading

### Phase 3: Camera + Image Processing 🔄
- [ ] v4l2 bindings or gphoto2
- [ ] Frame capture and buffering
- [ ] Image preprocessing (resize 512x512, normalize)
- [ ] Face detection model (optional ONNX)

### Phase 4: Storage + Auth 🔄
- [ ] User face embeddings storage (`~/.linux-hello/faces/{user}/`)
- [ ] Embedding comparison logic
- [ ] Authentication decision tree
- [ ] Error handling (no faces, no camera, etc.)

### Phase 5: Testing & Production 🔄
- [ ] Unit tests
- [ ] Integration tests with PAM module
- [ ] Performance benchmarks vs Python
- [ ] Security audit (socket permissions, model loading)

## Dependencies

| Crate | Purpose | Status |
|-------|---------|--------|
| `tokio` | Async runtime | ✅ |
| `serde_json` | JSON RPC | ✅ |
| `ndarray` | Linear algebra | ✅ |
| `ort` | ONNX Runtime | ⏳ Pending |
| `image` | Image codec | ✅ |
| `opencv` | Camera/CV | ❌ Deferred (too heavy) |
| `v4l2-sys` | Direct v4l2 | 📋 Future |

## Building

```bash
cd rust-daemon
cargo build --release
```

Binary: `target/release/linux-hello-daemon`

## Testing

```bash
# Check code
cargo check

# Run tests
cargo test

# Build docs
cargo doc --open
```

## Integration with PAM Module

The Rust daemon is a drop-in replacement for the Python daemon:

```c
// From pam_module/src/lib.rs
send_request_to_daemon(r#"{"action": "authenticate", "user": "john"}"#);
// Expected response:
// {"status": "OK", "message": "...", "user": "john"}
```

Socket path: `/run/linux-hello/daemon.sock`

## Performance Expectations

| Metric | Python | Rust |
|--------|--------|------|
| Binary size | ~200 MB (with deps) | ~15 MB |
| Memory (idle) | ~80 MB | ~5-10 MB |
| Auth latency | 100-200ms | 30-50ms |
| Startup time | ~2s | ~100ms |

## Migration Path

1. **Week 1**: Finish ONNX model export
2. **Week 2**: Implement embeddings + camera I/O
3. **Week 3**: Test + optimize performance
4. **Week 4**: Parallel run with Python daemon, benchmark
5. **Week 5**: Switch default, deprecate Python version

## Known Issues

- ONNX Model export from InsightFace not yet done
- Camera capture logic deferred (complex dependencies)
- No face detection model yet (optional performance feature)
- Async error propagation could be cleaner

## Resources

- [ONNX Runtime Rust](https://github.com/pykeio/ort)
- [InsightFace Export](https://github.com/deepinsight/insightface/issues/3154)
- [Tokio Async Patterns](https://tokio.rs/)

---

**Branch**: `rust/daemon-onnx`  
**Started**: 2025-12-23  
**Experimental**: Do not merge to main
