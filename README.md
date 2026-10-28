# Práctica 1 — Bloque 1: Ingesta de datos académicos (ITACA)

Ingesta de los XML exportados del sistema ITACA del centro CIPFP MISLATA hacia una arquitectura medallion (`raw` → `silver` → `gold`). Scripts en Python, solo librería estándar.

## 1. Fuentes de datos

- **Mecanismo de acceso**: exportaciones XML de ITACA, una por curso académico (2021-22 a 2025-26, carpeta `Analisis_Academico/<curso>/`). Cada exportación trae 4 ficheros, uno por tabla — `alumnos.xml`, `cursos.xml`, `calificaciones.xml`, `contenidos.xml` — con cabecera común `<centro ... curso="AAAA" fechaExportacion="...">`, de donde se saca el campo `Anyo` (no del nombre de la carpeta).
- **Frecuencia de actualización esperada**: snapshot anual por curso (renovación con las matrículas y reposición al cierre de las evaluaciones); aquí la fuente es estática y el pipeline es idempotente (re-ejecutar regenera la salida).
- **Campos disponibles**: los extraídos a raw (mapeo del apartado 2) y el resto del modelo en el apartado 4; en raw se guardan tal cual, como string.

## 2. Pipeline de ingesta

1. `listar_carpetas_raw.py` — lista las carpetas de curso de la fuente, las crea en `data/raw/` y genera `data/raw/carpetas_analisis_academico.json`.
2. `ingestar_xml_raw.py` — por cada curso lee los 4 XML, extrae el `Anyo` de la cabecera, mapea los campos y escribe un `.json` por tabla (con intros) en `data/raw/<curso>/`.

```text
Analisis_Academico/<curso>/{alumnos,cursos,calificaciones,contenidos}.xml
     │  (ingestar_xml_raw.py: parseo + Anyo de cabecera + NIA anonimizado)
     ▼
data/raw/<curso>/{alumnos,cursos,calificaciones,contenidos}.json
```

- **Anonimización de NIA** (Alumnos y Calificaciones): SHA-256 truncado a 10 caracteres, determinista, para conservar el cruce entre tablas: `hashlib.sha256(str(nia).encode()).hexdigest()[:10]`.
- **Volumen**: 116.108 registros en total (7.193 alumnos, 413 cursos, 106.814 calificaciones, 1.688 contenidos).

## 3. Estructura del proyecto

```text
Practica_1_Bloque_1_resolved/
├── Analisis_Academico/      # FUENTE: <curso>/ (2021-22 ... 2025-26) con los 4 XML
├── data/
│   ├── raw/                 # RAW: <curso>/{alumnos,calificaciones,contenidos,cursos}.json
│   ├── silver/              # pendiente: tipado, limpieza
│   └── gold/                # pendiente: métricas de explotación
├── listar_carpetas_raw.py   # paso 1 del pipeline
├── ingestar_xml_raw.py      # paso 2 del pipeline
├── Prompt General.txt       # enunciado (tablas y campos a extraer)
└── .venv/                   # entorno virtual Python 3.14
```

## 4. Modelo relacional de origen (caso real ITACA) 

Cuatro tablas: **Alumnos**, **Contenidos**, **Calificaciones** y **Cursos**.

| Tabla          |                           Campos                                              |
|----------------|-------------------------------------------------------------------------------|
| Alumnos        | Anyo, PrimSeg, Ciclo, Grado, Familia, Turno, Grupo, Curso (string); NIA (int) |
| Contenidos     | Anyo, Curso, Modulo, Nombre_Modulo (string)                                   |
| Calificaciones | Anyo, Curso, Modulo, Evaluacion (string); NIA (int); Nota (float)             |
| Cursos         | Anyo, Codigo, Nombre_Cas, Nombre_Val, Padre (string; jerarquía de cursos)     |

Claves de negocio: `NIA` cruza Alumnos ↔ Calificaciones; `Modulo` cruza Calificaciones ↔ Contenidos; el catálogo `Cursos` es jerárquico vía `Padre`; la partición natural es `Anyo` (los tipos indicados se aplican en silver, raw va sin tipar).

## 5. Cómo ejecutar

```powershell
.\.venv\Scripts\python.exe .\listar_carpetas_raw.py
.\.venv\Scripts\python.exe .\ingestar_xml_raw.py
```
