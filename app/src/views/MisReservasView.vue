<template>
  <div class="mis-reservas-page">

    <!-- ENCABEZADO -->
    <div class="page-header">
      <div class="header-content">
        <h1>Mis <span class="gold">Reservas</span></h1>
        <p>Gestiona todas tus reservas desde aquí</p>
      </div>
      <RouterLink to="/habitaciones" class="btn-nueva">
        + Nueva reserva
      </RouterLink>
    </div>

    <!-- TABS DE ESTADO -->
    <div class="tabs-bar">
      <button
        v-for="tab in tabs"
        :key="tab.valor"
        class="tab"
        :class="{ active: tabActivo === tab.valor }"
        @click="tabActivo = tab.valor"
      >
        {{ tab.label }}
        <span class="tab-count">{{ contarPorEstado(tab.valor) }}</span>
      </button>
    </div>

    <!-- CONTENIDO -->
    <div class="reservas-container">

      <!-- CARGANDO -->
      <div v-if="cargando" class="cargando">
        <div class="spinner"></div>
        <p>Cargando tus reservas...</p>
      </div>

      <!-- ERROR -->
      <div v-else-if="error" class="error-msg">
        ⚠️ {{ error }}
        <button @click="cargarReservas" class="btn-reintentar">Reintentar</button>
      </div>

      <!-- SIN RESERVAS -->
      <div v-else-if="reservasFiltradas.length === 0" class="sin-reservas">
        <span class="sin-emoji">🏨</span>
        <h3>No tienes reservas {{ tabActivo !== 'todas' ? tabActivo + 's' : '' }}</h3>
        <p>¿Listo para planear tu próxima estadía?</p>
        <RouterLink to="/habitaciones" class="btn-explorar">
          Explorar habitaciones
        </RouterLink>
      </div>

      <!-- LISTA DE RESERVAS -->
      <div v-else class="reservas-lista">
        <div
          v-for="reserva in reservasFiltradas"
          :key="reserva.id"
          class="reserva-card"
          :class="reserva.estado"
        >
          <!-- LADO IZQUIERDO -->
          <div class="reserva-img" :class="reserva.habitacion?.tipo">
            <span>{{ emojiTipo(reserva.habitacion?.tipo) }}</span>
          </div>

          <!-- INFO PRINCIPAL -->
          <div class="reserva-info">
            <div class="reserva-header">
              <div>
                <div class="reserva-tipo">
                  {{ reserva.habitacion?.tipo?.toUpperCase() || 'HABITACIÓN' }}
                </div>
                <div class="reserva-nombre">
                  {{ reserva.habitacion?.descripcion || 'Habitación ' + reserva.habitacion_id }}
                </div>
              </div>
              <div class="estado-badge" :class="reserva.estado">
                {{ labelEstado(reserva.estado) }}
              </div>
            </div>

            <div class="reserva-fechas">
              <div class="fecha-item">
                <span class="fecha-label">CHECK-IN</span>
                <span class="fecha-valor">{{ formatFecha(reserva.fecha_entrada) }}</span>
              </div>
              <div class="fecha-flecha">→</div>
              <div class="fecha-item">
                <span class="fecha-label">CHECK-OUT</span>
                <span class="fecha-valor">{{ formatFecha(reserva.fecha_salida) }}</span>
              </div>
              <div class="fecha-item">
                <span class="fecha-label">NOCHES</span>
                <span class="fecha-valor gold">{{ calcularNoches(reserva.fecha_entrada, reserva.fecha_salida) }}</span>
              </div>
            </div>

            <div class="reserva-footer">
              <div class="reserva-precio">
                ${{ reserva.precio_total }}
                <span>precio total</span>
              </div>
              <div class="reserva-id">
                ID: #{{ reserva.id?.slice(0, 8) }}
              </div>
              <div class="reserva-acciones">
                <button
                  v-if="reserva.estado === 'pendiente' || reserva.estado === 'confirmada'"
                  class="btn-cancelar"
                  @click="confirmarCancelacion(reserva)"
                >
                  Cancelar
                </button>
                <button class="btn-detalle" @click="verDetalle(reserva)">
                  Ver detalle
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- MODAL DETALLE -->
    <div v-if="reservaSeleccionada" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Detalle de reserva</h3>
          <button class="modal-cerrar" @click="cerrarModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="detalle-row">
            <span>ID de reserva</span>
            <span>#{{ reservaSeleccionada.id }}</span>
          </div>
          <div class="detalle-row">
            <span>Habitación</span>
            <span>{{ reservaSeleccionada.habitacion?.descripcion || 'Habitación ' + reservaSeleccionada.habitacion_id }}</span>
          </div>
          <div class="detalle-row">
            <span>Tipo</span>
            <span class="gold">{{ reservaSeleccionada.habitacion?.tipo?.toUpperCase() }}</span>
          </div>
          <div class="detalle-row">
            <span>Check-in</span>
            <span>{{ formatFecha(reservaSeleccionada.fecha_entrada) }}</span>
          </div>
          <div class="detalle-row">
            <span>Check-out</span>
            <span>{{ formatFecha(reservaSeleccionada.fecha_salida) }}</span>
          </div>
          <div class="detalle-row">
            <span>Noches</span>
            <span>{{ calcularNoches(reservaSeleccionada.fecha_entrada, reservaSeleccionada.fecha_salida) }}</span>
          </div>
          <div class="detalle-row">
            <span>Estado</span>
            <span class="estado-badge" :class="reservaSeleccionada.estado">
              {{ labelEstado(reservaSeleccionada.estado) }}
            </span>
          </div>
          <div class="detalle-row">
            <span>Precio total</span>
            <span class="gold">${{ reservaSeleccionada.precio_total }}</span>
          </div>
          <div class="detalle-row">
            <span>Fecha de creación</span>
            <span>{{ formatFecha(reservaSeleccionada.created_at) }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cerrar-modal" @click="cerrarModal">Cerrar</button>
        </div>
      </div>
    </div>

    <!-- MODAL CONFIRMAR CANCELACIÓN -->
    <div v-if="reservaACancelar" class="modal-overlay" @click.self="reservaACancelar = null">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>¿Cancelar reserva?</h3>
          <button class="modal-cerrar" @click="reservaACancelar = null">✕</button>
        </div>
        <div class="modal-body">
          <p style="color:#888;font-size:13px;line-height:1.6">
            Estás a punto de cancelar la reserva
            <strong style="color:#fff">
              #{{ reservaACancelar.id?.slice(0, 8) }}
            </strong>.
            Esta acción no se puede deshacer.
          </p>
        </div>
        <div class="modal-footer" style="gap:10px">
          <button class="btn-cerrar-modal" @click="reservaACancelar = null">
            No, mantener
          </button>
          <button class="btn-confirmar-cancelar" @click="cancelarReserva" :disabled="cancelando">
            {{ cancelando ? 'Cancelando...' : 'Sí, cancelar' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'MisReservasView',

  data() {
    return {
      cargando: false,
      cancelando: false,
      error: '',
      reservas: [],
      tabActivo: 'todas',
      reservaSeleccionada: null,
      reservaACancelar: null,
      tabs: [
        { label: 'Todas',      valor: 'todas' },
        { label: 'Pendientes', valor: 'pendiente' },
        { label: 'Confirmadas',valor: 'confirmada' },
        { label: 'Canceladas', valor: 'cancelada' },
      ]
    }
  },

  computed: {
    reservasFiltradas() {
      if (this.tabActivo === 'todas') return this.reservas
      return this.reservas.filter(r => r.estado === this.tabActivo)
    }
  },

  mounted() {
    const token = localStorage.getItem('token')
    if (!token) {
      this.$router.push('/login')
      return
    }
    this.cargarReservas()
  },

  methods: {
    async cargarReservas() {
      this.cargando = true
      this.error = ''
      try {
        const token = localStorage.getItem('token')
        const respuesta = await fetch('http://localhost:8000/api/reservas/usuario/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (!respuesta.ok) throw new Error('Error al cargar reservas')
        this.reservas = await respuesta.json()
      } catch (err) {
        this.error = 'No se pudieron cargar tus reservas. Verifica que el servidor esté activo.'
      } finally {
        this.cargando = false
      }
    },

    async cancelarReserva() {
      this.cancelando = true
      try {
        const token = localStorage.getItem('token')
        const respuesta = await fetch(
          `http://localhost:8000/api/reservas/${this.reservaACancelar.id}/cancelar`,
          {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${token}` }
          }
        )
        if (!respuesta.ok) throw new Error('Error al cancelar')

        // Actualizar estado localmente sin recargar
        const idx = this.reservas.findIndex(r => r.id === this.reservaACancelar.id)
        if (idx !== -1) this.reservas[idx].estado = 'cancelada'
        this.reservaACancelar = null

      } catch (err) {
        this.error = 'No se pudo cancelar la reserva. Intenta más tarde.'
      } finally {
        this.cancelando = false
      }
    },

    contarPorEstado(estado) {
      if (estado === 'todas') return this.reservas.length
      return this.reservas.filter(r => r.estado === estado).length
    },

    calcularNoches(entrada, salida) {
      if (!entrada || !salida) return 0
      const diff = (new Date(salida) - new Date(entrada)) / (1000 * 60 * 60 * 24)
      return diff > 0 ? diff : 0
    },

    formatFecha(fecha) {
      if (!fecha) return '—'
      const [anio, mes, dia] = fecha.split('T')[0].split('-')
      const meses = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
      return `${dia} ${meses[Number(mes) - 1]} ${anio}`
    },

    labelEstado(estado) {
      const labels = {
        pendiente:  '⏳ Pendiente',
        confirmada: '✅ Confirmada',
        cancelada:  '✕ Cancelada'
      }
      return labels[estado] || estado
    },

    emojiTipo(tipo) {
      const emojis = { simple: '🛏️', doble: '🛏️', suite: '👑' }
      return emojis[tipo] || '🏨'
    },

    verDetalle(reserva) {
      this.reservaSeleccionada = reserva
    },

    cerrarModal() {
      this.reservaSeleccionada = null
    },

    confirmarCancelacion(reserva) {
      this.reservaACancelar = reserva
    }
  }
}
</script>

<style scoped>
.mis-reservas-page {
  background-color: #0a0a0a;
  min-height: 100vh;
  color: #ffffff;
  padding-bottom: 3rem;
}

.gold { color: #C9A84C; }

/* ── ENCABEZADO ── */
.page-header {
  background-color: #111111;
  border-bottom: 1px solid #1e1e1e;
  padding: 1.75rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 4px;
}

.page-header p {
  font-size: 13px;
  color: #555555;
}

.btn-nueva {
  background-color: #C9A84C;
  color: #0a0a0a;
  padding: 9px 20px;
  border-radius: 7px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-nueva:hover { background-color: #E8C97A; }

/* ── TABS ── */
.tabs-bar {
  background-color: #0d0d0d;
  border-bottom: 1px solid #1a1a1a;
  padding: 0 2rem;
  display: flex;
  gap: 0;
}

.tab {
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #555555;
  padding: 1rem 1.25rem;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.tab:hover { color: #C9A84C; }

.tab.active {
  color: #C9A84C;
  border-bottom-color: #C9A84C;
}

.tab-count {
  background-color: #1a1a1a;
  border-radius: 10px;
  padding: 1px 7px;
  font-size: 11px;
  color: #888888;
}

.tab.active .tab-count {
  background-color: #2a1e08;
  color: #C9A84C;
}

/* ── CONTENEDOR ── */
.reservas-container {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 0 2rem;
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

/* ── SIN RESERVAS ── */
.sin-reservas {
  text-align: center;
  padding: 5rem 2rem;
  color: #555555;
}

.sin-emoji { font-size: 52px; }

.sin-reservas h3 {
  font-size: 20px;
  color: #ffffff;
  margin: 1rem 0 0.5rem;
}

.sin-reservas p {
  font-size: 13px;
  margin-bottom: 1.5rem;
}

.btn-explorar {
  background-color: #C9A84C;
  color: #0a0a0a;
  padding: 10px 24px;
  border-radius: 7px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
}

/* ── LISTA DE RESERVAS ── */
.reservas-lista {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.reserva-card {
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  transition: border-color 0.2s;
}

.reserva-card:hover { border-color: #2a2a2a; }
.reserva-card.cancelada { opacity: 0.6; }

/* IMAGEN LATERAL */
.reserva-img {
  width: 90px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}

.reserva-img.simple { background-color: #0d1a1a; }
.reserva-img.doble  { background-color: #1a0d0d; }
.reserva-img.suite  { background-color: #1a1a0d; }

/* INFO */
.reserva-info {
  flex: 1;
  padding: 1rem 1.25rem;
}

.reserva-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.reserva-tipo {
  font-size: 10px;
  color: #C9A84C;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 3px;
}

.reserva-nombre {
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
}

/* ESTADO BADGE */
.estado-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.estado-badge.pendiente {
  background-color: #1a1a08;
  border: 1px solid #3a3a10;
  color: #FFA726;
}

.estado-badge.confirmada {
  background-color: #0a1a0a;
  border: 1px solid #1a3a1a;
  color: #66BB6A;
}

.estado-badge.cancelada {
  background-color: #1a0a0a;
  border: 1px solid #3a1a1a;
  color: #EF5350;
}

/* FECHAS */
.reserva-fechas {
  display: flex;
  align-items: center;
  gap: 1rem;
  background-color: #0d0d0d;
  border: 1px solid #1a1a1a;
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 0.75rem;
}

.fecha-item {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.fecha-label {
  font-size: 9px;
  color: #444444;
  font-weight: 600;
  letter-spacing: 1px;
}

.fecha-valor {
  font-size: 13px;
  color: #ffffff;
  font-weight: 500;
}

.fecha-flecha {
  color: #333333;
  font-size: 16px;
}

/* FOOTER */
.reserva-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reserva-precio {
  font-size: 20px;
  font-weight: 500;
  color: #C9A84C;
}

.reserva-precio span {
  font-size: 11px;
  color: #555555;
  font-weight: 400;
  margin-left: 4px;
}

.reserva-id {
  font-size: 11px;
  color: #333333;
  font-family: monospace;
}

.reserva-acciones {
  display: flex;
  gap: 8px;
}

.btn-cancelar {
  background: transparent;
  border: 1px solid #3a1a1a;
  color: #EF5350;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancelar:hover {
  background-color: #1a0a0a;
}

.btn-detalle {
  background: transparent;
  border: 1px solid #2a2a2a;
  color: #888888;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-detalle:hover {
  border-color: #C9A84C;
  color: #C9A84C;
}

/* ── MODAL ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background-color: #111111;
  border: 1px solid #2a2a2a;
  border-radius: 14px;
  width: 100%;
  max-width: 480px;
}

.modal-sm { max-width: 380px; }

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #1e1e1e;
}

.modal-header h3 {
  font-size: 15px;
  font-weight: 500;
  color: #ffffff;
}

.modal-cerrar {
  background: transparent;
  border: none;
  color: #555555;
  font-size: 16px;
  cursor: pointer;
}

.modal-cerrar:hover { color: #ffffff; }

.modal-body {
  padding: 1.25rem 1.5rem;
}

.detalle-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #1a1a1a;
  font-size: 13px;
  color: #555555;
}

.detalle-row:last-child { border-bottom: none; }
.detalle-row span:last-child { color: #ffffff; }

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #1e1e1e;
  display: flex;
  justify-content: flex-end;
}

.btn-cerrar-modal {
  background: transparent;
  border: 1px solid #2a2a2a;
  color: #888888;
  padding: 8px 20px;
  border-radius: 7px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cerrar-modal:hover {
  border-color: #C9A84C;
  color: #C9A84C;
}

.btn-confirmar-cancelar {
  background-color: #EF5350;
  border: none;
  color: #ffffff;
  padding: 8px 20px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirmar-cancelar:hover:not(:disabled) {
  background-color: #c62828;
}

.btn-confirmar-cancelar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .reserva-card {
    flex-direction: column;
  }

  .reserva-img {
    width: 100%;
    height: 80px;
  }

  .reserva-fechas {
    flex-wrap: wrap;
  }

  .reserva-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>