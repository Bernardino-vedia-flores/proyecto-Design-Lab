<template>
  <div class="auth-page">
    <div class="auth-container">

      <!-- PANEL IZQUIERDO -->
      <div class="left-panel">
        <RouterLink to="/" class="logo">
          <div class="logo-icon">H</div>
          <span class="logo-brand">Hotel<span class="gold">Reserve</span></span>
        </RouterLink>

        <div class="left-content">
          <h2>Bienvenido de vuelta a tu <span class="gold">estancia ideal</span></h2>
          <p>Accede a tu cuenta para gestionar tus reservas, ver el historial y más.</p>
          <div class="perks">
            
            <div class="perk">
              <div class="perk-icon">📅</div>
              <span>Gestiona tus reservas fácilmente</span>
            </div>
            <div class="perk">
              <div class="perk-icon">✅</div>
              <span>Confirmaciones al instante</span>
            </div>
            <div class="perk">
              <div class="perk-icon">🛡️</div>
              <span>Datos protegidos y privados</span>
            </div>
          </div>
        </div>

        <p class="left-footer">© 2026 HotelReserve · Sucre, Bolivia</p>
      </div>

      <!-- PANEL DERECHO -->
      <div class="right-panel">

        <!-- TABS -->
        <div class="tabs">
          <button
            class="tab"
            :class="{ active: tabActivo === 'login' }"
            @click="tabActivo = 'login'"
          >
            Iniciar sesión
          </button>
          <button
            class="tab"
            :class="{ active: tabActivo === 'registro' }"
            @click="tabActivo = 'registro'"
          >
            Crear cuenta
          </button>
        </div>

        <!-- FORMULARIO LOGIN -->
        <div v-if="tabActivo === 'login'" class="form-section">
          <h3 class="form-title">Iniciar sesión</h3>
          <p class="form-sub">Ingresa tus credenciales para continuar</p>

          <div v-if="errorLogin" class="error-msg">{{ errorLogin }}</div>

          <div class="field">
            <label>CORREO ELECTRÓNICO</label>
            <input
              v-model="login.email"
              type="email"
              placeholder="tucorreo@email.com"
              @keyup.enter="iniciarSesion"
            />
          </div>

          <div class="field">
            <label>CONTRASEÑA</label>
            <input
              v-model="login.password"
              type="password"
              placeholder="••••••••"
              @keyup.enter="iniciarSesion"
            />
          </div>

          <div class="forgot">
            <a href="#">¿Olvidaste tu contraseña?</a>
          </div>

          <button class="btn-primary" @click="iniciarSesion" :disabled="cargando">
            {{ cargando ? 'Ingresando...' : 'Iniciar sesión' }}
          </button>

          
        </div>

        <!-- FORMULARIO REGISTRO -->
        <div v-if="tabActivo === 'registro'" class="form-section">
          <h3 class="form-title">Crear cuenta</h3>
          <p class="form-sub">Completa los datos para registrarte</p>

          <div v-if="errorRegistro" class="error-msg">{{ errorRegistro }}</div>
          <div v-if="exitoRegistro" class="exito-msg">{{ exitoRegistro }}</div>

          <div class="row-2">
            <div class="field">
              <label>NOMBRE</label>
              <input v-model="registro.nombre" type="text" placeholder="Juan" />
            </div>
            <div class="field">
              <label>APELLIDO</label>
              <input v-model="registro.apellido" type="text" placeholder="Pérez" />
            </div>
          </div>

          <div class="field">
            <label>CORREO ELECTRÓNICO</label>
            <input v-model="registro.email" type="email" placeholder="tucorreo@email.com" />
          </div>

          <div class="field">
            <label>CONTRASEÑA</label>
            <input v-model="registro.password" type="password" placeholder="Mínimo 8 caracteres" />
          </div>

          <div class="field">
            <label>CONFIRMAR CONTRASEÑA</label>
            <input v-model="registro.confirmar" type="password" placeholder="Repite tu contraseña" />
          </div>

          <button class="btn-primary" @click="registrarse" :disabled="cargando">
            {{ cargando ? 'Creando cuenta...' : 'Crear cuenta' }}
          </button>

          <p class="terms">
            Al registrarte aceptas nuestros
            <a href="#">Términos de servicio</a> y
            <a href="#">Política de privacidad</a>
          </p>

          <p class="switch-text">
            ¿Ya tienes cuenta?
            <a @click="tabActivo = 'login'">Inicia sesión</a>
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginRegistro',

  data() {
    return {
      tabActivo: 'login',
      cargando: false,

      // Datos del formulario de login
      login: {
        email: '',
        password: ''
      },

      // Datos del formulario de registro
      registro: {
        nombre: '',
        apellido: '',
        email: '',
        password: '',
        confirmar: ''
      },

      // Mensajes
      errorLogin: '',
      errorRegistro: '',
      exitoRegistro: ''
    }
  },

  methods: {
    // ── VALIDACIONES ──────────────────────────────
    validarLogin() {
      if (!this.login.email || !this.login.password) {
        this.errorLogin = 'Por favor completa todos los campos.'
        return false
      }
      if (!this.login.email.includes('@')) {
        this.errorLogin = 'El correo electrónico no es válido.'
        return false
      }
      this.errorLogin = ''
      return true
    },

    validarRegistro() {
      if (!this.registro.nombre || !this.registro.apellido || !this.registro.email || !this.registro.password) {
        this.errorRegistro = 'Por favor completa todos los campos.'
        return false
      }
      if (!this.registro.email.includes('@')) {
        this.errorRegistro = 'El correo electrónico no es válido.'
        return false
      }
      if (this.registro.password.length < 8) {
        this.errorRegistro = 'La contraseña debe tener al menos 8 caracteres.'
        return false
      }
      if (this.registro.password !== this.registro.confirmar) {
        this.errorRegistro = 'Las contraseñas no coinciden.'
        return false
      }
      this.errorRegistro = ''
      return true
    },

    // ── INICIAR SESIÓN ────────────────────────────
    async iniciarSesion() {
      if (!this.validarLogin()) return

      this.cargando = true
      try {
        const respuesta = await fetch('http://localhost:8000/api/usuarios/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: this.login.email,
            password: this.login.password
          })
        })

        const datos = await respuesta.json()

        if (!respuesta.ok) {
          this.errorLogin = datos.detail || 'Credenciales incorrectas.'
          return
        }

        // Guardar token y nombre en localStorage
        localStorage.setItem('token', datos.token)
        localStorage.setItem('nombre', datos.nombre)

        // Redirigir a la página principal
        this.$router.push('/')

      } catch (error) {
        this.errorLogin = 'No se pudo conectar con el servidor. Intenta más tarde.'
      } finally {
        this.cargando = false
      }
    },

    // ── REGISTRARSE ───────────────────────────────
    async registrarse() {
      if (!this.validarRegistro()) return

      this.cargando = true
      try {
        const respuesta = await fetch('http://localhost:8000/api/usuarios/registro', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nombre: this.registro.nombre,
            apellido: this.registro.apellido,
            email: this.registro.email,
            password: this.registro.password
          })
        })

        const datos = await respuesta.json()

        if (!respuesta.ok) {
          this.errorRegistro = datos.detail || 'Error al crear la cuenta.'
          return
        }

        // Mostrar mensaje de éxito y cambiar al tab de login
        this.exitoRegistro = '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.'
        setTimeout(() => {
          this.tabActivo = 'login'
          this.exitoRegistro = ''
        }, 2000)

      } catch (error) {
        this.errorRegistro = 'No se pudo conectar con el servidor. Intenta más tarde.'
      } finally {
        this.cargando = false
      }
    }
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background-color: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-container {
  display: flex;
  width: 100%;
  max-width: 900px;
  background-color: #111111;
  border: 1px solid #1e1e1e;
  border-radius: 16px;
  overflow: hidden;
  min-height: 560px;
}

/* ── PANEL IZQUIERDO ── */
.left-panel {
  width: 42%;
  background-color: #0d0d0d;
  border-right: 1px solid #1e1e1e;
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  margin-bottom: 2.5rem;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background-color: #C9A84C;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  color: #0a0a0a;
}

.logo-brand {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.gold {
  color: #C9A84C;
}

.left-content h2 {
  font-size: 20px;
  font-weight: 500;
  color: #ffffff;
  line-height: 1.4;
  margin-bottom: 0.75rem;
}

.left-content p {
  font-size: 12px;
  color: #555555;
  line-height: 1.7;
  margin-bottom: 1.5rem;
}

.perks {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.perk {
  display: flex;
  align-items: center;
  gap: 10px;
}

.perk-icon {
  width: 28px;
  height: 28px;
  background-color: #1a1a0a;
  border: 1px solid #2a2a10;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
}

.perk span {
  font-size: 12px;
  color: #888888;
}

.left-footer {
  font-size: 10px;
  color: #333333;
  margin-top: 2rem;
}

/* ── PANEL DERECHO ── */
.right-panel {
  flex: 1;
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
}

.tabs {
  display: flex;
  background-color: #0d0d0d;
  border: 1px solid #1e1e1e;
  border-radius: 8px;
  padding: 3px;
  margin-bottom: 1.75rem;
}

.tab {
  flex: 1;
  padding: 8px;
  text-align: center;
  font-size: 12px;
  border-radius: 6px;
  cursor: pointer;
  color: #555555;
  background: transparent;
  border: none;
  transition: all 0.2s;
}

.tab.active {
  background-color: #C9A84C;
  color: #0a0a0a;
  font-weight: 600;
}

/* ── FORMULARIO ── */
.form-title {
  font-size: 18px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 4px;
}

.form-sub {
  font-size: 12px;
  color: #555555;
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

.field input {
  width: 100%;
  background-color: #0d0d0d;
  border: 1px solid #1e1e1e;
  border-radius: 7px;
  padding: 9px 12px;
  font-size: 13px;
  color: #ffffff;
  outline: none;
  transition: border-color 0.2s;
}

.field input:focus {
  border-color: #C9A84C;
}

.field input::placeholder {
  color: #333333;
}

.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.forgot {
  text-align: right;
  margin-top: -6px;
  margin-bottom: 1rem;
}

.forgot a {
  font-size: 11px;
  color: #C9A84C;
  text-decoration: none;
  cursor: pointer;
}

.btn-primary {
  width: 100%;
  background-color: #C9A84C;
  border: none;
  color: #0a0a0a;
  padding: 11px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 1rem;
  transition: background 0.2s;
}

.btn-primary:hover {
  background-color: #E8C97A;
}

.btn-primary:disabled {
  background-color: #5a4a1e;
  color: #888;
  cursor: not-allowed;
}

.switch-text {
  text-align: center;
  font-size: 12px;
  color: #444444;
  margin-top: 0.75rem;
}

.switch-text a {
  color: #C9A84C;
  cursor: pointer;
  text-decoration: none;
}

.terms {
  font-size: 10px;
  color: #333333;
  text-align: center;
  margin-top: 0.5rem;
  line-height: 1.6;
}

.terms a {
  color: #555555;
  text-decoration: none;
}

/* ── MENSAJES ── */
.error-msg {
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

/* ── RESPONSIVE ── */
@media (max-width: 640px) {
  .auth-container {
    flex-direction: column;
  }

  .left-panel {
    width: 100%;
    padding: 1.5rem;
    border-right: none;
    border-bottom: 1px solid #1e1e1e;
  }

  .perks {
    display: none;
  }
}
</style>