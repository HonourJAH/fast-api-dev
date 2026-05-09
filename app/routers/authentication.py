import jwt
from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from app.database import SessionDep
from app.models.user_models import TokenData, UserInDB, User
from sqlmodel import select
from app import utils

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from dotenv import load_dotenv
import os

from datetime import timedelta

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(tags=["Authentication"])


def get_user(email: str, session: SessionDep):
    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_dict = user.model_dump()

    return UserInDB(**user_dict, hashed_password=user.password)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)

    except InvalidTokenError:
        raise credentials_exception

    user = get_user(email=token_data.email, session=session)

    if user is None:
        raise credentials_exception
    return user


@router.post("/login")
def login(
    session: SessionDep,
    login_details: OAuth2PasswordRequestForm = Depends(),
):
    # verify the email and password
    email, password = login_details.username, login_details.password

    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    correct_password = utils.verify_password(password, user.password)

    if email and correct_password:
        # Create a JWT token
        token = utils.create_access_token(
            data={"email": email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            SECRET_KEY=SECRET_KEY,
            ALGORITHM=ALGORITHM,
        )

        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
