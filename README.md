# CRUD Students & Pets (FastAPI)

Proyecto FastAPI para administrar estudiantes y mascotas. La creación de un estudiante junto con sus mascotas se guarda en PostgreSQL mediante una única transacción SQLAlchemy.

## Tecnologías

- Python 3.13
- FastAPI, SQLAlchemy y PostgreSQL
- Repositorios en memoria para las rutas de mascotas existentes
- HTML + JS + Tailwind CSS (frontend estático)

## Resumen funcional

La API expone CRUD de estudiantes y mascotas. La creación de un estudiante y sus mascotas anidadas usa PostgreSQL y una transacción SQLAlchemy. Las rutas CRUD independientes de mascotas todavía usan almacenamiento en memoria; no deben confundirse con la persistencia de la operación anidada.

**Estudiantes** — `/api/students`

- **Crear**: `POST /api/students` (opcionalmente con `pets[]` para crear el estudiante y sus mascotas en una sola petición)
- **Listar**: `GET /api/students`
- **Buscar por id**: `GET /api/students/:id`
- **Actualizar**: `PATCH /api/students/:id`
- **Eliminar**: `DELETE /api/students/:id` (elimina al estudiante y sus mascotas persistidas en la base de datos)

**Mascotas (almacenamiento en memoria)** — `/api/students/:studentId/pets`

- **Listar**: `GET /api/students/:studentId/pets`
- **Crear**: `POST /api/students/:studentId/pets`
- **Actualizar**: `PATCH /api/students/:studentId/pets/:petId`
- **Eliminar**: `DELETE /api/students/:studentId/pets/:petId`

### Alta de estudiante con mascotas

`POST /api/students` acepta un arreglo opcional `pets`:

```json
{
	"name": "Ana Pérez",
	"email": "ana@example.com",
	"pets": [
		{ "name": "Firulais", "species": "perro", "age": 3 },
		{ "name": "Michi", "species": "gato" }
	]
}
```

Si no se envía `pets` (o se envía vacío), se crea únicamente el estudiante.

> **Transacción:** el endpoint agrega el estudiante, obtiene su ID con `flush()`, agrega las mascotas y confirma una sola vez con `commit()`. Si ocurre un error, ejecuta `rollback()` para que no queden cambios parciales. Los nombres de mascotas repetidos en el mismo envío se rechazan con HTTP 409.

### Modelo de datos

| Estudiante SQL (`students`) | Mascota SQL (`pets`) |
| --------------------------- | -------------------- |
| id (UUID en texto)          | id (UUID en texto)   |
| name                        | student_id (FK)      |
| email (único, opcional)     | name                 |
|                             | species              |
|                             | age (opcional)       |

La relación ORM permite varias mascotas por estudiante y elimina las mascotas asociadas cuando se elimina el estudiante. En cambio, las rutas independientes de mascotas usan un repositorio en memoria.

### Validación y unicidad

La validación se realiza con Pydantic v2:

- `name` (estudiante): texto obligatorio.
- `email` (estudiante): dirección válida y opcional.
- `name` y `species` (mascota): texto entre 1 y 50 caracteres, sin etiquetas HTML.
- `age` (mascota): entero entre 0 y 100, opcional.

Unicidad (rechazado con `409 Conflict`):

- Estudiante: `email` es único cuando se informa.
- En una solicitud de alta: los nombres de mascotas no pueden repetirse.
- El esquema ORM también declara el nombre de mascota único por estudiante.

## Estándar de respuesta JSON

Toda respuesta de la API — exitosa o de error — usa el mismo **envelope** `ApiResponse`, definido en [`app/shared/api_response.py`](app/shared/api_response.py). Esto permite que el frontend interprete cualquier respuesta de forma uniforme.

### Envelope común

| Campo       | Tipo                | Descripción                                                               |
| ----------- | ------------------- | ------------------------------------------------------------------------- |
| `code`      | `number`            | Código de estado HTTP (coincide con el status de la respuesta).           |
| `success`   | `boolean`           | `true` si la operación se completó, `false` si hubo error.                |
| `message`   | `string`            | Resumen legible del resultado (varía según el método HTTP).               |
| `timestamp` | `string`            | Fecha/hora en ISO 8601 de la respuesta.                                   |
| `data`      | `object \| null`    | Datos de la operación. Presente en éxito; `null` en errores.              |
| `error`     | `string` (opcional) | Mensaje de error para errores simples (404, 500).                         |
| `errors`    | `object` (opcional) | Errores por campo para validación (400) y conflicto (409). Ver más abajo. |

### Respuestas de éxito

Un middleware global ([`api_response.py`](app/shared/api_response.py)) envuelve el retorno de los controladores en `data`:

- **Recurso único** (`GET :id`, `POST`, `PATCH`, `DELETE`): `data` contiene la entidad directamente.
- **Listado** (`GET` colección): `data` contiene `{ total, items }`.

```json
{
  "code": 201,
  "success": true,
  "message": "Recurso creado",
  "timestamp": "2026-09-09T16:49:33.368Z",
  "data": {
    "id": "c3600646-abe8-4be3-8096-d6ad629388e2",
    "name": "Juan Pérez",
    "email": "juan@example.com"
  }
}
```

`message` según el método HTTP:

| Método   | `message`             | `code` |
| -------- | --------------------- | ------ |
| `GET`    | `Operación exitosa`   | 200    |
| `POST`   | `Recurso creado`      | 201    |
| `PATCH`  | `Recurso actualizado` | 200    |
| `DELETE` | `Recurso eliminado`   | 200    |

### Errores simples (404, 500)

Los errores sin detalle por campo usan el campo `error`:

```json
{
  "code": 404,
  "success": false,
  "message": "Estudiante no encontrado",
  "timestamp": "2026-09-09T16:49:53.816Z",
  "data": null,
  "error": "Estudiante no encontrado"
}
```

### Validación (400) y conflicto (409)

Ambos casos comparten el **mismo esquema** para que el frontend los trate igual: el campo `errors` es un mapa `{ campo: { message } }`, donde la clave es el nombre del campo que falla.

```json
{
  "code": 400,
  "success": false,
  "message": "Error de validación",
  "timestamp": "2026-09-09T16:39:30.397Z",
  "data": null,
  "errors": {
    "name": { "message": "El nombre debe tener entre 3 y 100 caracteres" },
    "email": { "message": "El correo electrónico no es válido" }
  }
}
```

```json
{
  "code": 409,
  "success": false,
  "message": "Conflicto con datos existentes",
  "timestamp": "2026-09-09T16:49:45.110Z",
  "data": null,
  "errors": {
    "email": { "message": "El correo electrónico ya está en uso" }
  }
}
```

- `400 Bad Request`: cuando falla la validación de entrada. El handler global ([`exceptions.py`](app/shared/exceptions.py)) convierte los errores al mapa `{ campo: { message } }` (si un campo falla varias reglas, los mensajes se concatenan con `", "`).
- `409 Conflict`: cuando se viola una restricción de unicidad. Los servicios lanzan una `HTTPException` con el mismo mapa `errors`, por lo que es indistinguible de una validación a nivel de estructura.

### Interpretación en el frontend

El cliente estático (`public/`) consume este estándar de forma uniforme:

- `public/js/api.js` expone `api()` (hace `fetch` y devuelve `data` en éxito o lanza el envelope en error) y `normalizeErrors()` (convierte `{ campo: { message } }` en `{ campo: message }`).
- En los formularios, si la respuesta trae `errors`, cada mensaje se muestra bajo su input correspondiente; si trae `error`, se muestra como notificación global (toast).

## Contexto técnico y Dockerización
- Backend: FastAPI
- Persistencia: Base de datos relacional PostgreSQL 15 en contenedor Docker
- Administrador Visual: pgAdmin 4 en contenedor Docker accesible vía navegador web
- ORM & Migraciones: SQLAlchemy con Alembic para el control de versiones de la base de datos
- Variables de Entorno: Configuración segura mediante archivo `.env`
- Validación: Pydantic v2
- Frontend: archivos estáticos en public/ (Alpine.js + Tailwind CSS + vanilla-sonner, vía CDN)
- Gestor de dependencias: uv
- Documentación: Swagger en /docs

## Ejecución con Docker (Recomendado)

1. Copiar `.env.example` a `.env` y cambiar las claves de ejemplo para uso local.
2. Iniciar PostgreSQL y pgAdmin con `docker compose up -d`.
3. Instalar dependencias con `uv sync --group dev`.
4. Configurar `DATABASE_URL` en la terminal donde se ejecutará la API. En PowerShell, por ejemplo: `$env:DATABASE_URL = "postgresql://postgres:CAMBIAR_CLAVE@localhost:5432/taller_db"`.
5. Iniciar la API con `make dev`; abre Swagger en `http://localhost:3000/docs`.

Compose inicia PostgreSQL y pgAdmin, no la API. La aplicación no ejecuta migraciones automáticamente; la creación del esquema debe prepararse antes de usar las rutas persistidas.

Las variables de `.env` son consumidas por Docker Compose. La aplicación lee `DATABASE_URL` del entorno del proceso y no carga `.env` automáticamente.

## Pruebas

Instala las dependencias de desarrollo y ejecuta `uv run pytest`. La matriz de casos y sus resultados actuales están en [`pruebas.md`](pruebas.md). Las pruebas usan SQLite temporal y no requieren la base PostgreSQL local.

El diagrama y el estado de las tareas de Isidora están en [`docs/diagrama-estudiantes-mascotas.md`](docs/diagrama-estudiantes-mascotas.md) y [`docs/avance-isidora.md`](docs/avance-isidora.md).
## Comandos útiles

- `make install` — sincroniza dependencias con uv
- `make dev` — arranca uvicorn en modo reload
- `make lint` — ejecuta Ruff (con autocorrección)
- `make format` — formatea el código con Ruff
- `make format-check` — verifica el formato
- `make clean` — elimina `.venv`, cachés y artefactos

## Migraciones de base de datos

Alembic administra el esquema PostgreSQL para estudiantes y mascotas. Antes de
crear o aplicar migraciones, configura `DATABASE_URL` en el entorno o en un
archivo `.env` en la raíz del proyecto. Por ejemplo:

```text
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/estudiantes
```

Los modelos ORM definen las tablas `students` y `pets`, su relación uno-a-muchos,
las restricciones de unicidad y la eliminación en cascada. Para crear y aplicar
una migración:

```bash
uv run alembic revision --autogenerate -m "Migracion inicial de modelos y relaciones"
uv run alembic upgrade head
```

La API actual todavía utiliza repositorios en memoria; estas migraciones crean
el esquema de base de datos, pero no cambian aún la persistencia de los
endpoints.
