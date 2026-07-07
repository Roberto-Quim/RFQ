# Operacion - Despliegue interno (Fase 4)

Guia para ejecutar el sistema RFQ como aplicacion interna en una PC/laptop de
empresa (Windows), sin cloud ni APIs de correo.

> No subir datos reales: `PROYECTO.xlsx`, backups, reportes, correos, `.env`,
> `db.sqlite3`, `media/`, `logs/`, `staticfiles/` estan ignorados por Git.

---

## 1. Instalacion desde cero (Windows)

```bat
cd C:\x\proyectos\RFQ

:: Entorno virtual
python -m venv .venv
.venv\Scripts\activate

:: Dependencias
pip install -r requirements.txt
```

## 2. Configurar el entorno (.env)

Copia la plantilla y edita valores reales (el `.env` NO se versiona):

```bat
copy .env.example .env
```

Genera una `SECRET_KEY`:

```bat
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

Edita `.env`:

- `DJANGO_SECRET_KEY` = la clave generada (no la de ejemplo).
- `DJANGO_DEBUG=0` para uso interno.
- `DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,NOMBRE-PC,IP-LOCAL`
  (agrega el nombre de la PC y su IP local si otras maquinas la usaran).
- `RFQ_ARCHIVO_MAESTRO=C:\ruta\controlada\PROYECTO.xlsx` (ubicacion controlada).
- Opcional: `RFQ_CARPETA_BACKUPS`, `RFQ_CARPETA_REPORTES`, `RFQ_MEDIA_ROOT`,
  `RFQ_LOGS_DIR`.
- `RFQ_WAITRESS_HOST` (127.0.0.1 solo local; 0.0.0.0 accesible en la LAN),
  `RFQ_WAITRESS_PORT`.

## 3. Base de datos y usuario admin

```bat
python manage.py migrate
python manage.py createsuperuser
```

## 4. Permiso para confirmar escritura al Excel

Estar logueado permite subir y previsualizar. Para **confirmar** (escribir al
Excel) se requiere el permiso `seguimiento.puede_confirmar`:

1. Entra a `/admin/` con el superusuario.
2. **Grupos** -> crea `Confirmadores RFQ` y asignale el permiso
   *"Puede confirmar escritura al Excel"*.
3. Agrega a ese grupo los usuarios autorizados.

Sin el permiso, el usuario ve la vista previa pero no puede escribir (boton
oculto; el endpoint responde 403).

## 5. Archivos estaticos

```bat
python manage.py collectstatic --noinput
```

WhiteNoise sirve los estaticos (incluido el admin) bajo Waitress.

## 6. Ejecutar

Desarrollo (recarga automatica, DEBUG):

```bat
python manage.py runserver
```

Uso interno (Waitress):

```bat
python run_waitress.py
```

Lee `RFQ_WAITRESS_HOST` / `RFQ_WAITRESS_PORT` del entorno.

## 7. Acceder desde otra PC de la red

1. `RFQ_WAITRESS_HOST=0.0.0.0` en `.env`.
2. Agrega el nombre/IP de la PC a `DJANGO_ALLOWED_HOSTS`.
3. Permite el puerto en el Firewall de Windows.
4. Desde otra PC: `http://IP-LOCAL:8000/` (ej. `http://192.168.1.50:8000/`).

## 8. Verificaciones

- Chequeo operativo (recomendado antes de usar):

  ```bat
  python manage.py check_operativo
  ```

  Valida DEBUG, SECRET_KEY (sin mostrarla), existencia de `PROYECTO.xlsx` y la
  hoja `"SEGUIMIENTO "`, carpetas, BD, migraciones y permisos. Sale con codigo
  distinto de 0 si hay problemas.

- Pagina de estado (requiere login): `http://.../estado/`.

## 9. Logs

Se escriben en `logs/rfq.log` (o `RFQ_LOGS_DIR`). Incluyen errores de lectura de
RFQ, backup, escritura al Excel, permisos y confirmaciones exitosas.

## 10. Restaurar un backup del Excel

Antes de cada escritura se crea una copia en la carpeta de backups
(`RFQ_CARPETA_BACKUPS` o `backups/`), con nombre `PROYECTO_YYYYMMDD_HHMMSS.xlsx`.
Para restaurar: cierra Excel y copia el backup deseado encima del maestro:

```bat
copy C:\ruta\controlada\backups\PROYECTO_20260707_140420.xlsx C:\ruta\controlada\PROYECTO.xlsx
```

---

## Checklist antes de uso real

- [ ] `.venv` activado y `pip install -r requirements.txt` hecho.
- [ ] `.env` creado (no versionado) con `SECRET_KEY` propia.
- [ ] `DJANGO_DEBUG=0`.
- [ ] `DJANGO_ALLOWED_HOSTS` incluye la PC/IP correcta.
- [ ] `RFQ_ARCHIVO_MAESTRO` apunta al Excel real en ubicacion controlada.
- [ ] `python manage.py migrate` aplicado.
- [ ] Superusuario creado.
- [ ] Grupo `Confirmadores RFQ` creado y usuarios asignados.
- [ ] `python manage.py collectstatic` ejecutado.
- [ ] `python manage.py check_operativo` sin problemas.
- [ ] `PROYECTO.xlsx` cerrado en Excel al escribir (evita bloqueo).
- [ ] Probar el flujo con un `.txt` ficticio antes de usar RFQ reales.
