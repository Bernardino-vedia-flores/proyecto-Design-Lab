from locust import HttpUser, task, between
import random

class UsuarioHotel(HttpUser):
    wait_time = between(1, 3)  # Espera entre 1 y 3 segundos entre peticiones
    token = None

    def on_start(self):
        """Se ejecuta al inicio de cada usuario virtual — hace login"""
        respuesta = self.client.post("/api/usuarios/login", json={
            "email": "test@hotel.com",
            "password": "test12345"
        })
        if respuesta.status_code == 200:
            self.token = respuesta.json().get("token")

    def auth_headers(self):
        """Retorna headers con token JWT"""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    # ── PRUEBAS DE HABITACIONES (más frecuentes) ──────────────────

    @task(5)
    def listar_habitaciones(self):
        """Listar todas las habitaciones - tarea más común"""
        self.client.get("/api/habitaciones")

    @task(3)
    def filtrar_por_tipo(self):
        """Filtrar habitaciones por tipo"""
        tipo = random.choice(["simple", "doble", "suite"])
        self.client.get(f"/api/habitaciones?tipo={tipo}")

    @task(2)
    def ver_habitacion_detalle(self):
        """Ver detalle de una habitación específica"""
        # Primero obtener lista para conseguir un ID real
        respuesta = self.client.get("/api/habitaciones")
        if respuesta.status_code == 200 and respuesta.json():
            habitacion = random.choice(respuesta.json())
            self.client.get(f"/api/habitaciones/{habitacion['id']}")

    # ── PRUEBAS DE USUARIOS ───────────────────────────────────────

    @task(2)
    def login(self):
        """Prueba de login"""
        self.client.post("/api/usuarios/login", json={
            "email": "test@hotel.com",
            "password": "test12345"
        })

    # ── PRUEBAS DE RESERVAS ───────────────────────────────────────

    @task(2)
    def ver_mis_reservas(self):
        """Ver reservas del usuario autenticado"""
        if self.token:
            self.client.get(
                "/api/reservas/usuario/me",
                headers=self.auth_headers()
            )

    # ── PRUEBA GRAPHQL ────────────────────────────────────────────

    @task(1)
    def graphql_reservas(self):
        """Consulta GraphQL de reservas"""
        if self.token:
            self.client.post(
                "/graphql",
                json={
                    "query": """
                        query {
                            reservasPorEstado(estado: "pendiente") {
                                id
                                estado
                                precio_total
                            }
                        }
                    """
                },
                headers={**self.auth_headers(), "Content-Type": "application/json"}
            )

    # ── PRUEBA HEALTH ─────────────────────────────────────────────

    @task(1)
    def health_check(self):
        """Verificar estado del Gateway"""
        self.client.get("/health")