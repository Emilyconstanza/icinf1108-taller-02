# Matriz de pruebas de estudiantes

Los casos se reproducen con `uv run pytest`. La suite crea tablas en una base SQLite temporal y las elimina al terminar. No se usan datos ni credenciales de PostgreSQL.

| ID | Entrada | Resultado esperado | Resultado obtenido | Estado |
| --- | --- | --- | --- | --- |
| ST-01 | Crear estudiante con una mascota anidada | HTTP 201; ambos registros quedan en las tablas ORM | HTTP 201; se consultaron estudiante y mascota en SQLite | Aprobado |
| ST-02 | Listar estudiantes con `limit=1&offset=1` | HTTP 200; entrega el registro de la página solicitada | HTTP 200; se obtuvo un elemento | Aprobado |
| ST-03 | Repetir un correo ya registrado | HTTP 409 | HTTP 409 | Aprobado |
| ST-04 | Enviar correo con formato inválido | HTTP 400 | HTTP 400 | Aprobado |
| ST-05 | Consultar un UUID inexistente | HTTP 404 | HTTP 404 | Aprobado |
| ST-06 | Enviar dos mascotas con igual nombre en una solicitud | HTTP 409; estudiante no queda guardado | HTTP 409; estudiantes y mascotas quedaron en cero | Aprobado |
| ST-07 | Simular un error de integridad al persistir una mascota | HTTP 409; la transacción revierte estudiante y mascota | HTTP 409; estudiantes y mascotas quedaron en cero tras rollback | Aprobado |
| ST-08 | Solicitar `limit=0` | HTTP 400 por parámetro inválido | HTTP 400 | Aprobado |

Ejecución: `uv run pytest -q` — 8 aprobadas. Se usó SQLite temporal; PostgreSQL, Docker y persistencia tras reinicio no se probaron en esta ejecución.
