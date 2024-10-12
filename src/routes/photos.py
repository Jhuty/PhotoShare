import datetime
import os
import pickle

from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error, AuthorizationRequired, BadRequest

from src.database.db import get_db
from src.repository import photos as repository_photos
from src.schemas import PhotoResponse, PhotoModel, TagsPhoto
from src.conf.config import settings
from src.services.auth import auth_service
from src.database.models import User

router = APIRouter(prefix="/photos", tags=["photos"])

cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

# TODO: fetch all photos

@router.post('/', response_model=PhotoResponse)
async def create_photo(file: UploadFile = File(),
                       description: str = Form(),
                       # current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):
    # Create a clean file identifier
    clean_description = description[:7].replace(" ", "")
    clean_filename = file.filename.replace(".", "")
    public_id = f'PhotoShare/{clean_description}{clean_filename}'

    try:
        # Upload the file
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

        # Generate the Cloudinary image URL
        url = cloudinary.CloudinaryImage(public_id).build_url(crop='fill', version=r.get('version'))

        return await repository_photos.create_photo(description, url, db)
    except AuthorizationRequired as e:
        print(f"Required authorization: {e}.")
    except BadRequest:
        print(f"Loading ERROR. Bad request or file type not supported.")
    except Error as e:
        print(f"Error during loading the file: {e}")


@router.get('/{photo_id}', response_model=PhotoResponse)
async def read_photo(photo_id: int,
                     # current_user: User = Depends(auth_service.get_current_user),
                     db: Session = Depends(get_db)):
    photo = await repository_photos.read_photo(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo


@router.put('/{photo_id}', response_model=PhotoResponse)
async def update_photo(photo_id: int,
                       file: UploadFile = File(),
                       description: str = Form(),
                       # current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):

    # Create a clean file identifier
    clean_description = description[:7].replace(" ", "")
    clean_filename = file.filename.replace(".", "")
    public_id = f'PhotoShare/{clean_description}{clean_filename}'

    try:
        # Upload the file
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

        # Generate the Cloudinary image URL
        url = cloudinary.CloudinaryImage(public_id).build_url(crop='fill', version=r.get('version'))

        photo = await repository_photos.update_photo(photo_id, url, description, db)

        if photo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
        return photo

    except AuthorizationRequired as e:
        print(f"Required authorization: {e}.")
    except BadRequest:
        print(f"Loading ERROR. Bad request or file type not supported.")
    except Error as e:
        print(f"Error during loading the file: {e}")


@router.delete('/{photo_id}', response_model=PhotoResponse)
async def delete_photo(photo_id: int,
                       # current_user: User = Depends(auth_service.get_current_user),
                       db: Session = Depends(get_db)):

    photo = await repository_photos.delete_photo(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
    return photo


@router.patch('/{photo_id}', response_model=PhotoResponse)
async def change_description(photo_id: int,
                             description: str,
                             # current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):

    photo = await repository_photos.change_description(photo_id, description, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
    return photo


@router.patch('/add_tags/{photo_id}', response_model=PhotoResponse)
async def add_tags(photo_id: int,
                   body: TagsPhoto,
                   # current_user: User = Depends(auth_service.get_current_user),
                   db: Session = Depends(get_db)):
    if len(body.tags) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Can assign maximum 5 tags for a photo')

    photo = await repository_photos.add_tags(photo_id, body, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Photo not found')
    return photo

