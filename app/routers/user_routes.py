from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select

from app.database import SessionDep
from app.models.user_models import (
    User,
    CreateUser,
    UserInDB,
    UserPublic,
    UserPublicAll,
    UserUpdate,
    UsersResponse,
)
from app import utils
from app.routers.authentication import get_current_user

router = APIRouter(tags=["Users"])


@router.post("/user", status_code=status.HTTP_201_CREATED, response_model=UserPublicAll)
def create_user(user: CreateUser, session: SessionDep):
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password
    user = User(**user.model_dump())

    if session.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There's already a user with that email. Please choose another email",
        )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/users/{user_id}", response_model=UserPublic)
def get_user(
    user_id: int,
    session: SessionDep,
    # current_user: UserInDB = Depends(get_current_user),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/users", response_model=UsersResponse)
def get_all_users(
    session: SessionDep,
    # current_user: UserInDB = Depends(get_current_user),
):
    users = session.exec(select(User)).all()
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )
    return UsersResponse(results=len(users), data=users)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: UserInDB = Depends(get_current_user),
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user_db)
    session.commit()
    return None


@router.patch("/users/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserUpdate,
    session: SessionDep,
    current_user: UserInDB = Depends(get_current_user),
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_data = user.model_dump(exclude_unset=True)
    if "email" in user_data:
        if session.exec(select(User).where(User.email == user_data["email"])).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There's already a user with that email. Please choose another email",
            )
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db
