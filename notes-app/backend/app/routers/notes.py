from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..auth import require_api_key
from ..database import get_db

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    dependencies=[Depends(require_api_key)],
    responses={
        401: {"model": schemas.ErrorResponse, "description": "Missing key"},
        403: {"model": schemas.ErrorResponse, "description": "Invalid key"},
    },
)


@router.get(
    "/search",
    response_model=list[schemas.NoteOut],
    summary="Search notes by keyword and/or tag",
)
def search_notes(
    q: str | None = Query(
        default=None, description="Keyword matched against title and body"
    ),
    tag: str | None = Query(default=None, description="Exact tag to filter by"),
    db: Session = Depends(get_db),
):
    if not q and not tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one of 'q' or 'tag'.",
        )
    return crud.search_notes(db, q=q, tag=tag)


@router.get("", response_model=list[schemas.NoteOut], summary="List all notes")
def list_notes(db: Session = Depends(get_db)):
    return crud.list_notes(db)


@router.post(
    "",
    response_model=schemas.NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
)
def create_note(payload: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db, payload)


@router.get(
    "/{note_id}",
    response_model=schemas.NoteOut,
    summary="Get one note",
    responses={404: {"model": schemas.ErrorResponse}},
)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note {note_id} not found.",
        )
    return note


@router.put(
    "/{note_id}",
    response_model=schemas.NoteOut,
    summary="Update a note..",
    responses={404: {"model": schemas.ErrorResponse}},
)
def update_note(
    note_id: int,
    payload: schemas.NoteUpdate,
    db: Session = Depends(get_db),
):
    note = crud.get_note(db, note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note {note_id} not found...",
        )
    return crud.update_note(db, note, payload)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note..",
    responses={404: {"model": schemas.ErrorResponse}},
)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note {note_id} not found...",
        )
    crud.delete_note(db, note)
    return None
