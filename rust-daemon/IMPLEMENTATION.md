# Rust Daemon Implementation Progress

## ✅ Completed (Phase 1 + Phase 2)

### Architecture & Foundation
- [x] Project structure with Tokio async runtime
- [x] Modular design (config, camera, embeddings, socket)
- [x] Configuration management (JSON load/save)
- [x] Unix socket server with async request handling

### Embeddings Engine (Partial)
- [x] Cosine similarity calculation (linear algebra)
- [x] Threshold matching logic
- [x] Placeholder for ONNX model loading
- [x] Model path management
- [ ] **TODO**: Integrate actual ONNX Runtime (ort-rs)

### Camera Module (Stub)
- [x] Camera device detection
- [x] Frame structure definition
- [x] Placeholder frame processing (resize, to_rgb)
- [ ] **TODO**: Implement actual v4l2 or ffmpeg capture

### Socket Protocol
- [x] JSON RPC request/response
- [x] Async connection handling (Tokio)
- [x] Action dispatching (authenticate, status, enroll)
- [x] Error handling and logging

### Status Request
- [x] Returns daemon version, threshold, model path
- [x] Checks if ONNX model exists
- [x] Reports camera device

## 📋 Next Steps (Phase 3-5)

### Phase 3: ONNX Model Integration

1. **Export InsightFace to ONNX** (external step)
   ```bash
   # Created: /home/ebiton/Linux-Hello/export_onnx.py
   # Run: ./export_onnx.py
   # Output: /opt/linux-hello/models/recognition.onnx
   ```

2. **Integrate ort-rs in daemon**
   ```rust
   // In embeddings/mod.rs
   use ort::{Environment, SessionBuilder};
   
   pub struct Embeddings {
       session: ort::Session,
       threshold: f32,
   }
   ```

3. **Implement compute_embedding()**
   ```rust
   pub fn compute_embedding(&self, image_array: &ndarray::Array3<u8>) -> Result<Array1<f32>> {
       let input = ort::inputs![image_array]?;
       let outputs = self.session.run(input)?;
       Ok(outputs[0].try_extract_tensor()?)
   }
   ```

### Phase 4: Camera Capture & Image I/O

**Option A: ffmpeg (lightweight)**
- Use `ffmpeg -f v4l2 -i /dev/video0` as subprocess
- Parse raw frames via stdout
- Pros: Minimal dependencies, works well
- Cons: External process, slower

**Option B: v4l2-sys binding**
- Direct v4l2 ioctl system calls
- Pros: Fast, native
- Cons: Requires libclang at compile-time

**Option C: gstreamer**
- More modern video framework
- Pros: Flexible, maintained
- Cons: Heavier dependencies

**Recommended**: Start with Option A (subprocess ffmpeg)

Implementation:
```rust
// In camera/mod.rs
use std::process::{Command, Stdio};

pub fn capture_frame(&self) -> Result<Frame> {
    let child = Command::new("ffmpeg")
        .args(&["-f", "v4l2", "-i", "/dev/video0", 
                "-frames", "1", "-f", "rawvideo", "-"])
        .stdout(Stdio::piped())
        .spawn()?;
    
    // Read RGB frame from stdout
    let output = child.wait_with_output()?;
    // Parse into Frame struct
}
```

### Phase 5: User Embedding Storage & Comparison

**Storage Structure**:
```
~/.linux-hello/faces/
├── john/
│   ├── embedding_001.npy  (numpy binary format)
│   ├── embedding_002.npy
│   └── embedding_003.npy
└── jane/
    ├── embedding_001.npy
    └── embedding_002.npy
```

**Authentication Flow**:
```rust
// In socket/mod.rs authenticate_user()

1. Capture frame from camera
   let frame = camera.capture_frame()?;

2. Convert to embedding
   let live_embedding = embeddings.compute_embedding(&frame)?;

3. Load all user embeddings from disk
   let user_embeddings = load_user_embeddings(username)?;

4. Compare similarities
   let similarities: Vec<f32> = user_embeddings
       .iter()
       .map(|emb| Embeddings::cosine_similarity(&live_embedding, emb))
       .collect();

5. Find best match
   let best_similarity = similarities.iter().copied().fold(f32::NEG_INFINITY, f32::max);

6. Return result
   if embeddings.matches_threshold(best_similarity) {
       return Ok(json!({"status": "OK", "similarity": best_similarity}))
   }
```

## 📦 Implementation Details

### Testing Strategy
```bash
# Unit tests for embeddings
cargo test embeddings

# Unit tests for socket protocol
cargo test socket

# Integration test (requires ONNX model)
cargo test --test integration

# Manual test with PAM module
# (After full implementation)
```

### Performance Targets
| Operation | Target | Notes |
|-----------|--------|-------|
| ONNX model load | < 2s | Once at daemon startup |
| Frame capture | 30-50ms | v4l2 or ffmpeg |
| Embedding extract | 50-100ms | ONNX inference |
| Similarity compare | < 1ms | NumPy-like operations |
| **Total latency** | **100-200ms** | vs Python 200-300ms |

### Error Handling
```rust
// All operations should handle:
- Camera not available (NO_CAMERA)
- No face in frame (NO_FACE)
- ONNX model not found (MODEL_NOT_FOUND)
- User has no embeddings (NO_USER_FACES)
- Socket communication errors (SOCKET_ERROR)

// Response format:
{
    "status": "ERROR" | "OK" | "FAIL",
    "code": "NO_CAMERA" | ...,
    "message": "...",
    "similarity": 0.42  (optional)
}
```

## 🔄 Current Status

**Compilation**: ✅ Success (13 warnings, all non-critical)
**Unit tests**: ✅ 4/4 passing
- `cosine_similarity_identical`
- `cosine_similarity_orthogonal` 
- `threshold_matching`
- `status_request`

**Next milestone**: Export ONNX model and integrate ort-rs

## 📌 Build & Run

```bash
# Check compilation
cd /home/ebiton/Linux-Hello/rust-daemon
cargo check

# Build binary
cargo build --release
# Binary: target/release/linux-hello-daemon

# Run daemon
RUST_LOG=info ./target/release/linux-hello-daemon

# Test with PAM module (future)
# PAM will send JSON via /run/linux-hello/daemon.sock
```

## 🚀 Integration with PAM Module

Once complete, the Rust daemon will replace Python daemon:
- Same socket path: `/run/linux-hello/daemon.sock`
- Same JSON RPC protocol
- Backward compatible with existing PAM module
- **No changes needed to pam_module/src/lib.rs**

---

**Branch**: `rust/daemon-onnx`
**Status**: Pre-alpha (architecture complete, core features in progress)
