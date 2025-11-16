from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import PlanVentaUpdate, User, UserCreate, UserUpdate
from app.models.db_models import DBUser,    PlanVenta, PlanVendedor
from typing import List
from app.services.user_service import (
    create_user, 
    get_user, 
    update_user, 
    delete_user, 
    get_db, 
    verify_password, 
    create_access_token,
    get_current_user,
    create_vendedor,
    read_vendedor,
    update_vendedor,
    delete_vendedor,
    read_vendedores,
    send_forgot_password,
    crear_plan_venta,
    listar_planes_venta,
    obtener_plan_venta_por_id,
    actualizar_plan_de_venta,
    eliminar_plan_de_venta

)

router = APIRouter()

# Creacion de vendedores

# Recuperar contraseña  
@router.post("/forgotPassword/")
def forgot_password(email, db: Session = Depends(get_db)):
    return send_forgot_password(email, db)


@router.post("/planes_venta/", status_code=201)
def plan_venta(  periodo: str, valor_ventas: float, vendedores_ids: List[int],  db: Session = Depends(get_db),  current_user: DBUser = Depends(get_current_user)):
    return crear_plan_venta(periodo, valor_ventas, vendedores_ids, db)


# ============================================================
#  Obtener todos los planes de venta
# ============================================================
@router.get("/planes_venta/", response_model=list)
def planes_venta( db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    return listar_planes_venta(db,current_user)

# ============================================================
#  Obtener un plan de venta por ID
# ============================================================
@router.get("/planes_venta/{plan_id}")
def obtener_plan_venta( plan_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    return obtener_plan_venta_por_id(plan_id, db,current_user)


# ============================================================
#  Actualizar un plan de venta
# ============================================================
@router.put("/planes_venta/{plan_id}")
def actualizar_plan_venta( plan_id: int,  plan_data: PlanVentaUpdate, db: Session = Depends(get_db),  current_user: DBUser = Depends(get_current_user)):
     return actualizar_plan_de_venta(
        plan_id,
        plan_data.periodo,
        plan_data.valor_ventas,
        plan_data.estado,
        plan_data.vendedores_ids,
        db,
        current_user
    )

# ============================================================
#  Eliminar un plan de venta
# ============================================================
@router.delete("/planes_venta/{plan_id}")
def eliminar_plan_venta(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    return eliminar_plan_de_venta(plan_id, db, current_user)


# Crear usuario vendedor (registro)
@router.post("/vendedor/", response_model=User)
def create_user_vendedor(user: UserCreate, db: Session = Depends(get_db),current_user: DBUser = Depends(get_current_user)):
    return create_vendedor(user, db,current_user)

# Obtener usuario vendedor por ID (protegido)
@router.get("/vendedor/{user_id}", response_model=User)
def read_user_vendedor(user_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
     
    return read_vendedor(user_id, db,current_user)

# Obtener los usuarios vendedores (protegido)
@router.get("/vendedores",response_model=List[User])
def read_users_vendedores( db: Session = Depends(get_db),skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user)):
     return read_vendedores( db,skip,limit,current_user)


# Actualizar usuario vendedor por ID (protegido)
@router.put("/vendedor/{user_id}", response_model=User)
def update_user_vendedor(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    return update_vendedor(user_id, user, db,current_user)

# Eliminar usuario vendedor por ID (protegido)
@router.delete("/vendedor/{user_id}")
def delete_user_vendedor(user_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    return delete_vendedor(user_id, db,current_user)



# Crear usuario (registro)
@router.post("/users/", response_model=User)
def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(user, db)

# Obtener usuario por ID (protegido)
@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    #print("-----11111111-......1------")
   
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
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
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
