<template>
  <nav class="navbar">
    <div class="navbar-container">

      <!-- LOGO -->
      <RouterLink to="/" class="nav-logo">
        <div class="nav-icon">
          <span>H</span>
        </div>
        <span class="nav-brand">Hotel<span class="gold">Reserve</span></span>
      </RouterLink>

      <!-- LINKS -->
      <div class="nav-links" :class="{ 'nav-open': menuAbierto }">
        <RouterLink to="/" class="nav-link" @click="cerrarMenu">Inicio</RouterLink>
        <RouterLink to="/habitaciones" class="nav-link" @click="cerrarMenu">Habitaciones</RouterLink>
        <RouterLink to="/mis-reservas" class="nav-link" @click="cerrarMenu">Mis reservas</RouterLink>
        <RouterLink to="/contacto" class="nav-link" @click="cerrarMenu">Contacto</RouterLink>

        <!-- Si el usuario está logueado -->
        <div v-if="usuarioLogueado" class="nav-usuario">
          <span class="nav-nombre">{{ nombreUsuario }}</span>
          <button class="btn-logout" @click="cerrarSesion">Cerrar sesión</button>
        </div>

        <!-- Si no está logueado -->
        <RouterLink v-else to="/login" class="btn-login" @click="cerrarMenu">
          Iniciar sesión
        </RouterLink>
      </div>

      <!-- MENU HAMBURGUESA (móvil) -->
      <button class="nav-hamburguesa" @click="toggleMenu" aria-label="Abrir menú">
        <span></span>
        <span></span>
        <span></span>
      </button>

    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar',

  data() {
    return {
      menuAbierto: false,
      usuarioLogueado: false,
      nombreUsuario: ''
    }
  },

  mounted() {
    // Verificar si hay un token guardado al cargar el componente
    const token = localStorage.getItem('token')
    const nombre = localStorage.getItem('nombre')
    if (token) {
      this.usuarioLogueado = true
      this.nombreUsuario = nombre || 'Usuario'
    }
  },

  methods: {
    toggleMenu() {
      this.menuAbierto = !this.menuAbierto
    },

    cerrarMenu() {
      this.menuAbierto = false
    },

    cerrarSesion() {
      localStorage.removeItem('token')
      localStorage.removeItem('nombre')
      this.usuarioLogueado = false
      this.nombreUsuario = ''
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.navbar {
  background-color: #111111;
  border-bottom: 1px solid #1e1e1e;
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* LOGO */
.nav-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
}

.nav-icon {
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

.nav-brand {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.gold {
  color: #C9A84C;
}

/* LINKS */
.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  font-size: 13px;
  color: #888888;
  text-decoration: none;
  transition: color 0.2s;
}

.nav-link:hover {
  color: #C9A84C;
}

.nav-link.router-link-active {
  color: #C9A84C;
  font-weight: 500;
}

/* BOTÓN LOGIN */
.btn-login {
  background: transparent;
  border: 1px solid #C9A84C;
  color: #C9A84C;
  padding: 7px 18px;
  border-radius: 6px;
  font-size: 12px;
  text-decoration: none;
  transition: all 0.2s;
}

.btn-login:hover {
  background-color: #C9A84C;
  color: #0a0a0a;
}

/* USUARIO LOGUEADO */
.nav-usuario {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-nombre {
  font-size: 13px;
  color: #C9A84C;
}

.btn-logout {
  background: transparent;
  border: 1px solid #2a2a2a;
  color: #888;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  border-color: #EF5350;
  color: #EF5350;
}

/* HAMBURGUESA (móvil) */
.nav-hamburguesa {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
}

.nav-hamburguesa span {
  display: block;
  width: 22px;
  height: 2px;
  background-color: #888;
  border-radius: 2px;
  transition: background 0.2s;
}

.nav-hamburguesa:hover span {
  background-color: #C9A84C;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .nav-hamburguesa {
    display: flex;
  }

  .nav-links {
    display: none;
    position: absolute;
    top: 60px;
    left: 0;
    right: 0;
    background-color: #111111;
    border-bottom: 1px solid #1e1e1e;
    flex-direction: column;
    align-items: flex-start;
    padding: 1rem 1.5rem;
    gap: 1rem;
  }

  .nav-links.nav-open {
    display: flex;
  }
}
</style>