# Operacion en Windows - Servicio y arranque automatico (Fase 5)

Scripts para operar el sistema RFQ sin abrir la terminal cada vez. Todos los
scripts se ejecutan desde la carpeta `scripts\` y se posicionan solos en la raiz
del proyecto (`cd /d "%~dp0.."`).

> No requieren instalar nada. NSSM es opcional y NO se descarga aqui.
> Las variables de entorno se leen desde `.env` (lo carga `settings.py`).

## Scripts disponibles

| Script | Que hace |
|---|---|
| `iniciar_servidor.bat` | Activa `.venv`, corre `check_operativo --simple` y, si pasa, arranca Waitress |
| `iniciar_servidor.ps1` | Igual que el `.bat`, en PowerShell |
| `check_operativo.bat` | Chequeo operativo (acepta `--simple`) |
| `migrar_y_collectstatic.bat` | Aplica `migrate` y `collectstatic` |

Uso manual:

```bat
scripts\iniciar_servidor.bat
scripts\check_operativo.bat --simple
scripts\migrar_y_collectstatic.bat
```

PowerShell (si la politica bloquea el `.ps1`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\iniciar_servidor.ps1
```

---

## Opcion A: Task Scheduler (recomendada, sin instalar nada)

Arranca el servidor automaticamente al iniciar sesion o Windows.

1. Abre **Programador de tareas** (Task Scheduler) -> **Crear tarea** (no la basica).
2. **General:**
   - Nombre: `RFQ Servidor`.
   - Usuario: la cuenta que tiene acceso a `PROYECTO.xlsx` y al proyecto.
   - Marca **"Ejecutar tanto si el usuario inicio sesion como si no"** solo si el
     usuario tiene permiso; para empezar, "Ejecutar solo cuando el usuario haya
     iniciado sesion" es mas simple.
   - Marca **"Ejecutar con los privilegios mas altos"** si hace falta.
3. **Desencadenadores (Triggers):** nuevo -> "Al iniciar sesion" (o "Al iniciar
   el equipo").
4. **Acciones (Actions):** nueva -> "Iniciar un programa":
   - Programa o script: `C:\x\proyectos\RFQ\scripts\iniciar_servidor.bat`
   - **Iniciar en (Start in):** `C:\x\proyectos\RFQ`  <-- IMPORTANTE (carpeta de inicio).
5. **Condiciones/Configuracion:** desmarca "Detener si pasa a bateria" si es un
   equipo fijo; marca "Reiniciar si la tarea falla" (cada 1 min, 3 intentos).
6. Guarda (pedira la contrasena del usuario).

**Si no inicia, revisa:**
- El campo **"Iniciar en"** apunta a la raiz del proyecto.
- El usuario de la tarea puede leer/escribir `PROYECTO.xlsx` y las carpetas
  `media/ backups/ reportes/ logs/`.
- Existe `.venv` o el Python del sistema esta en el PATH del usuario.
- Ejecuta el `.bat` a mano una vez para ver el mensaje de error.
- Revisa `logs\rfq.log`.

---

## Opcion B: NSSM (servicio de Windows) - alternativa, NO se instala aqui

NSSM permite correr Waitress como servicio real (arranca sin sesion iniciada).
Descarga NSSM manualmente desde su sitio oficial y colocalo, por ejemplo, en
`C:\nssm\nssm.exe`. Luego (ejemplos; ajusta rutas):

```bat
:: Crear el servicio (una sola vez)
C:\nssm\nssm.exe install RFQServidor "C:\x\proyectos\RFQ\.venv\Scripts\python.exe" "C:\x\proyectos\RFQ\run_waitress.py"

:: Carpeta de trabajo (equivale a "Iniciar en")
C:\nssm\nssm.exe set RFQServidor AppDirectory "C:\x\proyectos\RFQ"

:: Redirigir salida a logs (opcional)
C:\nssm\nssm.exe set RFQServidor AppStdout "C:\x\proyectos\RFQ\logs\servicio_out.log"
C:\nssm\nssm.exe set RFQServidor AppStderr "C:\x\proyectos\RFQ\logs\servicio_err.log"

:: Arranque automatico
C:\nssm\nssm.exe set RFQServidor Start SERVICE_AUTO_START
```

Operar el servicio:

```bat
C:\nssm\nssm.exe start RFQServidor
C:\nssm\nssm.exe stop RFQServidor
C:\nssm\nssm.exe restart RFQServidor
C:\nssm\nssm.exe status RFQServidor
```

- **Ruta a Python:** usa el del `.venv` (`.venv\Scripts\python.exe`) para tener
  las dependencias correctas.
- **Argumentos:** `run_waitress.py` (host/puerto salen de `.env`).
- **Logs:** los de la app en `logs\rfq.log`; los del proceso en los `AppStdout/AppStderr`.
- Antes de crear el servicio, corre `scripts\migrar_y_collectstatic.bat` y
  `scripts\check_operativo.bat`.

Para uso diario (iniciar/detener/reiniciar, revisar estado, backups, fallos) ver
[../docs/OPERACION_DIARIA.md](../docs/OPERACION_DIARIA.md).
