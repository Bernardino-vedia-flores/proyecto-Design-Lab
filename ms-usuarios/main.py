from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# ── CONFIGURACIÓN ──────────────────────────────────────────────────
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET   = os.getenv("JWT_SECRET")
JWT_ALGO     = "HS256"
JWT_EXPIRY   = 60 * 24  # 24 horas en minutos

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="MS Usuarios", version="1.0.0")

# ── CORS ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)
# ── MODELOS ────────────────────────────────────────────────────────
class RegistroRequest(BaseModel):
    nombre:   str
    apellido: str
    email:    str
    password: str

class LoginRequest(BaseModel):
    email:    str
    password: str

# ── UTILIDADES JWT ─────────────────────────────────────────────────
def crear_token(data: dict):
    payload = data.copy()
    expira  = datetime.utcnow() + timedelta(minutes=JWT_EXPIRY)
    payload.update({"exp": expira})
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def verificar_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# ── ENDPOINTS ──────────────────────────────────────────────────────

@app.get("/")
def health():
    return {"servicio": "MS Usuarios", "estado": "activo"}

# REGISTRO
@app.post("/usuarios/registro")
def registro(data: RegistroRequest):
    # Verificar si el email ya existe
    existe = supabase.table("usuarios").select("id").eq("email", data.email).execute()
    if existe.data:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    # Encriptar contraseña
    password_hash = pwd_context.hash(data.password)

    # Guardar en Supabase
    nuevo = supabase.table("usuarios").insert({
        "nombre":        data.nombre,
        "apellido":      data.apellido,
        "email":         data.email,
        "password_hash": password_hash,
        "rol":           "huesped"
    }).execute()

    if not nuevo.data:
        raise HTTPException(status_code=500, detail="Error al crear el usuario.")

    usuario = nuevo.data[0]
    return {
        "mensaje":  "Usuario registrado exitosamente",
        "id":       usuario["id"],
        "nombre":   usuario["nombre"],
        "email":    usuario["email"]
    }

# LOGIN
@app.post("/usuarios/login")
def login(data: LoginRequest):
    # Buscar usuario por email
    resultado = supabase.table("usuarios").select("*").eq("email", data.email).execute()

    if not resultado.data:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

    usuario = resultado.data[0]

    # Verificar contraseña
    if not pwd_context.verify(data.password, usuario["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

    # Crear token JWT
    token = crear_token({
        "sub":   usuario["id"],
        "email": usuario["email"],
        "rol":   usuario["rol"],
        "nombre": usuario["nombre"]
    })

    return {
        "token":   token,
        "nombre":  usuario["nombre"],
        "email":   usuario["email"],
        "rol":     usuario["rol"]
    }

# VER PERFIL
@app.get("/usuarios/{id}")
def ver_perfil(id: str):
    resultado = supabase.table("usuarios").select(
        "id, nombre, apellido, email, rol, created_at"
    ).eq("id", id).execute()

    if not resultado.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return resultado.data[0]

# ACTUALIZAR PERFIL
@app.put("/usuarios/{id}")
def actualizar_perfil(id: str, data: dict):
    # No permitir actualizar password_hash ni rol directamente
    data.pop("password_hash", None)
    data.pop("rol", None)

    resultado = supabase.table("usuarios").update(data).eq("id", id).execute()

    if not resultado.data:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    return resultado.data[0]