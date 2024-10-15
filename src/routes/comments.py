from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.repository.comments import (
    create_comment,
    get_comments,
    update_comment,
    delete_comment,
)
from src.schemas import CommentCreate, CommentUpdate, Comment
from src.services.auth import auth_service
from src.database.models import User, Comment as DB_Comment
from typing import List

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/create_comment/", response_model=Comment)
async def add_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Create a new comment for a photo.

    Args:
        comment (CommentCreate): The comment data, including the photo ID and comment text.
        db (Session): Database session dependency.
        current_user (User): The current authenticated user.

    Returns:
        Comment: The newly created comment with its details.
    """

    comment_obj = create_comment(db, comment.photo_id, current_user.id, comment.text)

    return Comment(
        id=comment_obj.id,
        text=comment_obj.text,
        created_at=comment_obj.created_at.isoformat(),
        updated_at=comment_obj.updated_at.isoformat(),
        user_id=comment_obj.user_id,
        photo_id=comment_obj.photo_id,
    )


@router.get("/get_comments/{photo_id}", response_model=List[Comment])
def read_comments(photo_id: int, db: Session = Depends(get_db)):
    """
    Get all comments for a specific photo.

    Args:
        photo_id (int): The ID of the photo.
        db (Session): Database session dependency.

    Returns:
        List[Comment]: A list of comments related to the photo.
    """

    comments = get_comments(db, photo_id)

    for comment in comments:
        comment.created_at = comment.created_at.isoformat()
        comment.updated_at = comment.updated_at.isoformat()
    return comments


@router.put("/update_comment/{comment_id}")
async def modify_comment(
    comment_id: int,
    comment: CommentUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing comment.

    Args:
        comment_id (int): The ID of the comment to update.
        comment (CommentUpdate): The updated comment data.
        current_user (User): The current authenticated user.
        db (Session): Database session dependency.

    Raises:
        HTTPException: 404 if the comment is not found, or 403 if the user is not authorized to modify the comment.

    Returns:
        DB_Comment: The updated comment object.
    """

    existing_comment = db.query(DB_Comment).filter(DB_Comment.id == comment_id).first()

    if existing_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Checking if the user is the author of the comment
    if existing_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this comment"
        )

    # The comment refresh
    for key, value in comment.dict(exclude_unset=True).items():
        setattr(existing_comment, key, value)

    db.commit()
    db.refresh(existing_comment)

    return existing_comment
