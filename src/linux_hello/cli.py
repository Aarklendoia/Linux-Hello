import getpass
import os

import click
import cv2
import insightface
import numpy as np

from .doctor import main as doctor_main

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
    """Enregistrer un visage"""
    username = getpass.getuser()
    model = load_model()

    cap = cv2.VideoCapture(DEVICE)
    ret, frame = cap.read()
    cap.release()

    faces = model.get(frame)
    if not faces:
        click.echo("Aucun visage détecté")
        return

    embedding = faces[0].embedding
    path = os.path.join(FACE_DIR, f"{username}.npy")
    np.save(path, embedding)

    click.echo(f"✅ Embedding enregistré pour {username}")

@cli.command()
def test():
    """Tester la reconnaissance"""
    username = getpass.getuser()
    path = os.path.join(FACE_DIR, f"{username}.npy")

    if not os.path.exists(path):
        click.echo("Aucun embedding enregistré")
        return

    saved = np.load(path)
    model = load_model()

    cap = cv2.VideoCapture(DEVICE)
    ret, frame = cap.read()
    cap.release()

    faces = model.get(frame)
    if not faces:
        click.echo("Aucun visage détecté")
        return

    live = faces[0].embedding
    sim = np.dot(live, saved) / (np.linalg.norm(live) * np.linalg.norm(saved))

    click.echo(f"Similarité : {sim:.3f}")
    click.echo("✅ Reconnu" if sim > 0.35 else "❌ Non reconnu")

@cli.command()
def list():
    """Lister les embeddings enregistrés"""
    for f in os.listdir(FACE_DIR):
        if f.endswith(".npy"):
            click.echo(f[:-4])

@cli.command()
@click.argument("username")
def remove(username):
    """Supprimer un utilisateur"""
    path = os.path.join(FACE_DIR, f"{username}.npy")
    if os.path.exists(path):
        os.remove(path)
        click.echo(f"✅ Supprimé : {username}")
    else:
        click.echo("Utilisateur introuvable")

@cli.command()
def doctor():
    """Diagnostique l'installation Linux Hello."""
    doctor_main()

def main():
    cli()
