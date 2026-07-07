"""
Vistas del flujo web seguro (Fase 2):

  subir_rfq  -> sube .txt y muestra PREVIEW editable (NO escribe al Excel).
  confirmar  -> tras confirmar, escribe al Excel via el motor y guarda historial.
  historial  -> lista los RFQ procesados.

El modo seguro esta garantizado por el flujo: la escritura solo ocurre en
'confirmar', despues de que el usuario revisa/edita la vista previa.
"""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import SubirRFQForm, VistaPreviaForm
from .models import RFQProcesado
from .services import MotorError, escribir_confirmado, extraer_preview, guardar_subida
from src.modelo import RFQData


@login_required
def subir_rfq(request):
    """Paso 1-3: sube el .txt, extrae datos y muestra la vista previa editable."""
    if request.method == "POST":
        form = SubirRFQForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            ruta = guardar_subida(archivo, settings.MEDIA_ROOT)
            try:
                dato = extraer_preview(ruta)
            except MotorError as e:
                messages.error(request, str(e))
                return render(request, "seguimiento/subir_rfq.html", {"form": form})

            preview = VistaPreviaForm(initial={
                "rfq": dato.rfq,
                "descripcion": dato.descripcion or "",
                "fecha_arranque": dato.fecha_arranque,
                "solicitante": dato.solicitante or "",
                "planta": dato.planta or "",
                "archivo_nombre": archivo.name,
            })
            return render(request, "seguimiento/vista_previa.html", {
                "form": preview,
                "faltantes": dato.faltantes,
                "archivo_nombre": archivo.name,
            })
    else:
        form = SubirRFQForm()
    return render(request, "seguimiento/subir_rfq.html", {"form": form})


@login_required
def confirmar(request):
    """Paso 4-6: escribe al Excel SOLO tras confirmar y registra el historial."""
    if request.method != "POST":
        return redirect("subir_rfq")

    form = VistaPreviaForm(request.POST)
    if not form.is_valid():
        return render(request, "seguimiento/vista_previa.html", {
            "form": form,
            "faltantes": [],
            "archivo_nombre": request.POST.get("archivo_nombre", ""),
        })

    cd = form.cleaned_data
    dato = RFQData(
        rfq=cd["rfq"].strip(),
        descripcion=(cd["descripcion"] or None),
        fecha_arranque=(cd["fecha_arranque"] or None),
        solicitante=(cd["solicitante"] or None),
        planta=(cd["planta"] or None),
        origen_archivo=cd.get("archivo_nombre", ""),
    )
    dato.registrar_faltantes()

    try:
        resumen = escribir_confirmado(dato)
    except MotorError as e:
        RFQProcesado.objects.create(
            rfq=dato.rfq, descripcion=dato.descripcion or "",
            fecha_arranque=dato.fecha_arranque, solicitante=dato.solicitante or "",
            planta=dato.planta or "", archivo_nombre=dato.origen_archivo,
            estado=RFQProcesado.ESTADO_ERROR, accion="",
            campos_faltantes=", ".join(dato.faltantes), mensaje=str(e),
        )
        return render(request, "seguimiento/resultado.html", {
            "ok": False, "mensaje": str(e), "dato": dato,
        })

    RFQProcesado.objects.create(
        rfq=dato.rfq, descripcion=dato.descripcion or "",
        fecha_arranque=dato.fecha_arranque, solicitante=dato.solicitante or "",
        planta=dato.planta or "", archivo_nombre=dato.origen_archivo,
        estado=RFQProcesado.ESTADO_OK, accion=resumen["accion"],
        campos_faltantes=", ".join(resumen["faltantes"]),
        mensaje=f"Backup: {resumen['backup']}",
    )
    return render(request, "seguimiento/resultado.html", {
        "ok": True, "dato": dato, "resumen": resumen,
    })


@login_required
def historial(request):
    """Lista los ultimos RFQ procesados."""
    registros = RFQProcesado.objects.all()[:100]
    return render(request, "seguimiento/historial.html", {"registros": registros})
