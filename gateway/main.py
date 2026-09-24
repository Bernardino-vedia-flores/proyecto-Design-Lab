from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
import os

# ── CONFIGURACIÓN ──────────────────────────────────────────────────
load_dotenv()

MS_USUARIOS     = os.getenv("MS_USUARIOS",     "http://localhost:8001")
MS_HABITACIONES = os.getenv("MS_HABITACIONES", "http://localhost:8002")
MS_RESERVAS     = os.getenv("MS_RESERVAS",     "http://localhost:8003")

app = FastAPI(title="API Gateway - Hotel Reserve", version="1.0.0")

# ── CORS ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ── UTILIDAD: PROXY REQUEST ────────────────────────────────────────
async def proxy(method: str, url: str, request: Request = None, **kwargs):
    headers = {}
    if request:
        auth = request.headers.get("authorization")
        if auth:
            headers["authorization"] = auth

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            if method == "GET":
                resp = await client.get(url, headers=headers, params=kwargs.get("params"))
            elif method == "POST":
                resp = await client.post(url, headers=headers, json=kwargs.get("json"))
            elif method == "PUT":
                resp = await client.put(url, headers=headers, json=kwargs.get("json"))
            elif method == "DELETE":
                resp = await client.delete(url, headers=headers)

            return resp.json()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail=f"No se pudo conectar al microservicio. Verifica que esté corriendo."
            )

# ── HEALTH ─────────────────────────────────────────────────────────
@app.get("/")
def health():
    return {
        "servicio": "API Gateway",
        "estado":   "activo",
        "version":  "1.0.0",
        "microservicios": {
            "ms_usuarios":     MS_USUARIOS,
            "ms_habitaciones": MS_HABITACIONES,
            "ms_reservas":     MS_RESERVAS
        }
    }

@app.get("/health")
async def health_check():
    estados = {}
    async with httpx.AsyncClient(timeout=5) as client:
        for nombre, url in [
            ("ms_usuarios",     MS_USUARIOS),
            ("ms_habitaciones", MS_HABITACIONES),
            ("ms_reservas",     MS_RESERVAS)
        ]:
            try:
                resp = await client.get(url)
                estados[nombre] = "activo" if resp.status_code == 200 else "error"
            except:
                estados[nombre] = "inactivo"
    return {"gateway": "activo", "microservicios": estados}

# ── USUARIOS ───────────────────────────────────────────────────────
@app.post("/api/usuarios/registro")
async def registro(request: Request):
    body = await request.json()
    return await proxy("POST", f"{MS_USUARIOS}/usuarios/registro", json=body)

@app.post("/api/usuarios/login")
async def login(request: Request):
    body = await request.json()
    return await proxy("POST", f"{MS_USUARIOS}/usuarios/login", json=body)

@app.get("/api/usuarios/{id}")
async def ver_perfil(id: str, request: Request):
    return await proxy("GET", f"{MS_USUARIOS}/usuarios/{id}", request=request)

@app.put("/api/usuarios/{id}")
async def actualizar_perfil(id: str, request: Request):
    body = await request.json()
    return await proxy("PUT", f"{MS_USUARIOS}/usuarios/{id}", request=request, json=body)

# ── HABITACIONES ───────────────────────────────────────────────────
@app.get("/api/habitaciones")
async def listar_habitaciones(
    request: Request,
    tipo:        str = None,
    disponible:  bool = None,
    precio_max:  float = None
):
    params = {}
    if tipo:        params["tipo"]        = tipo
    if disponible is not None: params["disponible"] = disponible
    if precio_max:  params["precio_max"]  = precio_max

    return await proxy("GET", f"{MS_HABITACIONES}/habitaciones", params=params)

@app.get("/api/habitaciones/disponibles")
async def habitaciones_disponibles(
    request: Request,
    fecha_entrada: str,
    fecha_salida:  str
):
    params = {
        "fecha_entrada": fecha_entrada,
        "fecha_salida":  fecha_salida
    }
    return await proxy(
        "GET",
        f"{MS_HABITACIONES}/habitaciones/disponibles/fechas",
        params=params
    )

@app.get("/api/habitaciones/{id}")
async def ver_habitacion(id: str, request: Request):
    return await proxy("GET", f"{MS_HABITACIONES}/habitaciones/{id}")

@app.post("/api/habitaciones")
async def crear_habitacion(request: Request):
    body = await request.json()
    return await proxy("POST", f"{MS_HABITACIONES}/habitaciones", request=request, json=body)

@app.put("/api/habitaciones/{id}")
async def actualizar_habitacion(id: str, request: Request):
    body = await request.json()
    return await proxy("PUT", f"{MS_HABITACIONES}/habitaciones/{id}", request=request, json=body)

@app.delete("/api/habitaciones/{id}")
async def eliminar_habitacion(id: str, request: Request):
    return await proxy("DELETE", f"{MS_HABITACIONES}/habitaciones/{id}", request=request)

# ── RESERVAS ───────────────────────────────────────────────────────
@app.post("/api/reservas")
async def crear_reserva(request: Request):
    body = await request.json()
    return await proxy("POST", f"{MS_RESERVAS}/reservas", request=request, json=body)

@app.get("/api/reservas/usuario/me")
async def mis_reservas(request: Request):
    return await proxy("GET", f"{MS_RESERVAS}/reservas/usuario/me", request=request)

@app.get("/api/reservas/{id}")
async def ver_reserva(id: str, request: Request):
    return await proxy("GET", f"{MS_RESERVAS}/reservas/{id}", request=request)

@app.put("/api/reservas/{id}/cancelar")
async def cancelar_reserva(id: str, request: Request):
    return await proxy("PUT", f"{MS_RESERVAS}/reservas/{id}/cancelar", request=request)

# ── GRAPHQL PROXY ──────────────────────────────────────────────────
@app.post("/graphql")
async def graphql_proxy(request: Request):
    body = await request.json()
    headers = {}
    auth = request.headers.get("authorization")
    if auth:
        headers["authorization"] = auth

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                f"{MS_RESERVAS}/graphql",
                json=body,
                headers={**headers, "Content-Type": "application/json"}
            )
            return resp.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="MS Reservas no disponible.")