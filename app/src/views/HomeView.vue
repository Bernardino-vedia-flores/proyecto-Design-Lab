<template>
  <div class="home">

    <!-- HERO -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-badge">✨ RESERVAS EN LÍNEA 24/7</div>
        <h1>Tu estancia perfecta en <span class="gold">Sucre, Bolivia</span></h1>
        <p>Reserva habitaciones de forma fácil y segura. Disponibilidad en tiempo real, confirmación inmediata.</p>

        <!-- BUSCADOR -->
        <div class="search-box">
          <div class="search-field">
            <label>LLEGADA</label>
            <input type="date" v-model="busqueda.fechaEntrada" :min="hoy" />
          </div>
          <div class="search-field">
            <label>SALIDA</label>
            <input type="date" v-model="busqueda.fechaSalida" :min="busqueda.fechaEntrada" />
          </div>
          <div class="search-field search-field-sm">
            <label>TIPO</label>
            <select v-model="busqueda.tipo">
              <option value="">Todas</option>
              <option value="simple">Simple</option>
              <option value="doble">Doble</option>
              <option value="suite">Suite</option>
            </select>
          </div>
          <button class="btn-search" @click="buscarHabitaciones">
            🔍 Buscar
          </button>
        </div>

        <!-- ESTADÍSTICAS -->
        <div class="stats">
          <div class="stat">
            <span class="stat-num">24</span>
            <span class="stat-label">Habitaciones</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <span class="stat-num">3</span>
            <span class="stat-label">Tipos de suite</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <span class="stat-num">4.9</span>
            <span class="stat-label">Calificación</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <span class="stat-num">500+</span>
            <span class="stat-label">Huéspedes</span>
          </div>
        </div>
      </div>
    </section>

    <!-- HABITACIONES DESTACADAS -->
    <section class="section">
      <div class="section-header">
        <h2>Habitaciones <span class="gold">disponibles</span></h2>
        <RouterLink to="/habitaciones" class="ver-todas">Ver todas →</RouterLink>
      </div>

      <!-- CARGANDO -->
      <div v-if="cargando" class="cargando">
        <div class="spinner"></div>
        <p>Cargando habitaciones...</p>
      </div>

      <!-- ERROR -->
      <div v-else-if="error" class="error-msg">
        {{ error }}
      </div>

      <!-- HABITACIONES -->
      <div v-else class="rooms-grid">
        <div
          v-for="habitacion in habitacionesDestacadas"
          :key="habitacion.id"
          class="room-card"
          :class="{ 'no-disponible': !habitacion.disponible }"
        >
          <div class="room-img" :class="habitacion.tipo">
            <span class="room-emoji">{{ emojiTipo(habitacion.tipo) }}</span>
            <div class="room-badge" :class="habitacion.disponible ? 'disponible' : 'ocupada'">
              {{ habitacion.disponible ? '● Disponible' : '● Ocupada' }}
            </div>
          </div>
          <div class="room-info">
            <div class="room-type">{{ habitacion.tipo.toUpperCase() }}</div>
            <div class="room-name">{{ habitacion.descripcion || 'Habitación ' + habitacion.numero }}</div>
            <div class="room-features">
              <span class="feat">👤 {{ habitacion.capacidad }} pers.</span>
              <span class="feat">📶 WiFi</span>
              <span class="feat">❄️ A/C</span>
            </div>
            <div class="room-footer">
              <div class="room-price">
                ${{ habitacion.precio_noche }}
                <span>/ noche</span>
              </div>
              <button
                class="btn-reservar"
                :disabled="!habitacion.disponible"
                @click="irAReservar(habitacion.id)"
              >
                {{ habitacion.disponible ? 'Reservar' : 'No disponible' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CARACTERÍSTICAS -->
    <section class="features">
      <div class="feat-card">
        <div class="feat-icon blue">🔒</div>
        <h4>Reserva segura</h4>
        <p>Autenticación JWT en cada transacción</p>
      </div>
      <div class="feat-card">
        <div class="feat-icon gold">⚡</div>
        <h4>Disponibilidad real</h4>
        <p>Consulta en tiempo real desde Supabase</p>
      </div>
      <div class="feat-card">
        <div class="feat-icon green">✅</div>
        <h4>Confirmación inmediata</h4>
        <p>Reserva confirmada en segundos</p>
      </div>
      <div class="feat-card">
        <div class="feat-icon purple">📅</div>
        <h4>Gestión fácil</h4>
        <p>Cancela o consulta desde tu panel</p>
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="footer">
      <p>© 2026 HotelReserve · Sucre, Bolivia</p>
      <div class="footer-links">
        <a href="#">Términos</a>
        <a href="#">Privacidad</a>
        <a href="#">Contacto</a>
      </div>
    </footer>

  </div>
</template>

<script>
export default {
  name: 'HomeView',

  data() {
    return {
      cargando: false,
      error: '',
      habitacionesDestacadas: [],
      busqueda: {
        fechaEntrada: '',
        fechaSalida: '',
        tipo: ''
      }
    }
  },

  computed: {
    hoy() {
      return new Date().toISOString().split('T')[0]
    }
  },

  mounted() {
    this.cargarHabitaciones()
  },

  methods: {
    async cargarHabitaciones() {
      this.cargando = true
      this.error = ''
      try {
        const respuesta = await fetch('http://localhost:8000/api/habitaciones')
        if (!respuesta.ok) throw new Error('Error al cargar habitaciones')
        const datos = await respuesta.json()
        // Mostrar solo las primeras 3 en la landing
        this.habitacionesDestacadas = datos.slice(0, 3)
      } catch (err) {
        this.error = 'No se pudieron cargar las habitaciones. Verifica que el servidor esté activo.'
      } finally {
        this.cargando = false
      }
    },

    buscarHabitaciones() {
      // Redirigir a habitaciones con los filtros como parámetros
      this.$router.push({
        path: '/habitaciones',
        query: {
          entrada: this.busqueda.fechaEntrada,
          salida: this.busqueda.fechaSalida,
          tipo: this.busqueda.tipo
        }
      })
    },

    irAReservar(id) {
      const token = localStorage.getItem('token')
      if (!token) {
        this.$router.push('/login')
        return
      }
      this.$router.push(`/reservar/${id}`)
    },

    emojiTipo(tipo) {
      const emojis = { simple: '🛏️', doble: '🛏️', suite: '👑' }
      return emojis[tipo] || '🏨'
    }
  }
}
</script>

<style scoped>
.home {
  background-color: #0a0a0a;
  min-height: 100vh;
  color: #ffffff;
}

/* ── HERO ── */
.hero {
  padding: 4rem 2rem 3rem;
  text-align: center;
  border-bottom: 1px solid #1a1a1a;
}

.hero-content {
  max-width: 700px;
  margin: 0 auto;
}

.hero-badge {
  display: inline-block;
  background-color: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 20px;
  padding: 6px 16px;
  font-size: 11px;
  color: #C9A84C;
  font-weight: 500;
  letter-spacing: 1px;
  margin-bottom: 1.5rem;
}

.hero h1 {
  font-size: 38px;
  font-weight: 500;
  color: #ffffff;
  line-height: 1.2;
  margin-bottom: 1rem;
}

.gold {
  color: #C9A84C;
}

.hero p {
  font-size: 14px;
  color: #666666;
  line-height: 1.7;
  margin-bottom: 2rem;
}

/* ── BUSCADOR ── */
.search-box {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  padding: 1.25rem;
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 2rem;
}

.search-field {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.search-field-sm {
  max-width: 130px;
}

.search-field label {
  font-size: 10px;
  color: #C9A84C;
  font-weight: 600;
  letter-spacing: 1px;
}

.search-field input,
.search-field select {
  background-color: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 7px;
  padding: 8px 10px;
  font-size: 12px;
  color: #ffffff;
  outline: none;
  width: 100%;
  transition: border-color 0.2s;
}

.search-field input:focus,
.search-field select:focus {
  border-color: #C9A84C;
}

.search-field select option {
  background-color: #1a1a1a;
}

.btn-search {
  background-color: #C9A84C;
  border: none;
  color: #0a0a0a;
  padding: 9px 22px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
  height: 36px;
}

.btn-search:hover {
  background-color: #E8C97A;
}

/* ── ESTADÍSTICAS ── */
.stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #1a1a1a;
}

.stat {
  text-align: center;
}

.stat-num {
  display: block;
  font-size: 24px;
  font-weight: 500;
  color: #C9A84C;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: #555555;
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 30px;
  background-color: #1e1e1e;
}

/* ── SECCIÓN HABITACIONES ── */
.section {
  padding: 2.5rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 500;
}

.ver-todas {
  font-size: 12px;
  color: #C9A84C;
  text-decoration: none;
}

.ver-todas:hover {
  text-decoration: underline;
}

/* ── CARGANDO ── */
.cargando {
  text-align: center;
  padding: 3rem;
  color: #555;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #1e1e1e;
  border-top-color: #C9A84C;
  border-radius: 50%;
  animation: girar 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes girar {
  to { transform: rotate(360deg); }
}

/* ── ERROR ── */
.error-msg {
  background-color: #1a0a0a;
  border: 1px solid #3a1a1a;
  color: #EF5350;
  padding: 1rem;
  border-radius: 8px;
  font-size: 13px;
  text-align: center;
}

/* ── GRID HABITACIONES ── */
.rooms-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.room-card {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.room-card:hover {
  border-color: #C9A84C;
}

.room-card.no-disponible {
  opacity: 0.6;
}

.room-img {
  height: 110px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.room-img.simple { background-color: #0d1a1a; }
.room-img.doble  { background-color: #1a0d0d; }
.room-img.suite  { background-color: #1a1a0d; }

.room-emoji {
  font-size: 36px;
  opacity: 0.5;
}

.room-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  background-color: rgba(0,0,0,0.7);
  border: 1px solid #2a2a2a;
}

.room-badge.disponible { color: #66BB6A; }
.room-badge.ocupada    { color: #EF5350; }

.room-info {
  padding: 14px;
}

.room-type {
  font-size: 10px;
  color: #C9A84C;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.room-name {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 8px;
}

.room-features {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.feat {
  font-size: 11px;
  color: #555555;
}

.room-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.room-price {
  font-size: 18px;
  font-weight: 500;
  color: #C9A84C;
}

.room-price span {
  font-size: 11px;
  color: #555555;
  font-weight: 400;
}

.btn-reservar {
  background: transparent;
  border: 1px solid #C9A84C;
  color: #C9A84C;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reservar:hover:not(:disabled) {
  background-color: #C9A84C;
  color: #0a0a0a;
}

.btn-reservar:disabled {
  border-color: #2a2a2a;
  color: #333333;
  cursor: not-allowed;
}

/* ── CARACTERÍSTICAS ── */
.features {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  padding: 0 2rem 2.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.feat-card {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  padding: 1.25rem;
  text-align: center;
}

.feat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  font-size: 20px;
}

.feat-icon.blue   { background-color: #0a1a2a; }
.feat-icon.gold   { background-color: #1a1400; }
.feat-icon.green  { background-color: #0a1a0a; }
.feat-icon.purple { background-color: #1a0a1a; }

.feat-card h4 {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 6px;
}

.feat-card p {
  font-size: 11px;
  color: #555555;
  line-height: 1.5;
}

/* ── FOOTER ── */
.footer {
  background-color: #111111;
  border-top: 1px solid #1e1e1e;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer p {
  font-size: 11px;
  color: #333333;
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-links a {
  font-size: 11px;
  color: #333333;
  text-decoration: none;
}

.footer-links a:hover {
  color: #C9A84C;
}

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .hero h1 { font-size: 26px; }

  .search-box {
    flex-direction: column;
  }

  .search-field-sm {
    max-width: 100%;
  }

  .rooms-grid {
    grid-template-columns: 1fr;
  }

  .features {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats {
    gap: 1rem;
  }
}
</style>