from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User, UserCreate, UserUpdate
from app.models.db_models import DBUser
from app.services.user_service import (
    create_user, 
    get_user, 
    update_user, 
    delete_user, 
    get_db, 
    verify_password, 
    create_access_token,
    get_current_user
)

router = APIRouter()

# Crear usuario (registro)
@router.post("/users/", response_model=User)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(user, db)

# Obtener usuario por ID (protegido)
@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    print("-----11111111-......1------")
   
    return get_user(user_id, db,current_user)

# Actualizar usuario por ID (protegido)
@router.put("/users/{user_id}", response_model=User)
def update_user_route(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    return update_user(user_id, user, db,current_user)

# Eliminar usuario por ID (protegido)
@router.delete("/users/{user_id}")
def delete_user_route(user_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    return delete_user(user_id, db,current_user)

# Login para obtener token
@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        #print("-----------")
        #print(user)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.contrasena})
        #print("-----------")
        #print(access_token) 
        

    except Exception as e:
        #print(f"----------Error en login: {str(e)}")
        raise HTTPException(  
            status_code=500,
            detail=f"Error interno en autenticación: {str(e)}"
        )
    return {"access_token": access_token, "token_type": "bearer"}

# Autenticación interna
def authenticate_user(db, email: str, password: str):
    try:
        user = db.query(DBUser).filter(DBUser.email == email).first()
        
        if not user or not verify_password(password, user.contrasena):
            return False
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al autenticar usuario: {str(e)}")
