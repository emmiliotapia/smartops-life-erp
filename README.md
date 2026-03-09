# SmartOps Life ERP

Este es el repositorio principal para **SmartOps Life ERP**, un sistema modular basado en microservicios diseñado para la gestión personal (LifeOS).

## 🚀 Despliegue en VPS

La aplicación ha sido configurada y desplegada exitosamente en el servidor VPS de producción.

### Detalles de la Instalación

- **Ubicación en el servidor:** `~/smartops-internal/smartops-life-erp`
- **Gestión de contenedores:** Docker Compose

### 🔧 Puertos Configurados

Durante el despliegue se identificaron colisiones con los puertos predeterminados en el VPS. Por esta razón, se han reasignado los puertos externos de la siguiente manera para evitar conflictos con otros servicios (`smartops-postgres` y `smartops_casino`):

- **[Frontend (Streamlit) UI]** -> Puerto: `8505` (Accesible en `http://164.92.110.179:8505`)
- **[Backend (FastAPI) API]** -> Puerto: `8005` (Accesible en `http://164.92.110.179:8005`)
- **[pgAdmin (Gestor de BD)]** -> Puerto: `5055` (Accesible en `http://164.92.110.179:5055`)
- **[Base de Datos (PostgreSQL)]** -> Puerto: `5435`

### 🛠️ Comandos de Utilidad (VPS)

Si necesitas reiniciar o actualizar los servicios en el servidor, utiliza los siguientes comandos (estando dentro de la ruta `~/smartops-internal/smartops-life-erp`):

**Reconstruir y levantar los contenedores en segundo plano:**
```bash
docker-compose up -d --build
```

**Ver los logs en tiempo real:**
```bash
docker-compose logs -f
```

**Bajar los servicios:**
```bash
docker-compose down
```

## 📦 Tecnologías

- **Frontend:** Python (Streamlit)
- **Backend:** Python (FastAPI)
- **Base de Datos:** PostgreSQL + `pgvector`
- **Infraestructura:** Docker + Docker Compose
