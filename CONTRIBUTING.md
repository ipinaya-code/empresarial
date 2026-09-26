# Guía de Contribución — Sistema de Reservas BoA

Gracias por contribuir al proyecto. Esta guía establece las convenciones del equipo para que todos los participantes puedan colaborar de forma eficiente.

## 📋 Requisitos Previos

- Python 3.11+
- Docker o Podman
- Git

## 🚀 Configuración Inicial

```bash
# 1. Clonar el repositorio
git clone https://github.com/ipinaya-code/empresarial.git
cd empresarial

# 2. Crear entorno virtual e instalar dependencias
make setup

# 3. Activar el entorno virtual
source .venv/bin/activate

# 4. Copiar la configuración de ejemplo
cp .env.example .env

# 5. Levantar el entorno Docker
make compose-up

# 6. Inicializar datos de demostración
make seed
```

## 🌿 Flujo de Trabajo con Git

### Branches

| Branch | Propósito |
|--------|-----------|
| `main` | Código estable y revisado |
| `objetivo_2` | Rama de desarrollo para el objetivo 2 |
| `feature/<nombre>` | Nuevas funcionalidades |
| `fix/<nombre>` | Corrección de bugs |
| `chore/<nombre>` | Mantenimiento, CI/CD, docs |

### Convención de Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: agregar endpoint de búsqueda de vuelos
fix: corregir race condition en reserva provisional
docs: actualizar diagrama de secuencia
test: agregar tests de integración para expiración
chore: actualizar dependencias de pip
refactor: separar lógica de reservas en servicio
```

### Pull Requests

1. Crear una branch desde `objetivo_2` (o `main`):
   ```bash
   git checkout -b feature/mi-feature objetivo_2
   ```

2. Hacer commits siguiendo la convención.

3. Ejecutar linting y tests antes de push:
   ```bash
   make lint
   make test
   ```

4. Crear el PR en GitHub y completar el template.

## 📁 Estructura del Proyecto

```
app/
├── core/          # Configuración, excepciones, logging
├── models/        # Modelos SQLAlchemy (tablas de BD)
├── schemas/       # Schemas Pydantic (validación de datos)
├── services/      # Lógica de negocio
├── api/v1/        # Routers de FastAPI (endpoints HTTP)
├── db/            # Sesión de BD y caché Valkey
└── main.py        # App factory
```

### ¿Dónde va cada cosa?

| Cambio | Ubicación |
|--------|-----------|
| Nuevo campo en la BD | `app/models/` |
| Validación de datos | `app/schemas/` |
| Lógica de negocio | `app/services/` |
| Nuevo endpoint HTTP | `app/api/v1/` |
| Variable de config | `app/core/config.py` + `.env.example` |

## 🧪 Tests

```bash
make test              # Todos los tests
make test-unit         # Solo unitarios
make test-integration  # Solo integración
make test-e2e          # Solo end-to-end
make stress-test       # Pruebas de carga (requiere k6)
```

## 🎨 Estilo de Código

- **Formatter:** Black (120 chars)
- **Linter:** Ruff
- **Type checker:** MyPy (opcional por ahora)

```bash
make format   # Formatear automáticamente
make lint     # Verificar estilo
```

## 👥 Responsables por Área (CODEOWNERS)

| Área | Responsable | Épica |
|------|------------|-------|
| Control transaccional, modelos, BD | Iver Pinaya | Epic 1 |
| Arquitectura CQRS, API, DevOps | Thiago Sossa | Epic 2 |
| Caché Valkey, configuración | Nataly Crespo | Epic 3 |
| Tests, QA, pruebas de estrés | Wilson Gonzales | Epic 4 |

## ❓ Preguntas

Si tienes dudas sobre la arquitectura o el flujo de trabajo, consulta la documentación en `/docs/` o abre un Issue en GitHub.
