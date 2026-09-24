from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional
import os

# ── CONFIGURACIÓN ──────────────────────────────────────────────────
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="MS Habitaciones", version="1.0.0")

# ── CORS ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MODELOS ────────────────────────────────────────────────────────
class HabitacionCreate(BaseModel):
    numero:       str
    tipo:         str
    precio_noche: float
    capacidad:    int
    descripcion:  Optional[str] = None
    disponible:   Optional[bool] = True
    imagen_url:   Optional[str] = None

class HabitacionUpdate(BaseModel):
    tipo:         Optional[str] = None
    precio_noche: Optional[float] = None
    capacidad:    Optional[int] = None
    descripcion:  Optional[str] = None
    disponible:   Optional[bool] = None
    imagen_url:   Optional[str] = None

# ── ENDPOINTS ──────────────────────────────────────────────────────

@app.get("/")
def health():
    return {"servicio": "MS Habitaciones", "estado": "activo"}

@app.get("/test")
def test_conexion():
    resultado = supabase.table("habitaciones").select("*").execute()
    return {
        "total": len(resultado.data),
        "datos": resultado.data,
        "error": str(resultado) if not resultado.data else None
    }

# LISTAR TODAS LAS HABITACIONES
@app.get("/habitaciones")
def listar_habitaciones(
    tipo: Optional[str] = None,
    disponible: Optional[bool] = None,
    precio_max: Optional[float] = None
):
    query = supabase.table("habitaciones").select("*")

    if tipo:
        query = query.eq("tipo", tipo)
    if disponible is not None:
        query = query.eq("disponible", disponible)
    if precio_max:
        query = query.lte("precio_noche", precio_max)

    resultado = query.order("numero").execute()
    return resultado.data

# VER UNA HABITACIÓN
@app.get("/habitaciones/{id}")
def ver_habitacion(id: str):
    resultado = supabase.table("habitaciones").select("*").eq("id", id).execute()

    if not resultado.data:
        raise HTTPException(status_code=404, detail="Habitación no encontrada.")

    return resultado.data[0]

# HABITACIONES DISPONIBLES POR FECHAS
@app.get("/habitaciones/disponibles/fechas")
def habitaciones_disponibles(fecha_entrada: str, fecha_salida: str):
    # Obtener IDs de habitaciones ocupadas en esas fechas
    reservas = supabase.table("reservas").select("habitacion_id").neq(
        "estado", "cancelada"
    ).lte("fecha_entrada", fecha_salida).gte("fecha_salida", fecha_entrada).execute()

    ids_ocupados = [r["habitacion_id"] for r in reservas.data]

    # Obtener habitaciones disponibles que no estén en esos IDs
    query = supabase.table("habitaciones").select("*").eq("disponible", True)

    resultado = query.execute()

    # Filtrar las ocupadas
    disponibles = [h for h in resultado.data if h["id"] not in ids_ocupados]

    return disponibles



# CREAR HABITACIÓN (admin)
@app.post("/habitaciones")
def crear_habitacion(data: HabitacionCreate):
    # Verificar que el número no exista
    existe = supabase.table("habitaciones").select("id").eq("numero", data.numero).execute()
    if existe.data:
        raise HTTPException(status_code=400, detail="Ya existe una habitación con ese número.")

    nueva = supabase.table("habitaciones").insert(data.dict()).execute()

    if not nueva.data:
        raise HTTPException(status_code=500, detail="Error al crear la habitación.")

    return nueva.data[0]

# ACTUALIZAR HABITACIÓN (admin)
@app.put("/habitaciones/{id}")
def actualizar_habitacion(id: str, data: HabitacionUpdate):
    # Filtrar solo los campos que se enviaron
    campos = {k: v for k, v in data.dict().items() if v is not None}

    if not campos:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar.")

    resultado = supabase.table("habitaciones").update(campos).eq("id", id).execute()

    if not resultado.data:
        raise HTTPException(status_code=404, detail="Habitación no encontrada.")

    return resultado.data[0]

# ELIMINAR HABITACIÓN (admin)
@app.delete("/habitaciones/{id}")
def eliminar_habitacion(id: str):
    # Verificar que no tenga reservas activas
    reservas = supabase.table("reservas").select("id").eq(
        "habitacion_id", id
    ).neq("estado", "cancelada").execute()

    if reservas.data:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar una habitación con reservas activas."
        )

    resultado = supabase.table("habitaciones").delete().eq("id", id).execute()

    if not resultado.data:
        raise HTTPException(status_code=404, detail="Habitación no encontrada.")

    return {"mensaje": "Habitación eliminada correctamente"}