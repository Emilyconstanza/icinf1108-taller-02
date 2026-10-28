# Avance de Isidora

Este avance corresponde al repositorio `icinf1108-taller-02`, cuya API administra estudiantes y mascotas. El plan de avance adjunto propone clientes, servicios, profesionales y citas; como esas rutas no existen en este repositorio, las pruebas y el diagrama se ajustan al código disponible y dejan la diferencia documentada para que el equipo confirme cuál pauta aplica.

| Tarea de documentación y pruebas | Estado | Evidencia |
| --- | --- | --- |
| Diagrama de entidades y relación | Completado | [`diagrama-estudiantes-mascotas.md`](diagrama-estudiantes-mascotas.md) |
| Casos reproducibles de API | Completado | `tests/test_students_api.py` y [`pruebas.md`](../pruebas.md) |
| Resultado real de pruebas | Se registra tras ejecutar la suite | `pruebas.md` |
| Variables de entorno sin secretos | Completado | [`.env.example`](../.env.example) |
| README alineado con Docker, persistencia y rutas | Completado | [`README.md`](../README.md) |
| Confirmar con el grupo la pauta/domino que corresponde a este repositorio | Pendiente | El documento adjunto trata de agenda; este código trata de estudiantes y mascotas |

Las pruebas automatizadas usan una base SQLite efímera. No prueban el arranque de Docker ni la persistencia sobre PostgreSQL. El proyecto no contiene migraciones Alembic y el Compose actual levanta PostgreSQL y pgAdmin, pero no la API.
