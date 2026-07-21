from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from . import models, schemas

def create_note(db: Session, data: schemas.NoteCreate) -> models.Note:
    note = models.Note(title=data.title, body=data.body, tags=data.tags)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_note(db: Session, note_id: int) -> models.Note | None:
    return db.get(models.Note, note_id)


def list_notes(db: Session) -> list[models.Note]:
    return (
        db.query(models.Note)
        .order_by(models.Note.updated_at.desc())
        .all()
    )


def update_note(
    db: Session, note: models.Note, data: schemas.NoteUpdate
) -> models.Note:
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note: models.Note) -> None:
    db.delete(note)
    db.commit()


def search_notes(
    db: Session, q: str | None = None, tag: str | None = None
) -> list[models.Note]:
    query = db.query(models.Note)

    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            or_(
                func.lower(models.Note.title).like(like),
                func.lower(models.Note.body).like(like),
            )
        )

    notes = query.order_by(models.Note.updated_at.desc()).all()

    if tag:
        wanted = tag.strip().lower()
        notes = [n for n in notes if wanted in (n.tags or [])]

    return notes
