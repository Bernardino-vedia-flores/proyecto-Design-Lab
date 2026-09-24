<template>
  <div class="reserva-page">

    <!-- BREADCRUMB -->
    <div class="breadcrumb">
      <RouterLink to="/">Inicio</RouterLink>
      <span>›</span>
      <RouterLink to="/habitaciones">Habitaciones</RouterLink>
      <span>›</span>
      <span class="active">Realizar reserva</span>
    </div>

    <!-- CARGANDO HABITACIÓN -->
    <div v-if="cargando" class="cargando">
      <div class="spinner"></div>
      <p>Cargando información...</p>
    </div>

    <!-- ERROR -->
    <div v-else-if="error" class="error-msg">
      ⚠️ {{ error }}
      <RouterLink to="/habitaciones" class="btn-volver">Volver al catálogo</RouterLink>
    </div>

    <!-- CONTENIDO PRINCIPAL -->
    <div v-else class="reserva-container">

      <!-- COLUMNA IZQUIERDA: FORMULARIO -->
      <div class="form-col">

        <!-- PASOS -->
        <div class="steps">
          <div class="step" :class="{ done: pasoActual > 1, active: pasoActual === 1 }">
            <div class="step-circle">{{ pasoActual > 1 ? '✓' : '1' }}</div>
            <span>Habitación</span>
          </div>
          <div class="step-line" :class="{ done: pasoActual > 1 }"></div>
          <div class="step" :class="{ done: pasoActual > 2, active: pasoActual === 2 }">
            <div class="step-circle">{{ pasoActual > 2 ? '✓' : '2' }}</div>
            <span>Tus datos</span>
          </div>
          <div class="step-line" :class="{ done: pasoActual > 2 }"></div>
          <div class="step" :class="{ active: pasoActual === 3 }">
            <div class="step-circle">3</div>
            <span>Confirmar</span>
          </div>
        </div>

        <!-- PASO 1: FECHAS -->
        <div v-if="pasoActual === 1" class="paso">
          <h2 class="paso-titulo">📅 Selecciona las fechas</h2>

          <div v-if="errorPaso" class="error-inline">{{ errorPaso }}</div>

          <div class="row-2">
            <div class="field">
              <label>FECHA DE LLEGADA</label>
              <input type="date" v-model="reserva.fechaEntrada" :min="hoy" />
            </div>
            <div class="field">
              <label>FECHA DE SALIDA</label>
              <input type="date" v-model="reserva.fechaSalida" :min="reserva.fechaEntrada" />
            </div>
          </div>

          <div class="field">
            <label>NÚMERO DE HUÉSPEDES</label>
            <select v-model="reserva.huespedes">
              <option v-for="n in habitacion.capacidad" :key="n" :value="n">
                {{ n }} persona(s)
              </option>
            </select>
          </div>

          <div v-if="reserva.fechaEntrada && reserva.fechaSalida && noches > 0" class="resumen-fechas">
            <span>📆 {{ noches }} noche(s) seleccionada(s)</span>
            <span class="gold">Total estimado: ${{ precioTotal }}</span>
          </div>

          <button class="btn-siguiente" @click="siguientePaso">
            Continuar →
          </button>
        </div>

        <!-- PASO 2: DATOS DEL HUÉSPED -->
        <div v-if="pasoActual === 2" class="paso">
          <h2 class="paso-titulo">👤 Datos del huésped</h2>

          <div v-if="errorPaso" class="error-inline">{{ errorPaso }}</div>

          <div class="row-2">
            <div class="field">
              <label>NOMBRE</label>
              <input type="text" v-model="huesped.nombre" placeholder="Juan" />
            </div>
            <div class="field">
              <label>APELLIDO</label>
              <input type="text" v-model="huesped.apellido" placeholder="Pérez" />
            </div>
          </div>

          <div class="field">
            <label>CORREO ELECTRÓNICO</label>
            <input type="email" v-model="huesped.email" placeholder="tucorreo@email.com" />
          </div>

          <div class="field">
            <label>TELÉFONO</label>
            <input type="text" v-model="huesped.telefono" placeholder="+591 7XXXXXXX" />
          </div>

          <div class="field">
            <label>SOLICITUDES ESPECIALES (opcional)</label>
            <textarea
              v-model="huesped.solicitudes"
              placeholder="Ej: habitación en piso alto, cama extra, llegada tardía..."
              rows="3"
            ></textarea>
          </div>

          <div class="btn-grupo">
            <button class="btn-atras" @click="pasoActual = 1">← Atrás</button>
            <button class="btn-siguiente" @click="siguientePaso">Continuar →</button>
          </div>
        </div>

        <!-- PASO 3: CONFIRMACIÓN -->
        <div v-if="pasoActual === 3" class="paso">
          <h2 class="paso-titulo">✅ Confirma tu reserva</h2>

          <div class="confirmacion-detalle">
            <div class="conf-row">
              <span class="conf-label">Habitación</span>
              <span class="conf-value">{{ habitacion.descripcion || 'Habitación ' + habitacion.numero }}</span>
            </div>
            <div class="conf-row">
              <span class="conf-label">Tipo</span>
              <span class="conf-value gold">{{ habitacion.tipo?.toUpperCase() }}</span>
            </div>
            <div class="conf-row">
              <span class="conf-label">Check-in</span>
              <span class="conf-value">{{ formatFecha(reserva.fechaEntrada) }}</span>
            </div>
            <div class="conf-row">
              <span class="conf-label">Check-out</span>
              <span class="conf-value">{{ formatFecha(reserva.fechaSalida) }}</span>
            </div>
            <div class="conf-row">
              <span class="conf-label">Noches</span>
              <span class="conf-value">{{ noches }}</span>
            </div>
            <div class="conf-row">
              <span class="conf-label">Huéspedes</span>
              <span class="conf-value">{{ reserva.huespedes }} persona(s)</span>
            </div>
            <div class="conf-row">
              <span class="conf-label">Huésped</span>
              <span class="conf-value">{{ huesped.nombre }} {{ huesped.apellido }}</span>
            </div>
            <div class="conf-row">
              <span class="conf-label">Correo</span>
              <span class="conf-value">{{ huesped.email }}</span>
            </div>
          </div>

          <div class="politica">
            <h4>📋 Política de cancelación</h4>
            <p>✔ Cancelación gratuita hasta 48h antes del check-in</p>
            <p>✔ Check-in desde las 14:00 · Check-out hasta las 12:00</p>
            <p>✘ No se permiten mascotas en las instalaciones</p>
          </div>

          <div v-if="errorPaso" class="error-inline">{{ errorPaso }}</div>
          <div v-if="exitoReserva" class="exito-msg">{{ exitoReserva }}</div>

          <div class="btn-grupo">
            <button class="btn-atras" @click="pasoActual = 2">← Atrás</button>
            <button class="btn-confirmar" @click="confirmarReserva" :disabled="enviando">
              {{ enviando ? 'Procesando...' : '✓ Confirmar reserva' }}
            </button>
          </div>
        </div>

      </div>

      <!-- COLUMNA DERECHA: RESUMEN -->
      <div class="summary-col">

        <!-- HABITACIÓN -->
        <div class="room-preview">
          <div class="room-img" :class="habitacion.tipo">
            <span>{{ emojiTipo(habitacion.tipo) }}</span>
          </div>
          <div class="room-preview-info">
            <div class="room-tipo">{{ habitacion.tipo?.toUpperCase() }}</div>
            <div class="room-nombre">{{ habitacion.descripcion || 'Habitación ' + habitacion.numero }}</div>
            <div class="room-feats">
              <span>👤 {{ habitacion.capacidad }} pers.</span>
              <span>📶 WiFi</span>
              <span>❄️ A/C</span>
            </div>
          </div>
        </div>

        <!-- RESUMEN DE PRECIO -->
        <div class="precio-resumen">
          <h4>📄 Resumen de reserva</h4>
          <div class="precio-row">
            <span>Check-in</span>
            <span>{{ reserva.fechaEntrada ? formatFecha(reserva.fechaEntrada) : '—' }}</span>
          </div>
          <div class="precio-row">
            <span>Check-out</span>
            <span>{{ reserva.fechaSalida ? formatFecha(reserva.fechaSalida) : '—' }}</span>
          </div>
          <div class="precio-row">
            <span>Noches</span>
            <span class="gold">{{ noches || '—' }}</span>
          </div>
          <div class="precio-row">
            <span>Precio/noche</span>
            <span>${{ habitacion.precio_noche }}</span>
          </div>
          <div class="precio-row">
            <span>Subtotal</span>
            <span>${{ subtotal }}</span>
          </div>
          <div class="precio-row">
            <span>Impuestos (13%)</span>
            <span>${{ impuestos }}</span>
          </div>
          <div class="precio-total-box">
            <span>Precio total</span>
            <span class="precio-total-valor">${{ precioTotal }}</span>
          </div>
          <div class="noches-label">{{ noches }} noche(s) · {{ reserva.huespedes }} huésped(es)</div>
        </div>

        <div class="seguridad">
          🔒 Reserva segura con autenticación JWT
        </div>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReservaView',

  data() {
    return {
      cargando: false,
      enviando: false,
      error: '',
      errorPaso: '',
      exitoReserva: '',
      pasoActual: 1,
      habitacion: {},
      reserva: {
        fechaEntrada: '',
        fechaSalida: '',
        huespedes: 1
      },
      huesped: {
        nombre: '',
        apellido: '',
        email: '',
        telefono: '',
        solicitudes: ''
      }
    }
  },

  computed: {
    hoy() {
      return new Date().toISOString().split('T')[0]
    },

    noches() {
      if (!this.reserva.fechaEntrada || !this.reserva.fechaSalida) return 0
      const entrada = new Date(this.reserva.fechaEntrada)
      const salida  = new Date(this.reserva.fechaSalida)
      const diff = (salida - entrada) / (1000 * 60 * 60 * 24)
      return diff > 0 ? diff : 0
    },

    subtotal() {
      return (this.noches * (this.habitacion.precio_noche || 0)).toFixed(2)
    },

    impuestos() {
      return (this.subtotal * 0.13).toFixed(2)
    },

    precioTotal() {
      return (Number(this.subtotal) + Number(this.impuestos)).toFixed(2)
    }
  },

  mounted() {
    // Verificar que el usuario esté logueado
    const token = localStorage.getItem('token')
    if (!token) {
      this.$router.push('/login')
      return
    }

    // Prellenar datos del huésped si están en localStorage
    this.huesped.nombre = localStorage.getItem('nombre') || ''
    this.huesped.email  = localStorage.getItem('email')  || ''

    // Cargar habitación por ID desde la URL
    const id = this.$route.params.id
    this.cargarHabitacion(id)
  },

  methods: {
    async cargarHabitacion(id) {
      this.cargando = true
      this.error = ''
      try {
        const respuesta = await fetch(`http://localhost:8000/api/habitaciones/${id}`)
        if (!respuesta.ok) throw new Error('Habitación no encontrada')
        this.habitacion = await respuesta.json()
        this.reserva.huespedes = 1
      } catch (err) {
        this.error = 'No se pudo cargar la información de la habitación.'
      } finally {
        this.cargando = false
      }
    },

    siguientePaso() {
      this.errorPaso = ''

      if (this.pasoActual === 1) {
        if (!this.reserva.fechaEntrada || !this.reserva.fechaSalida) {
          this.errorPaso = 'Por favor selecciona las fechas de entrada y salida.'
          return
        }
        if (this.noches <= 0) {
          this.errorPaso = 'La fecha de salida debe ser posterior a la de entrada.'
          return
        }
      }

      if (this.pasoActual === 2) {
        if (!this.huesped.nombre || !this.huesped.apellido || !this.huesped.email) {
          this.errorPaso = 'Por favor completa los campos obligatorios.'
          return
        }
        if (!this.huesped.email.includes('@')) {
          this.errorPaso = 'El correo electrónico no es válido.'
          return
        }
      }

      this.pasoActual++
    },

    async confirmarReserva() {
      this.enviando = true
      this.errorPaso = ''

      try {
        const token = localStorage.getItem('token')
        const respuesta = await fetch('http://localhost:8000/api/reservas', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            habitacion_id: this.habitacion.id,
            fecha_entrada: this.reserva.fechaEntrada,
            fecha_salida:  this.reserva.fechaSalida,
            precio_total:  Number(this.precioTotal)
          })
        })

        const datos = await respuesta.json()

        if (!respuesta.ok) {
          this.errorPaso = datos.detail || 'Error al crear la reserva.'
          return
        }

        this.exitoReserva = '¡Reserva confirmada exitosamente! Redirigiendo...'
        setTimeout(() => {
          this.$router.push('/mis-reservas')
        }, 2000)

      } catch (err) {
        this.errorPaso = 'No se pudo conectar con el servidor. Intenta más tarde.'
      } finally {
        this.enviando = false
      }
    },

    formatFecha(fecha) {
      if (!fecha) return '—'
      const [anio, mes, dia] = fecha.split('-')
      const meses = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
      return `${dia} ${meses[Number(mes) - 1]} ${anio}`
    },

    emojiTipo(tipo) {
      const emojis = { simple: '🛏️', doble: '🛏️', suite: '👑' }
      return emojis[tipo] || '🏨'
    }
  }
}
</script>

<style scoped>
.reserva-page {
  background-color: #0a0a0a;
  min-height: 100vh;
  color: #ffffff;
  padding-bottom: 3rem;
}

.gold { color: #C9A84C; }

/* ── BREADCRUMB ── */
.breadcrumb {
  background-color: #0d0d0d;
  border-bottom: 1px solid #1a1a1a;
  padding: 0.75rem 2rem;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #444444;
}

.breadcrumb a {
  color: #555555;
  text-decoration: none;
}

.breadcrumb a:hover { color: #C9A84C; }
.breadcrumb .active { color: #C9A84C; }

/* ── CARGANDO / ERROR ── */
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

.error-msg {
  background-color: #1a0a0a;
  border: 1px solid #3a1a1a;
  color: #EF5350;
  padding: 1.25rem 2rem;
  margin: 2rem;
  border-radius: 10px;
  font-size: 13px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-volver {
  background-color: #C9A84C;
  color: #0a0a0a;
  padding: 7px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 12px;
  font-weight: 600;
}

/* ── CONTENEDOR PRINCIPAL ── */
.reserva-container {
  max-width: 1100px;
  margin: 2rem auto;
  padding: 0 2rem;
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

/* ── COLUMNA FORMULARIO ── */
.form-col {
  flex: 1;
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  padding: 1.75rem;
}

/* ── PASOS ── */
.steps {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.step-circle {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  background-color: #1a1a1a;
  border: 1px solid #2a2a2a;
  color: #444444;
}

.step.active .step-circle {
  background-color: #1a1a0a;
  border-color: #C9A84C;
  color: #C9A84C;
}

.step.done .step-circle {
  background-color: #C9A84C;
  border-color: #C9A84C;
  color: #0a0a0a;
}

.step span {
  font-size: 10px;
  color: #444444;
}

.step.active span { color: #ffffff; }
.step.done span   { color: #C9A84C; }

.step-line {
  flex: 1;
  height: 1px;
  background-color: #1e1e1e;
  margin: 0 8px;
  margin-bottom: 18px;
}

.step-line.done { background-color: #C9A84C; }

/* ── PASO ── */
.paso-titulo {
  font-size: 16px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 1.5rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  font-size: 10px;
  color: #C9A84C;
  font-weight: 600;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  background-color: #0d0d0d;
  border: 1px solid #1e1e1e;
  border-radius: 7px;
  padding: 9px 12px;
  font-size: 13px;
  color: #ffffff;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}

.field input:focus,
.field select:focus,
.field textarea:focus {
  border-color: #C9A84C;
}

.field select option { background-color: #0d0d0d; }
.field textarea { resize: vertical; }

.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.resumen-fechas {
  background-color: #0d1a0d;
  border: 1px solid #1a3a1a;
  border-radius: 7px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #66BB6A;
  margin-bottom: 1rem;
}

/* ── CONFIRMACIÓN ── */
.confirmacion-detalle {
  background-color: #0d0d0d;
  border: 1px solid #1e1e1e;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.conf-row {
  display: flex;
  justify-content: space-between;
  padding: 7px 0;
  border-bottom: 1px solid #1a1a1a;
  font-size: 13px;
}

.conf-row:last-child { border-bottom: none; }
.conf-label { color: #555555; }
.conf-value { color: #ffffff; }

.politica {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.25rem;
}

.politica h4 {
  font-size: 12px;
  color: #C9A84C;
  margin-bottom: 8px;
}

.politica p {
  font-size: 11px;
  color: #555555;
  margin-bottom: 4px;
}

/* ── BOTONES ── */
.btn-siguiente {
  width: 100%;
  background-color: #C9A84C;
  border: none;
  color: #0a0a0a;
  padding: 11px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 0.5rem;
  transition: background 0.2s;
}

.btn-siguiente:hover { background-color: #E8C97A; }

.btn-grupo {
  display: flex;
  gap: 10px;
  margin-top: 0.5rem;
}

.btn-atras {
  flex: 1;
  background: transparent;
  border: 1px solid #2a2a2a;
  color: #888888;
  padding: 11px;
  border-radius: 7px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-atras:hover {
  border-color: #C9A84C;
  color: #C9A84C;
}

.btn-confirmar {
  flex: 2;
  background-color: #C9A84C;
  border: none;
  color: #0a0a0a;
  padding: 11px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirmar:hover:not(:disabled) { background-color: #E8C97A; }
.btn-confirmar:disabled {
  background-color: #5a4a1e;
  color: #888888;
  cursor: not-allowed;
}

/* ── MENSAJES ── */
.error-inline {
  background-color: #2a0a0a;
  border: 1px solid #5a1a1a;
  color: #EF5350;
  padding: 10px 14px;
  border-radius: 7px;
  font-size: 12px;
  margin-bottom: 1rem;
}

.exito-msg {
  background-color: #0a2a0a;
  border: 1px solid #1a5a1a;
  color: #66BB6A;
  padding: 10px 14px;
  border-radius: 7px;
  font-size: 12px;
  margin-bottom: 1rem;
}

/* ── COLUMNA RESUMEN ── */
.summary-col {
  width: 300px;
  flex-shrink: 0;
  position: sticky;
  top: 80px;
}

.room-preview {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.room-img {
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  opacity: 0.6;
}

.room-img.simple { background-color: #0d1a1a; }
.room-img.doble  { background-color: #1a0d0d; }
.room-img.suite  { background-color: #1a1a0d; }

.room-preview-info { padding: 12px; }

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
  margin-bottom: 8px;
}

.room-feats {
  display: flex;
  gap: 10px;
  font-size: 11px;
  color: #555555;
}

.precio-resumen {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.precio-resumen h4 {
  font-size: 12px;
  color: #ffffff;
  margin-bottom: 1rem;
}

.precio-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 6px 0;
  border-bottom: 1px solid #1a1a1a;
  color: #555555;
}

.precio-row span:last-child { color: #ffffff; }

.precio-total-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1a1a0a;
  border: 1px solid #2a2010;
  border-radius: 8px;
  padding: 10px 12px;
  margin-top: 10px;
  font-size: 12px;
  color: #888888;
}

.precio-total-valor {
  font-size: 20px;
  font-weight: 500;
  color: #C9A84C;
}

.noches-label {
  font-size: 10px;
  color: #333333;
  text-align: center;
  margin-top: 6px;
}

.seguridad {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 8px;
  padding: 10px;
  font-size: 11px;
  color: #444444;
  text-align: center;
}

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .reserva-container {
    flex-direction: column;
    padding: 0 1rem;
  }

  .summary-col {
    width: 100%;
    position: static;
  }

  .row-2 {
    grid-template-columns: 1fr;
  }
}
</style>