import warnings
import insightface
import numpy as np
from skimage import transform as trans

# Patch the deprecated method in face_align module
import insightface.utils.face_align as face_align_module

original_estimate_norm = face_align_module.estimate_norm

def patched_estimate_norm(landmark, image_size=112, mode='arcface'):
    """Patched version using the new SimilarityTransform.from_estimate method"""
    assert isinstance(image_size, int)
    assert image_size >= 112
    assert image_size % 112 == 0 or image_size % 128 == 0
    if mode == 'arcface':
        s = image_size*0.5
        a = image_size*0.4
    elif mode == 'mobileface':
        s = image_size*0.5
        a = image_size*0.3
    else:
        s = image_size
        a = image_size
    
    arcface_dst = np.array(
        [[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366],
         [41.5493, 92.3655], [70.7299, 92.2041]],
        dtype=np.float32)
    arcface_dst *= s
    arcface_dst -= 48
    arcface_dst += a / 2
    arcface_dst = arcface_dst.astype(np.float32)

    ratio = float(image_size)/128.0
    diff_x = 8.0*ratio
    dst = arcface_dst * ratio
    dst[:,0] += diff_x
    
    # Use the new method instead of the deprecated one
    tform = trans.SimilarityTransform.from_estimate(landmark, dst)
    M = tform.params[0:2, :]
    return M

# Apply the patch
face_align_module.estimate_norm = patched_estimate_norm

_model = None

def get_model():
    global _model
    if _model is None:
        _model = insightface.app.FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )
        _model.prepare(ctx_id=0)
    return _model

def get_embedding(frame):
    model = get_model()
    faces = model.get(frame)

    if not faces:
        return None

    emb = faces[0].embedding
    # Normalisation
    emb = emb / np.linalg.norm(emb)
    return emb