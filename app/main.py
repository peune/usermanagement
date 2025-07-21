from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sqlalchemy.orm import Session
from typing import List, Any
from datetime import timedelta

import models, schemas, crud, auth, email_service
from database import SessionLocal, engine
from config import settings
from dependencies import get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8000"], # ???
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


#########################################################################################33

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/check-auth")
async def check_auth(request: Request, db: Session = Depends(get_db)):
    # Reuse your existing auth logic
    try:
        user = auth.get_current_user(request, db)
        return {"status": "authenticated"}
    except HTTPException:
        raise HTTPException(status_code=401)

@app.post("/token")
async def login_for_access_token(
    response: Response,  # Inject Response to set cookies
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")

    access_token = auth.create_access_token(data={"sub": user.email})

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,  # Enable in production (HTTPS only)
        samesite="lax",
        max_age=1800  # 30 minutes
    )
    return {"status": "success"}


@app.get("/welcome", response_class=HTMLResponse)
def welcome_page(
    request: Request, 
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db) 
    ):

    # Force fresh DB check (bypass cache)
    db.refresh(current_user)
    return templates.TemplateResponse("welcome.html", {"request": request, "user": current_user})

@app.post("/logout")
def logout(response: Response):
    # Clear the cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,  # Disable if not using HTTPS in dev
        samesite="lax"
    )
    return {"status": "success"}

##########################################################################################
@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

@app.post("/register", response_model=schemas.User)
def register_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db)
    ):

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = crud.create_user(db=db, user=user)

    # Send emails
    email_service.send_new_account_email(email_to=user.email, user=user)
    email_service.send_account_approval_request(admin_email=settings.ADMIN_EMAIL, user=user)
        
    return db_user

@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.post("/forgot-password")
async def forgot_password(
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return {"detail": "If this email exists, a reset link has been sent."}  # Avoid revealing if email exists
    
    reset_token = auth.generate_password_reset_token(user.email) 
 
    email_service.send_password_reset_email(user, reset_token) # implicit User conversion?

    return {"detail": "Password reset link sent to your email."}

from jose import JWTError, jwt

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "email": email, "token": token}
        )
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    

@app.post("/reset-password")
async def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update password (hash it first!)
        user.hashed_password = auth.get_password_hash(new_password)
        db.commit()
        return {"detail": "Password updated successfully"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

##########################################################################################
# Admin endpoints
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/admin/login")
def admin_login(
    response: Response, 
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
    ):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user or not user.is_superuser:
        raise HTTPException(status_code=400, detail="Invalid admin credentials")
    
    access_token = auth.create_access_token(data={"sub": user.email})

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,  # Enable in production (HTTPS only)
        samesite="lax",
        max_age=1800  # 30 minutes
    )
    return {"status": "success"}

@app.get("/admin/verify-token")
def verify_token(
    user: models.User = Depends(auth.get_current_admin)
):
    return {"status": "valid"}

@app.get("/admin/pending-users", response_model=List[schemas.User])
def get_pending_users(
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):
    pending_users = db.query(models.User)\
        .filter(models.User.is_approved == False)\
        .all()
    return pending_users

@app.patch("/admin/users/{user_id}/approve")
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):    
    db_user = crud.approve_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"detail": "User approved successfully"}

@app.delete("/admin/users/{user_id}/reject") # reject then delete
def reject_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(auth.get_current_admin)
):
    if not crud.reject_user(db, user_id=user_id):
        raise HTTPException(status_code=404, detail="User not found")
 
    return {"detail": "User rejected successfully"}
