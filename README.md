# MVP - Actualizador de PROYECTO.xlsx desde RFQ

Automatizacion local que lee archivos RFQ de `entrada/`, extrae los campos
clave y actualiza la hoja de seguimiento de `PROYECTO.xlsx` sin perder
formato, formulas, bordes ni filtros.

> **Fases del proyecto**
> - **Fase 1 (completa): motor local en Python.** Lee correos/RFQ, extrae,
>   actualiza el Excel conservando formato/formulas, evita duplicados y genera
>   bitacora. Se usa por CLI (`python main.py`).
> - **Fase 2 (en curso): sistema web basico con Django** que ENVUELVE el motor
>   de Fase 1 (no lo reescribe). Login, subir `.txt`, vista previa editable y
>   escritura confirmada al Excel, con historial en SQLite.
>
> El motor de Fase 1 (`config.py`, `src/`) queda intacto; Django lo reutiliza
> por import a traves de `seguimiento/services.py`.

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

## No versionar datos sensibles
`.gitignore` excluye: `PROYECTO.xlsx` y todo `*.xlsx/.xls/.xlsm`, `*.eml/.msg/.pdf/.docx/.txt`,
las carpetas `entrada/procesados/backups/reportes/muestras/media/`, y `db.sqlite3`.
Las migraciones (`seguimiento/migrations/*.py`) SI se versionan: son estructura, no datos.

## Config
Todo lo ajustable esta en `config.py` (rutas, hoja, columnas, formato de
fecha, marcado de faltantes, fuente del RFQ y mapeo de planta).
