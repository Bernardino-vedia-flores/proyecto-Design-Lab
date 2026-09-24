from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from jose import JWTError, jwt
from dotenv import load_dotenv
from typing import Optional
import strawberry
from strawberry.fastapi import GraphQLRouter
import os

# ── CONFIGURACIÓN ──────────────────────────────────────────────────
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET   = os.getenv("JWT_SECRET")
JWT_ALGO     = "HS256"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="MS Reservas", version="1.0.0")

# ── CORS ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MODELOS REST ───────────────────────────────────────────────────
class ReservaCreate(BaseModel):
    habitacion_id: str
    fecha_entrada: str
    fecha_salida:  str
    precio_total:  float

# ── UTILIDAD JWT ───────────────────────────────────────────────────
def obtener_usuario_token(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado.")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado.")

# ── GRAPHQL TYPES ──────────────────────────────────────────────────
@strawberry.type
class ReservaType:
    id:            str
    usuario_id:    str
    habitacion_id: str
    fecha_entrada: str
    fecha_salida:  str
    precio_total:  float
    estado:        str
    created_at:    str

@strawberry.type
class Query:
    @strawberry.field
    def reservas(self, usuario_id: Optional[str] = None) -> list[ReservaType]:
        query = supabase.table("reservas").select("*")
        if usuario_id:
            query = query.eq("usuario_id", usuario_id)
        resultado = query.order("created_at", desc=True).execute()
        return [ReservaType(**{
            "id":            r["id"],
            "usuario_id":    r["usuario_id"],
            "habitacion_id": r["habitacion_id"],
            "fecha_entrada": r["fecha_entrada"],
            "fecha_salida":  r["fecha_salida"],
            "precio_total":  float(r["precio_total"]),
            "estado":        r["estado"],
            "created_at":    str(r["created_at"])
        }) for r in resultado.data]

    @strawberry.field
    def reserva(self, id: str) -> Optional[ReservaType]:
        resultado = supabase.table("reservas").select("*").eq("id", id).execute()
        if not resultado.data:
            return None
        r = resultado.data[0]
        return ReservaType(**{
            "id":            r["id"],
            "usuario_id":    r["usuario_id"],
            "habitacion_id": r["habitacion_id"],
            "fecha_entrada": r["fecha_entrada"],
            "fecha_salida":  r["fecha_salida"],
            "precio_total":  float(r["precio_total"]),
            "estado":        r["estado"],
            "created_at":    str(r["created_at"])
        })

    @strawberry.field
    def reservas_por_estado(self, estado: str) -> list[ReservaType]:
        resultado = supabase.table("reservas").select("*").eq(
            "estado", estado
        ).order("created_at", desc=True).execute()
        return [ReservaType(**{
            "id":            r["id"],
            "usuario_id":    r["usuario_id"],
            "habitacion_id": r["habitacion_id"],
            "fecha_entrada": r["fecha_entrada"],
            "fecha_salida":  r["fecha_salida"],
            "precio_total":  float(r["precio_total"]),
            "estado":        r["estado"],
            "created_at":    str(r["created_at"])
        }) for r in resultado.data]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def crear_reserva(
        self,
        usuario_id:    str,
        habitacion_id: str,
        fecha_entrada: str,
        fecha_salida:  str,
        precio_total:  float
    ) -> ReservaType:
        nueva = supabase.table("reservas").insert({
            "usuario_id":    usuario_id,
            "habitacion_id": habitacion_id,
            "fecha_entrada": fecha_entrada,
            "fecha_salida":  fecha_salida,
            "precio_total":  precio_total,
            "estado":        "pendiente"
        }).execute()

        if not nueva.data:
            raise Exception("Error al crear la reserva.")

        r = nueva.data[0]
        return ReservaType(**{
            "id":            r["id"],
            "usuario_id":    r["usuario_id"],
            "habitacion_id": r["habitacion_id"],
            "fecha_entrada": r["fecha_entrada"],
            "fecha_salida":  r["fecha_salida"],
            "precio_total":  float(r["precio_total"]),
            "estado":        r["estado"],
            "created_at":    str(r["created_at"])
        })

    @strawberry.mutation
    def cancelar_reserva(self, id: str) -> ReservaType:
        resultado = supabase.table("reservas").update(
            {"estado": "cancelada"}
        ).eq("id", id).execute()

        if not resultado.data:
            raise Exception("Reserva no encontrada.")

        r = resultado.data[0]
        return ReservaType(**{
            "id":            r["id"],
            "usuario_id":    r["usuario_id"],
            "habitacion_id": r["habitacion_id"],
            "fecha_entrada": r["fecha_entrada"],
            "fecha_salida":  r["fecha_salida"],
            "precio_total":  float(r["precio_total"]),
            "estado":        r["estado"],
            "created_at":    str(r["created_at"])
        })

    @strawberry.mutation
    def actualizar_estado(self, id: str, estado: str) -> ReservaType:
        estados_validos = ["pendiente", "confirmada", "cancelada"]
        if estado not in estados_validos:
            raise Exception(f"Estado inválido. Debe ser uno de: {estados_validos}")

        resultado = supabase.table("reservas").update(
            {"estado": estado}
        ).eq("id", id).execute()

        if not resultado.data:
            raise Exception("Reserva no encontrada.")

        r = resultado.data[0]
        return ReservaType(**{
            "id":            r["id"],
            "usuario_id":    r["usuario_id"],
            "habitacion_id": r["habitacion_id"],
            "fecha_entrada": r["fecha_entrada"],
            "fecha_salida":  r["fecha_salida"],
            "precio_total":  float(r["precio_total"]),
            "estado":        r["estado"],
            "created_at":    str(r["created_at"])
        })

# ── GRAPHQL ROUTER ─────────────────────────────────────────────────
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# ── ENDPOINTS REST ─────────────────────────────────────────────────
@app.get("/")
def health():
    return {"servicio": "MS Reservas", "estado": "activo"}

# CREAR RESERVA (REST)
@app.post("/reservas")
def crear_reserva(data: ReservaCreate, authorization: str = Header(None)):
    usuario = obtener_usuario_token(authorization)
    usuario_id = usuario["sub"]

    # Verificar que la habitación esté disponible
    habitacion = supabase.table("habitaciones").select(
        "id, disponible"
    ).eq("id", data.habitacion_id).execute()

    if not habitacion.data:
        raise HTTPException(status_code=404, detail="Habitación no encontrada.")

    if not habitacion.data[0]["disponible"]:
        raise HTTPException(status_code=400, detail="La habitación no está disponible.")

    # Crear la reserva
    nueva = supabase.table("reservas").insert({
        "usuario_id":    usuario_id,
        "habitacion_id": data.habitacion_id,
        "fecha_entrada": data.fecha_entrada,
        "fecha_salida":  data.fecha_salida,
        "precio_total":  data.precio_total,
        "estado":        "pendiente"
    }).execute()

    if not nueva.data:
        raise HTTPException(status_code=500, detail="Error al crear la reserva.")

    return nueva.data[0]

# VER MIS RESERVAS (REST)
@app.get("/reservas/usuario/me")
def mis_reservas(authorization: str = Header(None)):
    usuario = obtener_usuario_token(authorization)
    usuario_id = usuario["sub"]

    resultado = supabase.table("reservas").select("*").eq(
        "usuario_id", usuario_id
    ).order("created_at", desc=True).execute()

    return resultado.data

# VER DETALLE DE RESERVA (REST)
@app.get("/reservas/{id}")
def ver_reserva(id: str, authorization: str = Header(None)):
    obtener_usuario_token(authorization)

    resultado = supabase.table("reservas").select("*").eq("id", id).execute()

    if not resultado.data:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    return resultado.data[0]

# CANCELAR RESERVA (REST)
@app.put("/reservas/{id}/cancelar")
def cancelar_reserva(id: str, authorization: str = Header(None)):
    usuario = obtener_usuario_token(authorization)
    usuario_id = usuario["sub"]

    # Verificar que la reserva pertenece al usuario
    reserva = supabase.table("reservas").select("*").eq("id", id).execute()

    if not reserva.data:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    if reserva.data[0]["usuario_id"] != usuario_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para cancelar esta reserva.")

    if reserva.data[0]["estado"] == "cancelada":
        raise HTTPException(status_code=400, detail="La reserva ya está cancelada.")

    resultado = supabase.table("reservas").update(
        {"estado": "cancelada"}
    ).eq("id", id).execute()

    return resultado.data[0]