from django.contrib import admin

from .models import RFQProcesado


@admin.register(RFQProcesado)
class RFQProcesadoAdmin(admin.ModelAdmin):
    list_display = ("rfq", "accion", "estado", "usuario", "solicitante", "planta",
                    "campos_faltantes", "campos_editados", "creado_en")
    list_filter = ("estado", "accion", "creado_en", "usuario")
    search_fields = ("rfq", "solicitante", "planta", "descripcion")
    readonly_fields = ("creado_en",)
