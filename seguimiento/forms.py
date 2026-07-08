from django import forms

MAX_BYTES = 2 * 1024 * 1024  # 2 MB
MAX_DESCRIPCION = 2000       # limite defensivo para descripcion
# Formatos aceptados HOY en la web. .msg/.pdf/.docx siguen siendo placeholders.
EXTENSIONES_PERMITIDAS = (".txt", ".eml")


class SubirRFQForm(forms.Form):
    """Paso 1: subir el archivo RFQ/correo (.txt o .eml)."""
    archivo = forms.FileField(
        label="Archivo RFQ / correo (.txt o .eml)",
        help_text="Correo Form Approvals como .txt o .eml. Max 2 MB. "
                  ".msg/.pdf/.docx aun no soportados.",
    )

    def clean_archivo(self):
        f = self.cleaned_data["archivo"]
        if not f.name.lower().endswith(EXTENSIONES_PERMITIDAS):
            raise forms.ValidationError(
                "Solo se aceptan archivos .txt o .eml por ahora."
            )
        if f.size == 0:
            raise forms.ValidationError("El archivo esta vacio.")
        if f.size > MAX_BYTES:
            raise forms.ValidationError("El archivo excede el limite de 2 MB.")
        return f


class VistaPreviaForm(forms.Form):
    """Paso 3: preview EDITABLE antes de escribir al Excel.

    Todos los campos salvo RFQ son opcionales; lo que quede vacio se registrara
    como faltante. Los campos 'orig_*' (ocultos) guardan lo que el motor extrajo,
    para detectar que edito el usuario a mano (auditoria).
    """
    rfq = forms.CharField(label="RFQ (numero de pedido)", max_length=50)
    descripcion = forms.CharField(
        label="Descripcion", required=False, max_length=MAX_DESCRIPCION,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    fecha_arranque = forms.DateField(
        label="Fecha de arranque", required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        input_formats=["%Y-%m-%d", "%d/%m/%Y"],
    )
    solicitante = forms.CharField(label="Solicitante", required=False, max_length=200)
    planta = forms.CharField(label="Planta", required=False, max_length=200)
    archivo_nombre = forms.CharField(required=False, widget=forms.HiddenInput)

    # Valores originales extraidos por el motor (para auditar ediciones).
    orig_rfq = forms.CharField(required=False, widget=forms.HiddenInput)
    orig_descripcion = forms.CharField(required=False, widget=forms.HiddenInput)
    orig_fecha_arranque = forms.CharField(required=False, widget=forms.HiddenInput)
    orig_solicitante = forms.CharField(required=False, widget=forms.HiddenInput)
    orig_planta = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_rfq(self):
        rfq = (self.cleaned_data.get("rfq") or "").strip()
        if not rfq:
            raise forms.ValidationError("El RFQ es obligatorio y no puede estar vacio.")
        return rfq

    def campos_editados(self) -> list[str]:
        """Compara los valores enviados con los originales extraidos."""
        cd = self.cleaned_data
        editados = []
        pares = {
            "rfq": cd.get("orig_rfq", ""),
            "descripcion": cd.get("orig_descripcion", ""),
            "solicitante": cd.get("orig_solicitante", ""),
            "planta": cd.get("orig_planta", ""),
            "fecha_arranque": cd.get("orig_fecha_arranque", ""),
        }
        for campo, original in pares.items():
            actual = cd.get(campo)
            actual = "" if actual in (None, "") else str(actual)
            if actual != (original or ""):
                editados.append(campo)
        return editados
