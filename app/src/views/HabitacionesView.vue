<template>
  <div class="habitaciones-page">

    <!-- ENCABEZADO -->
    <div class="page-header">
      <div class="header-content">
        <h1>Habitaciones <span class="gold">disponibles</span></h1>
        <p>Encuentra la habitación perfecta para tu estadía en Sucre, la capital</p>
      </div>
    </div>

    <!-- FILTROS -->
    <div class="filtros-bar">
      <div class="filtros-content">

        <div class="filtro-field">
          <label>LLEGADA</label>
          <input type="date" v-model="filtros.fechaEntrada" :min="hoy" @change="filtrar" />
        </div>

        <div class="filtro-field">
          <label>SALIDA</label>
          <input type="date" v-model="filtros.fechaSalida" :min="filtros.fechaEntrada" @change="filtrar" />
        </div>

        <div class="filtro-field filtro-sm">
          <label>TIPO</label>
          <select v-model="filtros.tipo" @change="filtrar">
            <option value="">Todos</option>
            <option value="simple">Simple</option>
            <option value="doble">Doble</option>
            <option value="suite">Suite</option>
          </select>
        </div>

        <div class="filtro-field filtro-sm">
          <label>PRECIO MÁX.</label>
          <select v-model="filtros.precioMax" @change="filtrar">
            <option value="">Cualquiera</option>
            <option value="100">Hasta $100</option>
            <option value="150">Hasta $150</option>
            <option value="200">Hasta $200</option>
            <option value="300">Hasta $300</option>
          </select>
        </div>

        <div class="filtro-field filtro-sm">
          <label>SOLO DISPONIBLES</label>
          <select v-model="filtros.soloDisponibles" @change="filtrar">
            <option value="false">Todas</option>
            <option value="true">Solo disponibles</option>
          </select>
        </div>

        <button class="btn-limpiar" @click="limpiarFiltros">✕ Limpiar</button>

      </div>
    </div>

    <!-- RESULTADOS -->
    <div class="resultados-container">

      <!-- CONTADOR -->
      <div class="resultados-header">
        <span class="resultados-count">
          {{ habitacionesFiltradas.length }} habitación(es) encontrada(s)
        </span>
        <div class="orden">
          <label>Ordenar por:</label>
          <select v-model="orden" @change="ordenar">
            <option value="precio_asc">Precio: menor a mayor</option>
            <option value="precio_desc">Precio: mayor a menor</option>
            <option value="capacidad">Capacidad</option>
          </select>
        </div>
      </div>

      <!-- CARGANDO -->
      <div v-if="cargando" class="cargando">
        <div class="spinner"></div>
        <p>Cargando habitaciones...</p>
      </div>

      <!-- ERROR -->
      <div v-else-if="error" class="error-msg">
        <span>⚠️ {{ error }}</span>
        <button @click="cargarHabitaciones" class="btn-reintentar">Reintentar</button>
      </div>

      <!-- SIN RESULTADOS -->
      <div v-else-if="habitacionesFiltradas.length === 0" class="sin-resultados">
        <span style="font-size:48px">🏨</span>
        <h3>No se encontraron habitaciones</h3>
        <p>Intenta cambiar los filtros de búsqueda</p>
        <button @click="limpiarFiltros" class="btn-limpiar-grande">Limpiar filtros</button>
      </div>

      <!-- GRID DE HABITACIONES -->
      <div v-else class="rooms-grid">
        <div
          v-for="habitacion in habitacionesFiltradas"
          :key="habitacion.id"
          class="room-card"
          :class="{ 'no-disponible': !habitacion.disponible }"
        >
          <!-- IMAGEN -->
          <div class="room-img" :class="habitacion.tipo">
            <span class="room-emoji">{{ emojiTipo(habitacion.tipo) }}</span>
            <div class="room-badge" :class="habitacion.disponible ? 'disponible' : 'ocupada'">
              {{ habitacion.disponible ? '● Disponible' : '● Ocupada' }}
            </div>
            <div class="room-numero"># {{ habitacion.numero }}</div>
          </div>

          <!-- INFO -->
          <div class="room-info">
            <div class="room-tipo">{{ habitacion.tipo.toUpperCase() }}</div>
            <div class="room-nombre">{{ habitacion.descripcion || 'Habitación ' + habitacion.numero }}</div>

            <div class="room-features">
              <div class="feature">
                <span>👤</span>
                <span>{{ habitacion.capacidad }} persona(s)</span>
              </div>
              <div class="feature">
                <span>📶</span>
                <span>WiFi gratis</span>
              </div>
              <div class="feature">
                <span>❄️</span>
                <span>Aire acondicionado</span>
              </div>
              <div class="feature">
                <span>🍳</span>
                <span>Desayuno incluido</span>
              </div>
            </div>

            <div class="room-footer">
              <div>
                <div class="room-price">
                  ${{ habitacion.precio_noche }}
                  <span class="price-label">/ noche</span>
                </div>
                <div v-if="filtros.fechaEntrada && filtros.fechaSalida" class="precio-total">
                  Total: ${{ calcularTotal(habitacion.precio_noche) }}
                  ({{ calcularNoches() }} noches)
                </div>
              </div>
              <button
                class="btn-reservar"
                :class="{ 'btn-reservar-active': habitacion.disponible }"
                :disabled="!habitacion.disponible"
                @click="irAReservar(habitacion.id)"
              >
                {{ habitacion.disponible ? 'Reservar' : 'No disponible' }}
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: 'HabitacionesView',

  data() {
    return {
      cargando: false,
      error: '',
      habitaciones: [],
      habitacionesFiltradas: [],
      orden: 'precio_asc',
      filtros: {
        fechaEntrada: '',
        fechaSalida: '',
        tipo: '',
        precioMax: '',
        soloDisponibles: 'false'
      }
    }
  },

  computed: {
    hoy() {
      return new Date().toISOString().split('T')[0]
    }
  },

  mounted() {
    // Leer filtros desde la URL si vienen del buscador de la landing
    const query = this.$route.query
    if (query.entrada) this.filtros.fechaEntrada = query.entrada
    if (query.salida)  this.filtros.fechaSalida  = query.salida
    if (query.tipo)    this.filtros.tipo          = query.tipo

    this.cargarHabitaciones()
  },

  methods: {
    async cargarHabitaciones() {
      this.cargando = true
      this.error = ''
      try {
        const respuesta = await fetch('http://localhost:8000/api/habitaciones')
        if (!respuesta.ok) throw new Error('Error al cargar habitaciones')
        this.habitaciones = await respuesta.json()
        this.filtrar()
      } catch (err) {
        this.error = 'No se pudieron cargar las habitaciones. Verifica que el servidor esté activo.'
      } finally {
        this.cargando = false
      }
    },

    filtrar() {
      let resultado = [...this.habitaciones]

      // Filtro por tipo
      if (this.filtros.tipo) {
        resultado = resultado.filter(h => h.tipo === this.filtros.tipo)
      }

      // Filtro por precio máximo
      if (this.filtros.precioMax) {
        resultado = resultado.filter(h => h.precio_noche <= Number(this.filtros.precioMax))
      }

      // Filtro solo disponibles
      if (this.filtros.soloDisponibles === 'true') {
        resultado = resultado.filter(h => h.disponible)
      }

      this.habitacionesFiltradas = resultado
      this.ordenar()
    },

    ordenar() {
      if (this.orden === 'precio_asc') {
        this.habitacionesFiltradas.sort((a, b) => a.precio_noche - b.precio_noche)
      } else if (this.orden === 'precio_desc') {
        this.habitacionesFiltradas.sort((a, b) => b.precio_noche - a.precio_noche)
      } else if (this.orden === 'capacidad') {
        this.habitacionesFiltradas.sort((a, b) => a.capacidad - b.capacidad)
      }
    },

    limpiarFiltros() {
      this.filtros = {
        fechaEntrada: '',
        fechaSalida: '',
        tipo: '',
        precioMax: '',
        soloDisponibles: 'false'
      }
      this.filtrar()
    },

    calcularNoches() {
      if (!this.filtros.fechaEntrada || !this.filtros.fechaSalida) return 0
      const entrada = new Date(this.filtros.fechaEntrada)
      const salida  = new Date(this.filtros.fechaSalida)
      const diff = (salida - entrada) / (1000 * 60 * 60 * 24)
      return diff > 0 ? diff : 0
    },

    calcularTotal(precioPorNoche) {
      const noches = this.calcularNoches()
      return (noches * precioPorNoche).toFixed(2)
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
.habitaciones-page {
  background-color: #0a0a0a;
  min-height: 100vh;
  color: #ffffff;
}

/* ── ENCABEZADO ── */
.page-header {
  background-color: #111111;
  border-bottom: 1px solid #1e1e1e;
  padding: 2rem;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header h1 {
  font-size: 26px;
  font-weight: 500;
  margin-bottom: 6px;
}

.gold { color: #C9A84C; }

.page-header p {
  font-size: 13px;
  color: #555555;
}

/* ── FILTROS ── */
.filtros-bar {
  background-color: #0d0d0d;
  border-bottom: 1px solid #1a1a1a;
  padding: 1rem 2rem;
  position: sticky;
  top: 60px;
  z-index: 100;
}

.filtros-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filtro-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  min-width: 120px;
}

.filtro-sm { max-width: 150px; }

.filtro-field label {
  font-size: 9px;
  color: #C9A84C;
  font-weight: 600;
  letter-spacing: 1px;
}

.filtro-field input,
.filtro-field select {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 6px;
  padding: 7px 10px;
  font-size: 12px;
  color: #ffffff;
  outline: none;
  transition: border-color 0.2s;
}

.filtro-field input:focus,
.filtro-field select:focus {
  border-color: #C9A84C;
}

.filtro-field select option { background-color: #111111; }

.btn-limpiar {
  background: transparent;
  border: 1px solid #2a2a2a;
  color: #555555;
  padding: 7px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  height: 34px;
}

.btn-limpiar:hover {
  border-color: #EF5350;
  color: #EF5350;
}

/* ── RESULTADOS ── */
.resultados-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

.resultados-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.resultados-count {
  font-size: 13px;
  color: #555555;
}

.orden {
  display: flex;
  align-items: center;
  gap: 8px;
}

.orden label {
  font-size: 12px;
  color: #555555;
}

.orden select {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 12px;
  color: #ffffff;
  outline: none;
}

/* ── CARGANDO ── */
.cargando {
  text-align: center;
  padding: 4rem;
  color: #555555;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #1e1e1e;
  border-top-color: #C9A84C;
  border-radius: 50%;
  animation: girar 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes girar { to { transform: rotate(360deg); } }

/* ── ERROR ── */
.error-msg {
  background-color: #1a0a0a;
  border: 1px solid #3a1a1a;
  color: #EF5350;
  padding: 1.25rem;
  border-radius: 10px;
  font-size: 13px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-reintentar {
  background: transparent;
  border: 1px solid #EF5350;
  color: #EF5350;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
}

/* ── SIN RESULTADOS ── */
.sin-resultados {
  text-align: center;
  padding: 4rem;
  color: #555555;
}

.sin-resultados h3 {
  font-size: 18px;
  color: #ffffff;
  margin: 1rem 0 0.5rem;
}

.sin-resultados p {
  font-size: 13px;
  margin-bottom: 1.5rem;
}

.btn-limpiar-grande {
  background-color: #C9A84C;
  border: none;
  color: #0a0a0a;
  padding: 10px 24px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

/* ── GRID ── */
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
  transition: border-color 0.2s, transform 0.2s;
}

.room-card:hover {
  border-color: #C9A84C;
  transform: translateY(-2px);
}

.room-card.no-disponible { opacity: 0.55; }

.room-img {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.room-img.simple { background-color: #0d1a1a; }
.room-img.doble  { background-color: #1a0d0d; }
.room-img.suite  { background-color: #1a1a0d; }

.room-emoji { font-size: 40px; opacity: 0.45; }

.room-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  background-color: rgba(0,0,0,0.75);
  border: 1px solid #2a2a2a;
}

.room-badge.disponible { color: #66BB6A; }
.room-badge.ocupada    { color: #EF5350; }

.room-numero {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
  color: #444444;
  background-color: rgba(0,0,0,0.6);
  padding: 2px 8px;
  border-radius: 4px;
}

.room-info { padding: 14px; }

.room-tipo {
  font-size: 10px;
  color: #C9A84C;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.room-nombre {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 10px;
}

.room-features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5px;
  margin-bottom: 12px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: #555555;
}

.room-footer {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-top: 1px solid #1a1a1a;
  padding-top: 10px;
  margin-top: 4px;
}

.room-price {
  font-size: 20px;
  font-weight: 500;
  color: #C9A84C;
}

.price-label {
  font-size: 11px;
  color: #555555;
  font-weight: 400;
}

.precio-total {
  font-size: 10px;
  color: #555555;
  margin-top: 2px;
}

.btn-reservar {
  background: transparent;
  border: 1px solid #2a2a2a;
  color: #444444;
  padding: 7px 14px;
  border-radius: 6px;
  font-size: 11px;
  cursor: not-allowed;
  transition: all 0.2s;
}

.btn-reservar-active {
  border-color: #C9A84C;
  color: #C9A84C;
  cursor: pointer;
}

.btn-reservar-active:hover {
  background-color: #C9A84C;
  color: #0a0a0a;
}

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .rooms-grid {
    grid-template-columns: 1fr;
  }

  .filtros-content {
    flex-wrap: wrap;
  }

  .filtro-sm {
    max-width: 100%;
  }

  .resultados-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>