# 🛸 SmartOps Life ERP (VIVID OS)
> **Resumen del Sistema y Funcionalidad Core**

SmartOps Life ERP es un **"HUD Táctico"** y un sistema inteligente de planificación financiera (Personal ERP) diseñado bajo una estética inmersiva de consola Matrix/Cyberpunk. Su objetivo es integrar la gestión de operaciones (Agencia de IA, Casino, Side Hustles) con un motor financiero estricto.

---

## 💻 1. Arquitectura Técnica
- **Frontend (UI/UX):** Streamlit (Python). Personalizado profundamente vía Inyección CSS para emular una terminal de consola ("Cockpit Layout").
- **Backend (API Base):** FastAPI (Python). Expone endpoints modulares y ejecuta las reglas del negocio.
- **Base de Datos:** PostgreSQL.
- **Infraestructura:** Docker Compose (Contenedores) desplegado en un VPS de DigitalOcean, gestionado a través de NGINX Proxy Manager.

---

## ⚡ 2. El Motor Estocástico Financiero ("The Power Engine")

La característica clave del sistema es la automatización de presupuestos diarios y el rastreo de deudas mediante un esquema de gamificación (Boss Raids). 

El sistema orbita alrededor del factor **Daily Power**:
* `Daily Power = Presupuesto Semanal Total / 6 días (Lunes a Sábado)`.
* Determina cuánto dinero puede gastar el usuario hoy sin comprometer sus objetivos de ahorro o pago de deudas.

### Estados Lógicos (State-Machine)
Dependiendo de la salud financiera del usuario, el sistema actúa bajo dos protocolos en segundo plano:

1. **[ MODO_GUERRA ] (Deuda > $0):**
    - Si el usuario genera "Ingresos Extra", durante el `Monday Reset`, el excedente es distribuido agresivamente: 
    - **70%** destinado a atacar el `Debt_Boss_Raid` (Pago de deudas).
    - **30%** inyectado como `Next_Week_Buff` (Aumenta tu *Daily Power* la siguiente semana para mantener moral).
    
2. **[ MODO_EXPANSION ] (Deuda == $0):**
    - El usuario está libre de amenazas. Los ingresos se ramifican a la construcción de riqueza:
    - **30%** inyectado a `Next_Week_Buff`.
    - **30%** guardado automáticamente en el `Luxury_Vault` (Recreación/Viajes).
    - **40%** inyectado directamente al `Investment_Vault`.

---

## 🎮 3. Módulos de la Interfaz (Terminal HUD)

La interfaz se despliega como un panel táctico de navegación lateral (`SYSTEM_NAV`):

### `[01] TERMINAL` (Centro de Comando)
- Incluye métricas vitales, como el perfil interactivo del Arquitecto y el Status Online (`OPERATIONAL`).
- **[ DAILY_POWER ]:** Muestra el saldo actual del día mediante una barra ASCII reactiva que pulsa en verde.
- Si hay penalizaciones por sobregiro, el contenedor "pulsa" en Magenta Cyber (`#FF007A`) y entra en `[ PENALTY_MODE ]`.
- **[ INPUT_CMD ]:** El componente donde se registran Incomes (Ingresos), Expenses (Gastos), Apartados (Guardar dinero) y Defenses (Pagar Deuda). Incluye el motor Failsafe que **evita gastar de un Apartado/Vault sin saldo suficiente**.
- **[ DAILY_POWER_PROJECTION ]:** Un *forecast* o predicción algorítmica de como se comportará tu Daily Power durante los próximos 14 días.

### `[02] DASHBOARD` (Analítica Visual - En Construcción Fase 2)
- Revisa flujos de salida mediante simuladores gráficos basados en caracteres (ASCII Graphics) segmentados por días (`WEEK_FOCUS`).

### `[03] CRM_OPS` / `[04] VAULTS` / `[05] BOSS_RAID` (Fases Sucesivas)
- Trazabilidad de proyectos (Casino, Inteligencia Artificial), asignación de bóvedas dinámicas (como "Vault Fanny" y "Familia"), y el listado de las amenazas activas con sus "Barras de Puntos de Vida (HP)".

---

## 🤖 4. Protocolos y Automatizaciones (A Futuro)
El ERP evolucionará con *Smart Suggestions* que reaccionan orgánicamente a los datos:
- **Burnout Alert:** Sugiere utilizar el "Luxury Vault" si el usuario pasa >15 días sin transacciones recreativas pero factura fuertemente en Operations.
- **Runway Tracker:** Indicador global de "Meses de Supervivencia" basado en el cálculo del Total Ahorrado entre el ritmo de Gastos Mensuales.
