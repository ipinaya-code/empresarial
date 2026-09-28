"""Entrada histórica. La prueba reproducible vive en tests/postgres/test_integrity.py.

Ejecutar `make test-postgres` sobre una base descartable llamada boa_test.
El control negativo crea una tabla aislada; nunca retira restricciones de la aplicación.
"""
