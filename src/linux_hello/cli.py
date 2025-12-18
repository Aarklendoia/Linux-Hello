import getpass
import os

import click
import cv2
import insightface
import numpy as np

from .doctor import main as doctor_main
from .select_camera import select_camera as select_camera_fn
from .enroll import enroll as enroll_fn
from .i18n import _

FACE_DIR = "/var/lib/linux-hello/faces"
DEVICE = "/dev/video0"

@click.group()
def cli():
    pass

def load_model():
    model = insightface.app.FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"]
    )
    model.prepare(ctx_id=0)
    return model

@cli.command()
def add():
    """Register a face"""
    username = getpass.getuser()
    model = load_model()

    cap = cv2.VideoCapture(DEVICE)
    ret, frame = cap.read()
    cap.release()

    faces = model.get(frame)
    if not faces:
        click.echo(_("No face detected"))
        return

    embedding = faces[0].embedding
    path = os.path.join(FACE_DIR, f"{username}.npy")
    np.save(path, embedding)

    click.echo(_("✅ Embedding saved for %s") % username)

@cli.command()
def test():
    """Test recognition"""
    username = getpass.getuser()
    path = os.path.join(FACE_DIR, f"{username}.npy")

    if not os.path.exists(path):
        click.echo(_("No embedding registered"))
        return

    saved = np.load(path)
    model = load_model()

    cap = cv2.VideoCapture(DEVICE)
    ret, frame = cap.read()
    cap.release()

    faces = model.get(frame)
    if not faces:
        click.echo(_("No face detected"))
        return

    live = faces[0].embedding
    sim = np.dot(live, saved) / (np.linalg.norm(live) * np.linalg.norm(saved))

    click.echo(_("Similarity: %.3f") % sim)
    click.echo(_("✅ Recognized") if sim > 0.35 else _("❌ Not recognized"))

@cli.command()
def list():
    """List registered embeddings"""
    for f in os.listdir(FACE_DIR):
        if f.endswith(".npy"):
            click.echo(f[:-4])

@cli.command()
@click.argument("username")
def remove(username):
    """Remove a user"""
    path = os.path.join(FACE_DIR, f"{username}.npy")
    if os.path.exists(path):
        os.remove(path)
        click.echo(_("✅ Deleted: %s") % username)
    else:
        click.echo(_("User not found"))

@cli.command()
def doctor():
    """Diagnose Linux Hello installation."""
    doctor_main()

@cli.command()
def select_camera():
    """Select camera for recognition."""
    select_camera_fn()

@cli.command()
def enroll():
    """Register your face for authentication."""
    enroll_fn()

def main():
    cli()

