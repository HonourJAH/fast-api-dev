from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models.vote_models import Vote
from app.models.post_models import Post
from app.models.user_models import UserInDB
from app.routers.authentication import get_current_user

router = APIRouter(tags=["Votes"])


# VOTE / UNVOTE
@router.post("/vote/{post_id}", status_code=status.HTTP_201_CREATED)
def vote(
    post_id: int,
    session: SessionDep,
    current_user: UserInDB = Depends(get_current_user),
):
    # check if post exists
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {post_id} not found",
        )

    # check if vote already exists
    existing_vote = session.get(Vote, (current_user.id, post_id))

    if existing_vote:
        # already voted → unvote
        session.delete(existing_vote)
        session.commit()
        return {"message": "Vote removed successfully"}
    else:
        # not voted yet → vote
        new_vote = Vote(user_id=current_user.id, post_id=post_id)
        session.add(new_vote)
        session.commit()
        return {"message": "Vote added successfully"}


# CAST A VOTE
# @router.post("/vote/{post_id}", status_code=status.HTTP_201_CREATED)
# def vote(
#     post_id: int,
#     session: SessionDep,
#     current_user: UserInDB = Depends(get_current_user),
# ):
#     # check if post exists
#     post = session.get(Post, post_id)
#     if not post:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {post_id} not found"
#         )

#     # check if user already voted
#     existing_vote = session.get(Vote, (current_user.id, post_id))
#     if existing_vote:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail="You have already voted on this post",
#         )

#     # create the vote
#     vote = Vote(user_id=current_user.id, post_id=post_id)
#     session.add(vote)
#     session.commit()

#     return {"message": "Vote added successfully"}


# DELETE VOTE (UNVOTE)
# @router.delete("/unvote/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
# def unvote(
#     post_id: int,
#     session: SessionDep,
#     current_user: UserInDB = Depends(get_current_user),
# ):
#     existing_vote = session.get(Vote, (current_user.id, post_id))

#     if not existing_vote:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="You have not voted on this post",
#         )

#     session.delete(existing_vote)
#     session.commit()
#     return None
