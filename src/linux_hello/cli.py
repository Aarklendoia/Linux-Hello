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

def translated_command(name=None, **kwargs):
    """Decorator that translates the docstring for help text and adds to cli group"""
    def decorator(f):
        # Translate the docstring if it exists
        if f.__doc__:
            kwargs['help'] = _(f.__doc__.strip())
        return cli.command(name, **kwargs)(f)
    return decorator

def get_faces_dir():
    """Get user-specific faces directory"""
    home = os.path.expanduser("~")
    faces_dir = os.path.join(home, ".linux-hello", "faces")
    os.makedirs(faces_dir, exist_ok=True)
    return faces_dir

DEVICE = "/dev/video0"

def require_non_root():
    """Check that command is not run as root"""
    if os.geteuid() == 0:
        click.echo(_("❌ This command cannot be run as root."))
        click.echo(_("Please run as a regular user."))
        raise SystemExit(1)

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

@translated_command()
def test():
    """Test recognition"""
    require_non_root()
    username = getpass.getuser()
    faces_dir = get_faces_dir()
    path = os.path.join(faces_dir, f"{username}.npy")

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

@translated_command()
def list():
    """List registered embeddings"""
    faces_dir = get_faces_dir()
    for f in os.listdir(faces_dir):
        if f.endswith(".npy"):
            click.echo(f[:-4])

@translated_command()
@click.argument("username")
def remove(username):
    """Remove a user"""
    faces_dir = get_faces_dir()
    path = os.path.join(faces_dir, f"{username}.npy")
    if os.path.exists(path):
        os.remove(path)
        click.echo(_("✅ Deleted: %s") % username)
    else:
        click.echo(_("User not found"))

@translated_command()
def doctor():
    """Diagnose Linux Hello installation."""
    doctor_main()

@translated_command()
def select_camera():
    """Select camera for recognition."""
    select_camera_fn()

@translated_command()
def enroll():
    """Register your face for authentication."""
    require_non_root()
    enroll_fn()

def main():
    cli()

