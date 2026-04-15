# Olympics Data API

**Name: Emilie Dyrvik Homlong**


## Setup

1. **Install dependencies:**
    ```bash
    pip install -r requirements.txt

2. **Initialize database**
    Create and seed the SQLite database with Olympic data:
    python app/seed.py

3. **Run server:**
    uvicorn app.main:app --reload


## Using APIs

1. **Create user**
    POST /v1/user
    *Body:* {"email": "user@example.com", "password": "password"}
    This returns a user_id and 100 initial tokens.

2. **Get sports data**
    GET /v1/sport/{sport_name}?user_id={UUID}
    This will cost 1 token per successful request.
    *Formats:* Use Accept header for application/json (set as default) or application/xml.

3. **Quality and testing**
    Run pytest to verify logic and token reduction.
    Verified with flake8 and mypy for code standards and type safety.


## Deployment

**Live URL:** 





