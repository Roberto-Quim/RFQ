# MVP - Actualizador de PROYECTO.xlsx desde RFQ

Automatizacion local que lee archivos RFQ de `entrada/`, extrae los campos
clave y actualiza la hoja de seguimiento de `PROYECTO.xlsx` sin perder
formato, formulas, bordes ni filtros.

> **Fases del proyecto**
> - **Fase 1 (completa): motor local en Python.** Lee correos/RFQ, extrae,
>   actualiza el Excel conservando formato/formulas, evita duplicados y genera
>   bitacora. Se usa por CLI (`python main.py`).
> - **Fase 2 (completa): sistema web basico con Django** que ENVUELVE el motor
>   (no lo reescribe). Login, subir `.txt`, vista previa editable y escritura
>   confirmada al Excel, con historial en SQLite.
> - **Fase 3 (completa): endurecimiento para uso interno controlado.**
>   Configuracion por variables de entorno, ruta del Excel configurable, lock
>   de escritura, permisos por usuario, auditoria, pagina `/estado/` y logging.
>
> El motor de Fase 1 (`config.py`, `src/`) queda practicamente intacto (solo se
> le agrego lectura de rutas por variable de entorno con fallback al valor de
> siempre). Django lo reutiliza por import via `seguimiento/services.py`.

## Estructura real del maestro (PROYECTO.xlsx)
Confirmada al inspeccionar el archivo real:

- **Hoja:** `"SEGUIMIENTO "` — OJO: el nombre **termina con un ESPACIO**.
  (En `config.py` esta escrito con el espacio a proposito; no lo quites.)
- **Encabezados:** fila **2**.
- **Datos:** empiezan en la fila **3**.
- **Columnas gestionadas** (las unicas que escribe el motor):
  - A = RFQ, B = DESCRIPCION, C = FECHA DE ARRANQUE, D = SOLICITANTE, F = PLANTA.
- **Columnas O y P tienen formulas** (O = `IF(...)`, P = resta de fechas) y se
  repiten por fila. **No se escriben manualmente.** Al agregar una fila nueva,
  el motor copia y **ajusta** esas formulas a la fila nueva.

## Instalacion
```
pip install -r requirements.txt
```

## Uso
1. Coloca tu maestro real en `PROYECTO.xlsx` (raiz del proyecto).
2. **Primero** analiza su estructura:
   ```
   python inspeccionar.py
   ```
   Ajusta `config.py` (hoja, fila de encabezados, columnas) segun lo que reporte.
3. Deja archivos RFQ en `entrada/` (por ahora `.csv`; ver formatos abajo).
4. Ejecuta:
   ```
   python main.py
   ```
5. Revisa el reporte en `reportes/`.

## Como funciona
- Antes de escribir hace **backup** en `backups/`.
- Busca el RFQ en la columna A **desde la fila 3** (nunca toma el encabezado
  de la fila 2 como dato): si existe **actualiza** esa fila; si no, **agrega** al final.
- Solo toca columnas A, B, C, D, F. Las demas quedan intactas (incluidas O y P).
- RFQ siempre como texto (conserva `185`, `185.5`, `131/4`); fechas como fechas reales de Excel.
- Al **agregar** una fila nueva, hereda estilo/formato de la fila anterior y
  **ajusta las formulas de O y P** a la fila nueva (traductor de openpyxl).
- Guarda de forma atomica (temp + replace) para no corromper el archivo.
- Los archivos ya leidos se mueven a `procesados/`.

## Validacion
Prueba minima del motor (sin datos reales ni PROYECTO.xlsx):

```
python tests/test_motor.py
```

Verifica: RFQ desde PEDIDO #/Request #, RFQ como texto, no duplicar,
no tocar O/P al actualizar, y ajuste de formulas O/P al agregar filas.

## Formato CSV de entrada (funcional hoy)
Encabezados exactos:
```
rfq,descripcion,fecha_arranque,solicitante,planta
```
Fechas en `dd/mm/aaaa`. RFQ puede ser `185`, `185.5`, `131/4`.

## Extractores
`src/extractores/` — un plugin por tipo de archivo:
- `csv_manual.py` — funcional (carga manual/masiva).
- `excel_rfq.py` — plantilla adaptable para RFQ en Excel.
- `correo_formapprovals.py` — funcional. Correos "Form Approvals" (`.txt` / `.eml`).
- `pendientes.py` — PDF / Word (por implementar con archivos reales).

Para un formato nuevo: crea una subclase de `Extractor` y agregala a
`REGISTRO` en `src/extractores/__init__.py`.

## Regla de negocio: RFQ = numero de pedido
Confirmado con el area (Edith): en los correos Form Approvals, el **numero de
RFQ se toma del numero de pedido**.

- `PEDIDO #228`  -> se registra `RFQ = 228`.
- `Request #228` -> tambien se registra `RFQ = 228`.

Este es el comportamiento por defecto (`config.FUENTE_RFQ_CORREO = "pedido"`).
El RFQ se guarda siempre como **texto** en la columna A del maestro.

## Pendientes por confirmar con negocio
- **Fecha de arranque**: el correo Form Approvals NO la incluye. Falta definir
  de donde sale (se captura manual, viene en otro documento, o se usa la fecha
  del pedido). Hoy queda como faltante y se reporta en la bitacora.
- **Planta vs Unidad de Negocio**: falta confirmar si `Selecciona Unidad de
  Negocio` (ej. "Questum Maquinados Ramos") equivale directo a `Planta`, o si
  requiere un mapeo (ej. -> "Ramos Arizpe"). El mapeo opcional esta en
  `config.MAPA_UNIDAD_A_PLANTA` (vacio = se usa el valor tal cual).
## Fase 2 - Sistema web (Django)
Django **envuelve** el motor de Fase 1; no lo reescribe. Toda la interaccion
con el motor pasa por `seguimiento/services.py`.

Estructura anadida:

```text
manage.py
rfq_project/           # proyecto Django (settings, urls, wsgi, asgi)
seguimiento/           # app: models, forms, views, urls, services, admin, templates
  services.py          # UNICO puente Django <-> motor (Fase 1)
  templates/seguimiento/  subir_rfq / vista_previa / resultado / historial
  templates/registration/ login
```

Instalar y arrancar:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # crea TU usuario (no se versiona)
python manage.py runserver
```

Luego abre http://127.0.0.1:8000/ e inicia sesion.

Flujo web seguro (el Excel solo se escribe al confirmar):

1. Subir archivo `.txt` (correo Form Approvals).
2. El motor (`FormApprovalsExtractor`) extrae RFQ, descripcion, solicitante,
   planta; la fecha de arranque queda faltante.
3. Vista previa **editable** — aun NO se escribe nada.
4. El usuario revisa/corrige y confirma.
5. Se crea **backup** y se escribe en `PROYECTO.xlsx` via
   `excel_maestro.agregar_o_actualizar()` (solo A/B/C/D/F; O y P se conservan).
6. Se muestra el resultado (agregado/actualizado, backup, faltantes, errores)
   y se guarda el historial en SQLite (`RFQProcesado`).

Errores claros: si `PROYECTO.xlsx` o la hoja `"SEGUIMIENTO "` no existen, o si el
archivo esta abierto en Excel, la app lo indica y NO deja el maestro a medias.

Compatibilidad CLI (Fase 1 intacta):

```bash
python main.py                # motor por linea de comandos
python inspeccionar.py        # analisis del maestro
python tests/test_motor.py    # pruebas del motor
python tests/test_servicios.py    # pruebas del servicio web (sin BD)
python manage.py test seguimiento # pruebas de integracion web (BD de prueba)
```

## Fase 3 - Endurecimiento para uso interno
Mejoras de seguridad/configuracion/permisos/auditoria, sin despliegue final aun.

### Variables de entorno (.env)
Copia `.env.example` a `.env` (el `.env` real NO se versiona) y ajusta:

```bash
DJANGO_SECRET_KEY=<clave-larga>   # OBLIGATORIA si DJANGO_DEBUG=0
DJANGO_DEBUG=1                    # 0 en entorno compartido/produccion
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
RFQ_ARCHIVO_MAESTRO=C:\ruta\a\PROYECTO.xlsx   # ruta configurable del Excel
# Opcionales: RFQ_CARPETA_BACKUPS, RFQ_CARPETA_REPORTES, RFQ_MEDIA_ROOT, RFQ_LOGS_DIR
```

`config.py` lee estas rutas con **fallback** al valor de siempre, asi la CLI
(`python main.py`, `python inspeccionar.py`) sigue funcionando sin `.env`.

### Migrar y crear usuario

```bash
python manage.py migrate
python manage.py createsuperuser   # tu usuario admin (no se versiona)
```

### Permiso para confirmar escritura
Estar logueado permite subir y previsualizar. Para **confirmar** (escribir al
Excel) se necesita el permiso `seguimiento.puede_confirmar`. Recomendado por grupo:

1. Admin (`/admin/`) -> Grupos -> crea **"Confirmadores RFQ"** y asignale el
   permiso *"Puede confirmar escritura al Excel"*.
2. Agrega a ese grupo los usuarios autorizados.

Sin el permiso, la vista previa se ve pero el boton de confirmar no aparece y el
endpoint responde 403.

### Correr y revisar estado

```bash
python manage.py runserver        # http://127.0.0.1:8000/
```

- `/estado/` (requiere login): muestra si existen `PROYECTO.xlsx`, la hoja
  `"SEGUIMIENTO "`, carpetas `media/backups/reportes/logs`, si la BD responde y
  si `DEBUG=True`. **No** muestra `SECRET_KEY` ni datos sensibles.
- Escritura al Excel **serializada por lock** (`seguimiento/locking.py`): una a
  la vez. Es cooperativo (protege a la app; no impide que alguien edite el Excel
  a mano). Logs en `logs/rfq.log`.
- Auditoria: `RFQProcesado` guarda usuario, accion, campos faltantes, campos
  editados a mano, mensaje y error.

### Pruebas

```bash
python tests/test_motor.py         # Fase 1
python tests/test_servicios.py     # Fase 2 servicio (preview no escribe)
python manage.py test seguimiento  # Fase 2+3: permisos, estado, lock, auditoria
python manage.py check
```

## Fase 4 - Despliegue interno (Windows)
Deja el proyecto listo para correr como aplicacion interna en una PC de empresa,
sin cloud ni APIs de correo. Guia completa: **[docs/OPERACION.md](docs/OPERACION.md)**.

Resumen:

```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env            # editar: SECRET_KEY propia, DEBUG=0, ALLOWED_HOSTS, RFQ_ARCHIVO_MAESTRO
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py check_operativo  # valida DEBUG/SECRET_KEY/Excel/hoja/carpetas/BD/migraciones/permisos
python run_waitress.py            # servidor interno (host/puerto por env)
```

- `run_waitress.py`: sirve la app con **Waitress** (`RFQ_WAITRESS_HOST`/`RFQ_WAITRESS_PORT`).
- Estaticos servidos por **WhiteNoise** tras `collectstatic` (incluye `/admin/`).
- `check_operativo`: management command que valida el entorno; NO muestra `SECRET_KEY`.

## Fase 5 - Operacion persistente (Windows)
Deja el sistema listo para correr como servicio/tarea sin abrir la terminal cada vez.

- **Scripts** (`scripts/`): `iniciar_servidor.bat`/`.ps1`, `check_operativo.bat`,
  `migrar_y_collectstatic.bat`. Cada script activa `.venv`, corre el chequeo y arranca Waitress.
- **Arranque automatico**: guia de **Task Scheduler** y **NSSM** (sin instalar nada) en
  **[scripts/README_OPERACION_WINDOWS.md](scripts/README_OPERACION_WINDOWS.md)**.
- **Operacion diaria** (iniciar/detener/reiniciar, logs, backups, Excel bloqueado,
  restaurar backup, checklist): **[docs/OPERACION_DIARIA.md](docs/OPERACION_DIARIA.md)**.
- **Logs rotativos**: `logs/rfq.log`, 5 MB por archivo, 5 backups (stdlib `RotatingFileHandler`).
- **Monitoreo compacto**: `python manage.py check_operativo --simple` (una linea, ideal para `.bat`).

## No versionar datos sensibles
`.gitignore` excluye: `PROYECTO.xlsx` y todo `*.xlsx/.xls/.xlsm`, `*.eml/.msg/.pdf/.docx/.txt`,
las carpetas `entrada/procesados/backups/reportes/muestras/media/logs/`, `db.sqlite3` y `.env`.
Las migraciones (`seguimiento/migrations/*.py`) SI se versionan: son estructura, no datos.
El archivo `.env.example` (valores ficticios) SI se versiona.

## Config
Todo lo ajustable esta en `config.py` (rutas, hoja, columnas, formato de
fecha, marcado de faltantes, fuente del RFQ y mapeo de planta).
