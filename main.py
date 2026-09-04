import flet as ft
import asyncio

async def main(page: ft.Page):
    # ==========================================
    # --- CONFIGURACIÓN PARA MÓVIL (ANDROID) ---
    # ==========================================
    page.title = "DocenteSmart"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F7F5EE"  # Beige claro institucional

    # Variables de estado global
    lista_cursos = []
    curso_seleccionado = None
    alumnos_temporal_ocr = []

    # ==========================================
    # --- 1. PANTALLA DE CARGA (SPLASH) --------
    # ==========================================
    splash_view = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.SCHOOL, size=80, color="#5C3A21"),
                ft.Text("DocenteSmart", size=28, weight=ft.FontWeight.BOLD, color="#5C3A21"),
                ft.Text(
                    "U.E. 17 de Septiembre De San Francisco de Milagro",
                    size=14,
                    color="#8C5A32",
                    text_align=ft.TextAlign.CENTER
                ),
                ft.ProgressRing(color="#8C5A32", stroke_width=3)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        alignment=ft.Alignment(0, 0),  # Corregido para compatibilidad total en Android
        expand=True,
    )

    # ==========================================
    # --- 2. VISTAS DE ASISTENCIA Y NOTAS ------
    # ==========================================
    columna_asistencia = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    columna_notas = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)

    lbl_curso_titulo_asistencia = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color="#5C3A21")
    lbl_curso_titulo_notas = ft.Text("", size=15, weight=ft.FontWeight.BOLD, color="#5C3A21")

    def cargar_tabla_asistencia():
        columna_asistencia.controls.clear()
        if not curso_seleccionado:
            return

        lbl_curso_titulo_asistencia.value = f"Curso: {curso_seleccionado['curso']} - {curso_seleccionado['asignatura']}"

        for al in curso_seleccionado.get("alumnos", []):
            def actualizar_estado(e, estudiante=al):
                estudiante["asistencia"] = e.control.value
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"Asistencia: {estudiante['nombre']} -> {e.control.value}"),
                    bgcolor="#5C3A21"
                )
                page.snack_bar.open = True
                page.update()

            radio_asistencia = ft.RadioGroup(
                content=ft.Row([
                    ft.Radio(value="Presente", label="P"),
                    ft.Radio(value="Atraso", label="A"),
                    ft.Radio(value="Falta", label="F"),
                ], spacing=2),
                value=al.get("asistencia", "Presente"),
                on_change=actualizar_estado
            )

            fila = ft.Container(
                padding=8,
                bgcolor="white",
                border_radius=8,
                border=ft.Border.all(1, "#E8DFD8"),
                content=ft.Row(
                    [
                        ft.Text(
                            f"{al['id']}. {al['nombre']}",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                            color="#5C3A21",
                            expand=True
                        ),
                        radio_asistencia
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            )
            columna_asistencia.controls.append(fila)
        page.update()

    def cargar_tabla_notas():
        columna_notas.controls.clear()
        if not curso_seleccionado:
            return

        lbl_curso_titulo_notas.value = f"Notas: {curso_seleccionado['curso']} - {curso_seleccionado['asignatura']}"

        for al in curso_seleccionado.get("alumnos", []):
            tf_n1 = ft.TextField(value=str(al.get("n1", "0.00")), width=50, text_size=11, height=35, border_radius=6)
            tf_n2 = ft.TextField(value=str(al.get("n2", "0.00")), width=50, text_size=11, height=35, border_radius=6)
            tf_n3 = ft.TextField(value=str(al.get("n3", "0.00")), width=50, text_size=11, height=35, border_radius=6)

            def guardar_notas_alumno(e, estudiante=al, t1=tf_n1, t2=tf_n2, t3=tf_n3):
                estudiante["n1"] = t1.value
                estudiante["n2"] = t2.value
                estudiante["n3"] = t3.value

            tf_n1.on_change = guardar_notas_alumno
            tf_n2.on_change = guardar_notas_alumno
            tf_n3.on_change = guardar_notas_alumno

            fila = ft.Container(
                padding=8,
                bgcolor="white",
                border_radius=8,
                border=ft.Border.all(1, "#E8DFD8"),
                content=ft.Row(
                    [
                        ft.Text(
                            f"{al['id']}. {al['nombre']}",
                            weight=ft.FontWeight.BOLD,
                            size=11,
                            color="#5C3A21",
                            expand=True
                        ),
                        ft.Row([tf_n1, tf_n2, tf_n3], spacing=4)
                    ]
                )
            )
            columna_notas.controls.append(fila)
        page.update()

    vista_tabla_asistencia = ft.Container(
        padding=12,
        content=ft.Column([
            lbl_curso_titulo_asistencia,
            ft.Text("P = Presente | A = Atraso | F = Falta", size=11, color="#8C5A32"),
            ft.Divider(color="#8C5A32", height=10),
            ft.Container(content=columna_asistencia, expand=True)
        ]),
        expand=True
    )

    vista_tabla_notas = ft.Container(
        padding=12,
        content=ft.Column([
            lbl_curso_titulo_notas,
            ft.Text("Aporte 1 | Aporte 2 | Aporte 3", size=11, color="#8C5A32"),
            ft.Divider(color="#8C5A32", height=10),
            ft.Container(content=columna_notas, expand=True)
        ]),
        expand=True
    )

    # ==========================================
    # --- 3. PANTALLA PRINCIPAL (CURSOS) -------
    # ==========================================
    columna_cursos = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def abrir_detalle_curso(curso):
        nonlocal curso_seleccionado
        curso_seleccionado = curso
        cargar_tabla_asistencia()
        vista_principal.content = vista_tabla_asistencia
        barra_navegacion.selected_index = 1
        page.update()

    def refrescar_lista_cursos():
        columna_cursos.controls.clear()
        if not lista_cursos:
            columna_cursos.controls.append(
                ft.Container(
                    padding=20,
                    content=ft.Text(
                        "Aún no tienes cursos registrados.\nPresiona 'AÑADIR NUEVO CURSO' para escanear la primera lista.",
                        text_align=ft.TextAlign.CENTER,
                        color="#8C5A32",
                        size=13
                    )
                )
            )
        else:
            for c in lista_cursos:
                tarjeta = ft.Container(
                    padding=15,
                    bgcolor="white",
                    border_radius=12,
                    border=ft.Border.all(1, "#D4C5B9"),
                    shadow=ft.BoxShadow(blur_radius=4, color="#00000010"),
                    on_click=lambda e, curso=c: abrir_detalle_curso(curso),
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Row([
                                        ft.Icon(ft.Icons.BOOKMARK, color="#5C3A21", size=18),
                                        ft.Text(c['curso'], weight=ft.FontWeight.BOLD, size=15, color="#8C5A32"),
                                    ]),
                                    ft.Text(f"Asignatura: {c['asignatura']}", size=12, color="#8C5A32"),
                                    ft.Row([
                                        ft.Icon(ft.Icons.PEOPLE_ALT, size=14, color="#8C5A32"),
                                        ft.Text(
                                            f"{len(c.get('alumnos', []))} alumnos digitalizados",
                                            size=11,
                                            color="#8C5A32"
                                        ),
                                        ft.Text(
                                            " • [TUTOR]" if c.get('es_tutor') else "",
                                            size=11,
                                            color="green",
                                            weight=ft.FontWeight.BOLD
                                        ),
                                    ])
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#5C3A21")
                        ]
                    )
                )
                columna_cursos.controls.append(tarjeta)
        page.update()

    def procesar_imagen_ocr():
        estudiantes_detectados = []
        for i in range(1, 6):
            estudiantes_detectados.append({
                "id": i,
                "nombre": f"Estudiante {i}",
                "asistencia": "Presente",
                "n1": "0.00",
                "n2": "0.00",
                "n3": "0.00"
            })
        return estudiantes_detectados

    visor_camara = ft.Container(
        width=280,
        height=120,
        bgcolor="#2C3E50",
        border_radius=10,
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            [
                ft.Icon(ft.Icons.CAMERA_ALT, color="white", size=28),
                ft.Text("VISTA DE CÁMARA EN VIVO", color="white", size=10, weight=ft.FontWeight.BOLD),
                ft.Text("Enfoque la lista impresa para escanear", color="#BDC3C7", size=9)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    lbl_estado_escaneo = ft.Text(
        "📷 Presione para capturar la lista",
        size=11,
        color="#8C5A32",
        weight=ft.FontWeight.BOLD
    )

    def tomar_foto_camara(e):
        nonlocal alumnos_temporal_ocr
        lbl_estado_escaneo.value = "⏳ Procesando captura de lista..."
        page.update()

        alumnos_temporal_ocr = procesar_imagen_ocr()

        visor_camara.bgcolor = "#27AE60"
        visor_camara.content = ft.Column(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, color="white", size=28),
                ft.Text("¡ESCANEO COMPLETADO!", color="white", size=11, weight=ft.FontWeight.BOLD),
                ft.Text(f"{len(alumnos_temporal_ocr)} Filas detectadas para registro", color="white", size=9)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        lbl_estado_escaneo.value = "✅ Lista detectada. Complete los datos del curso."
        page.update()

    btn_capturar_lista = ft.ElevatedButton(
        "📸 TOMAR FOTO AHORA",
        style=ft.ButtonStyle(color="white", bgcolor="#8C5A32", shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=tomar_foto_camara
    )

    txt_curso = ft.TextField(label="Curso y Especialidad", hint_text="Ej: Tercero F Informática", border_radius=8)
    txt_asignatura = ft.TextField(label="Asignatura principal", hint_text="Ej: Soporte Técnico", border_radius=8)
    txt_asig_tutor = ft.TextField(
        label="Asignatura(s) adicional(es)",
        hint_text="Ej: Historia",
        border_radius=8,
        visible=False
    )

    def cambio_tutor(e):
        txt_asig_tutor.visible = (radio_tutor.value == "SI")
        modal_crear_curso.update()

    radio_tutor = ft.RadioGroup(
        content=ft.Row([
            ft.Text("¿Es Tutor/a?", size=12, weight=ft.FontWeight.BOLD, color="#5C3A21"),
            ft.Radio(value="NO", label="NO"),
            ft.Radio(value="SI", label="SI"),
        ]),
        value="NO",
        on_change=cambio_tutor
    )

    def guardar_curso_accion(e):
        if not txt_curso.value.strip() or not txt_asignatura.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Ingrese el curso y la asignatura"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return

        es_tut = (radio_tutor.value == "SI")
        asig_final = txt_asignatura.value.strip()
        if es_tut and txt_asig_tutor.value.strip():
            asig_final += f" / {txt_asig_tutor.value.strip()}"

        alumnos_a_guardar = alumnos_temporal_ocr if alumnos_temporal_ocr else [
            {"id": i, "nombre": f"Estudiante {i}", "asistencia": "Presente", "n1": "0.00", "n2": "0.00", "n3": "0.00"}
            for i in range(1, 21)
        ]

        nuevo_curso = {
            "curso": txt_curso.value.strip(),
            "asignatura": asig_final,
            "alumnos": alumnos_a_guardar,
            "es_tutor": es_tut
        }
        lista_cursos.append(nuevo_curso)

        txt_curso.value = ""
        txt_asignatura.value = ""
        txt_asig_tutor.value = ""
        radio_tutor.value = "NO"
        txt_asig_tutor.visible = False

        modal_crear_curso.open = False
        refrescar_lista_cursos()
        page.snack_bar = ft.SnackBar(ft.Text("✅ ¡Curso guardado exitosamente!"), bgcolor="#5C3A21")
        page.snack_bar.open = True
        page.update()

    modal_crear_curso = ft.AlertDialog(
        title=ft.Text("📷 Digitalización de Lista", size=16, weight=ft.FontWeight.BOLD, color="#5C3A21"),
        content=ft.Column(
            [
                visor_camara,
                btn_capturar_lista,
                lbl_estado_escaneo,
                txt_curso,
                txt_asignatura,
                radio_tutor,
                txt_asig_tutor
            ],
            spacing=8,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(modal_crear_curso, "open", False) or page.update()),
            ft.ElevatedButton(
                "💾 GUARDAR CURSO",
                style=ft.ButtonStyle(color="white", bgcolor="#5C3A21", shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=guardar_curso_accion
            )
        ]
    )

    def abrir_escaneo(e):
        page.dialog = modal_crear_curso
        modal_crear_curso.open = True
        page.update()

    def cerrar_sesion(e):
        page.appbar.visible = False
        page.navigation_bar.visible = False
        page.controls.clear()
        page.add(login_view)
        page.update()

    pantalla_principal_view = ft.Container(
        padding=15,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("DocenteSmart", size=20, weight=ft.FontWeight.BOLD, color="#5C3A21"),
                            ft.Text("Panel del Docente", size=12, color="#8C5A32")
                        ]),
                        ft.ElevatedButton(
                            "Salir",
                            style=ft.ButtonStyle(
                                color="white",
                                bgcolor="#A93226",
                                shape=ft.RoundedRectangleBorder(radius=8)
                            ),
                            on_click=cerrar_sesion
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color="#8C5A32", height=10),
                ft.ElevatedButton(
                    text="📷 AÑADIR NUEVO CURSO",
                    width=340,
                    height=45,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#5C3A21",
                        shape=ft.RoundedRectangleBorder(radius=10),
                        elevation=3
                    ),
                    on_click=abrir_escaneo
                ),
                ft.Container(height=5),
                ft.Text("Cursos Registrados:", size=13, weight=ft.FontWeight.BOLD, color="#5C3A21"),
                ft.Container(content=columna_cursos, expand=True)
            ]
        ),
        expand=True
    )

    # ==========================================
    # --- 4. PANTALLA DE LOGIN -----------------
    # ==========================================
    msg_error = ft.Text("", color="red", size=12, weight=ft.FontWeight.BOLD, visible=False)

    txt_correo = ft.TextField(
        label="Correo Institucional / Usuario",
        border_color="#8C5A32",
        focused_border_color="#5C3A21",
        text_size=13,
        border_radius=10,
        bgcolor="white"
    )

    txt_password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        border_color="#8C5A32",
        focused_border_color="#5C3A21",
        text_size=13,
        border_radius=10,
        bgcolor="white"
    )

    def validar_login(e):
        correo = txt_correo.value.strip()
        clave = txt_password.value.strip()

        if not correo or not clave:
            msg_error.value = "⚠️ Por favor, ingrese su correo y contraseña."
            msg_error.visible = True
            page.update()
        elif "@" in correo and len(clave) >= 4:
            msg_error.visible = False
            refrescar_lista_cursos()
            page.appbar.visible = True
            page.navigation_bar.visible = True
            vista_principal.content = pantalla_principal_view
            page.controls.clear()
            page.add(vista_principal)
            page.update()
        else:
            msg_error.value = "❌ El correo o la contraseña son incorrectos."
            msg_error.visible = True
            page.update()

    login_view = ft.Container(
        padding=25,
        content=ft.Column(
            [
                ft.Icon(ft.Icons.SCHOOL, size=70, color="#5C3A21"),
                ft.Text("DocenteSmart", size=24, weight=ft.FontWeight.BOLD, color="#5C3A21"),
                ft.Text(
                    "U.E. 17 de Septiembre De San Francisco de Milagro",
                    size=12,
                    color="#8C5A32",
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Divider(color="#8C5A32", height=20, thickness=1),
                msg_error,
                txt_correo,
                txt_password,
                ft.Container(height=10),
                ft.ElevatedButton(
                    text="INICIAR SESIÓN",
                    width=300,
                    height=45,
                    style=ft.ButtonStyle(
                        color="white",
                        bgcolor="#5C3A21",
                        shape=ft.RoundedRectangleBorder(radius=10),
                        elevation=4
                    ),
                    on_click=validar_login
                ),
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCK, size=14, color="#8C5A32"),
                        ft.Text("Modo Fuera de Línea (Offline) Activo", size=11, color="#8C5A32")
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        alignment=ft.Alignment(0, 0),
        expand=True
    )

    # ==========================================
    # --- 5. NAVEGACIÓN Y MONTAJE PRINCIPAL ----
    # ==========================================
    vista_principal = ft.Container(
        content=pantalla_principal_view,
        expand=True,
        padding=5
    )

    def cambiar_pestana(e):
        index = e.control.selected_index

        if index == 0:
            refrescar_lista_cursos()
            vista_principal.content = pantalla_principal_view
        elif index == 1:
            if curso_seleccionado:
                cargar_tabla_asistencia()
                vista_principal.content = vista_tabla_asistencia
            else:
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ Primero seleccione un curso de la lista"), bgcolor="orange")
                page.snack_bar.open = True
        elif index == 2:
            if curso_seleccionado:
                cargar_tabla_notas()
                vista_principal.content = vista_tabla_notas
            else:
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ Primero seleccione un curso de la lista"), bgcolor="orange")
                page.snack_bar.open = True

        page.update()

    barra_navegacion = ft.NavigationBar(
        selected_index=0,
        bgcolor="#FDFBF7",
        active_color="#5C3A21",
        indicator_color="#E8DFD8",
        on_change=cambiar_pestana,
        visible=False,
        destinations=[
            ft.NavigationDestination(
                icon=ft.Icons.CLASS_OUTLINED,
                selected_icon=ft.Icons.CLASS,
                label="Cursos"
            ),
            ft.NavigationDestination(
                icon=ft.Icons.HOW_TO_REG_OUTLINED,
                selected_icon=ft.Icons.HOW_TO_REG,
                label="Asistencia"
            ),
            ft.NavigationDestination(
                icon=ft.Icons.GRADE_OUTLINED,
                selected_icon=ft.Icons.GRADE,
                label="Notas"
            )
        ]
    )

    app_bar = ft.AppBar(
        title=ft.Row(
            [
                ft.Icon(ft.Icons.SCHOOL, color="white"),
                ft.Text("DocenteSmart", weight=ft.FontWeight.BOLD, color="white", size=18)
            ],
            spacing=10
        ),
        bgcolor="#5C3A21",
        center_title=False,
        visible=False,
        actions=[
            ft.IconButton(
                icon=ft.Icons.ADD_A_PHOTO,
                icon_color="white",
                tooltip="Nuevo Curso con OCR",
                on_click=abrir_escaneo
            )
        ]
    )

    # Montaje e inicio de la app
    page.appbar = app_bar
    page.navigation_bar = barra_navegacion
    page.add(splash_view)
    page.update()

    # Transición asíncrona Splash -> Login (1.5 segundos)
    await asyncio.sleep(1.5)
    page.controls.clear()
    page.add(login_view)
    page.update()

# ==========================================
# --- PUNTO DE ENTRADA ÚNICO DE LA APP -----
# ==========================================
ft.app(target=main)
