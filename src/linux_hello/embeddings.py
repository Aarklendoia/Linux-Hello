import insightface
import numpy as np

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