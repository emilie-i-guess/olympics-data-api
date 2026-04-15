import uuid
from . import schemas
from . import models
from utils.utils import format_response
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from typing import List, Optional

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get database access in endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency for guarding tokens, or if the user has permission to fetch data
def verify_token(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.tokens < 1:
        raise HTTPException(
            status_code=402, detail="Not enough tokens. Please buy more."
        )

    # Subtract 1 token and save
    user.tokens -= 1 # type: ignore
    db.commit()
    return user


# ENDPOINTS #


# POST /v1/user to create user
@app.post("/v1/user", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate server id and saves user
    generated_id = str(uuid.uuid4())

    new_user = models.User(
        user_id=generated_id,
        email=user.email,
        hashed_password=user.password,
        tokens=100,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# GET /user to return all users
@app.get("/v1/user", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# GET /user/<user-id> to return specific user
@app.get("/v1/user/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# PUT /user/<user-id> to update user
@app.put("/v1/user/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: str, user_update: schemas.UserUpdate, db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.email:
        db_user.email = user_update.email # type: ignore
    if user_update.password:
        db_user.hashed_password = user_update.password # type: ignore

    db.commit()
    db.refresh(db_user)
    return db_user


# DEL /user/<user-id> to delete user
@app.delete("/v1/user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}


# POST /tokens for adding tokens to a user
@app.post("/v1/tokens/{user_id}", response_model=schemas.UserResponse)
def add_tokens(
    user_id: str, token_data: schemas.TokenAdd, db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.tokens += token_data.amount # type: ignore
    db.commit()
    db.refresh(user)
    return user


# GET /v1/sport/{sport_id}
@app.get("/v1/sport/{sport_id}")
def get_sport_results(
    sport_id: str,
    country: Optional[str] = None,
    year: Optional[int] = None,
    medals: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(verify_token),
    accept: Optional[str] = Header(None),
):
    query = db.query(models.OlympicResult).filter(
        models.OlympicResult.sport == sport_id
    )

    if country:
        query = query.filter(models.OlympicResult.noc == country.upper())
    if year:
        query = query.filter(models.OlympicResult.year == year)
    if medals:
        query = query.filter(
            models.OlympicResult.medal == medals.capitalize()
        )  # Capitalization to match data set

    results = query.all()

    # Manually converting SQLAlchemy objects into dicts before XML conversion
    results_dict = [row.__dict__ for row in results]
    for r in results_dict:
        r.pop("_sa_instance_state", None)

    data = {
        "sport": sport_id,
        "count": len(results),
        "results": results_dict,
        "remaining_tokens": user.tokens,
    }

    return format_response(data, accept or "")


# GET /v1/athlete/{athlete_id}
@app.get("/v1/athlete/{athlete_id}")
def get_athlete_results(
    athlete_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(verify_token),
):
    results = (
        db.query(models.OlympicResult)
        .filter(models.OlympicResult.athlete_id == athlete_id)
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="Athlete not found")

    return {
        "athlete_id": athlete_id,
        "name": results[0].name,
        "results": results,
        "remaining_tokens": user.tokens,
    }


# GET /v1/country/{country_id}
@app.get("/v1/country/{country_id}")
def get_country_results(
    country_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(verify_token),
):
    # Uppercasing country_id to match NOC format
    results = (
        db.query(models.OlympicResult)
        .filter(models.OlympicResult.noc == country_id.upper())
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="Country code not found")

    return {
        "country": country_id.upper(),
        "total_entries": len(results),
        "results": results,
        "remaining_tokens": user.tokens,
    }
