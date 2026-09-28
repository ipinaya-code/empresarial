# Contribución

Trabajar desde la rama base acordada por el equipo; ramas `feat/`, `fix/`, `docs/` o `chore/`. No depender de una rama `objetivo_2` que puede no existir. Commits con prefijo descriptivo, por ejemplo `fix: proteger unicidad de reservas activas`.

```bash
make setup PYTHON=python3.12
make format
make check
make test-postgres  # cuando cambia persistencia o concurrencia
```

No basta con SQLite para validar transacciones PostgreSQL. Ejecutar la base descartable del README y conservar JUnit. Para cambios de navegador: `make browser-install` y `make test-browser` con API levantada. Para cambios de rendimiento: comparar ambas variantes y conservar resultados crudos.

Los cambios de esquema incluyen una migración revisada. Los cambios de alcance se reflejan en plan y matriz de trazabilidad. No marcar tareas completas por la sola existencia de un archivo, ni introducir métricas inventadas. Revisión por otro integrante antes de merge; configurar protección de rama y checks requeridos en GitHub al publicar.

Dependencias canónicas: `pyproject.toml`; regenerar locks con Python 3.12 y pip-tools 7.6.1:

```bash
pip-compile --strip-extras -o requirements.lock pyproject.toml
pip-compile --strip-extras --extra=dev -o requirements-dev.lock pyproject.toml
pip-compile --strip-extras --extra=dev --extra=browser -o requirements-browser.lock pyproject.toml
```

Verificar instalación en entorno limpio y correr CI. No editar locks a mano para cambiar versiones. Los rangos permiten planificar actualizaciones; las instalaciones usan versiones fijadas. Se conserva la licencia MIT que ya declaraba el proyecto; ver [LICENSE](LICENSE).
