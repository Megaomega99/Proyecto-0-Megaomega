import flet as ft
import requests
from enum import Enum
import base64
from flet import Container, Row, Column, Image, Text

BASE_URL = "http://0.0.0.0:8550"

class CategoriaEnum(str, Enum):
    HOGAR = "Hogar"
    TRABAJO = "Trabajo"
    URGENTE = "Urgente"
    PERSONAL = "Personal"
    OTROS = "Otros"

# Color scheme
COLORS = {
    "primary": "#2196F3",
    "secondary": "#FFC107",
    "background": "#F5F5F5",
    "card": "#FFFFFF",
    "error": "#F44336",
    "success": "#4CAF50",
}

# Category colors
CATEGORY_COLORS = {
    "Hogar": "#4CAF50",
    "Trabajo": "#2196F3",
    "Urgente": "#F44336",
    "Personal": "#9C27B0",
    "Otros": "#FF9800"
}

def main(page: ft.Page):
    page.title = "Gestión de Tareas"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = COLORS["background"]
    page.padding = 0
    
    page.client_storage.set("token", "")
    page.client_storage.set("username", "")

    txt_usuario = ft.TextField(
        label="Usuario",
        width=300,
        border_radius=8,
        prefix_icon=ft.icons.PERSON,
        focused_border_color=COLORS["primary"]
    )
    
    txt_password = ft.TextField(
        label="Contraseña",
        password=True,
        width=300,
        border_radius=8,
        prefix_icon=ft.icons.LOCK,
        focused_border_color=COLORS["primary"]
    )
    
    txt_error = ft.Text(color=COLORS["error"], size=14)
    lista_tareas = ft.Column()
    
    txt_nueva_tarea = ft.TextField(
        label="Nueva tarea",
        multiline=True,
        min_lines=1,
        max_lines=3,
        expand=True,
        border_radius=8,
        focused_border_color=COLORS["primary"]
    )
    
    dd_categoria = ft.Dropdown(
        label="Categoría",
        options=[
            ft.dropdown.Option(key=cat.value, text=cat.value)
            for cat in CategoriaEnum
        ],
        value=CategoriaEnum.OTROS.value,
        width=200,
        border_radius=8
    )

    dd_estado = ft.Dropdown(
        label="Estado",
        options=[
            ft.dropdown.Option("Sin Empezar"),
            ft.dropdown.Option("Empezada"),
            ft.dropdown.Option("Finalizada")
        ],
        value="Sin Empezar",
        width=150,
        border_radius=8
    )

    txt_nuevo_usuario = ft.TextField(
        label="Nuevo Usuario",
        width=300,
        border_radius=8,
        prefix_icon=ft.icons.PERSON_ADD
    )
    
    txt_nueva_password = ft.TextField(
        label="Nueva Contraseña",
        password=True,
        width=300,
        border_radius=8,
        prefix_icon=ft.icons.LOCK
    )
    
    txt_confirmar_password = ft.TextField(
        label="Confirmar Contraseña",
        password=True,
        width=300,
        border_radius=8,
        prefix_icon=ft.icons.LOCK_CLOCK
    )
    
    txt_error_registro = ft.Text(color=COLORS["error"], size=14)
    
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    imagen_perfil = ft.Image(src=r"Tareota/Front/gracioso.png", width=100, height=100, border_radius=50)
    imagen_bytes = None

    def seleccionar_imagen(e):
        file_picker.pick_files("Selecciona una imagen", allowed_extensions=["jpg", "png", "jpeg"])

    def on_file_selected(e):
        nonlocal imagen_bytes
        if e.files:
            imagen_bytes = base64.b64encode(open(e.files[0].path, "rb").read()).decode("utf-8")
            imagen_perfil.src_base64 = imagen_bytes
            page.update()

    file_picker.on_result = on_file_selected

    def login(e):
        try:
            response = requests.post(
                f"{BASE_URL}/token",
                json={
                    "username": txt_usuario.value,
                    "password": txt_password.value
                }
            )
            if response.status_code == 200:
                data = response.json()
                page.client_storage.set("token", data["access_token"])
                page.client_storage.set("username", txt_usuario.value)
                page.go("/tareas")
            else:
                txt_error.value = "Usuario o contraseña incorrectos"
                page.update()
        except requests.RequestException:
            txt_error.value = "Error de conexión con el servidor"
            page.update()

    def registrar_usuario(e):
        if txt_nueva_password.value != txt_confirmar_password.value:
            txt_error_registro.value = "Las contraseñas no coinciden"
            page.update()
            return

        imagen_bytes = None
        if not imagen_bytes:
            with open(r"Tareota/Front/gracioso.png", "rb") as f:
                imagen_bytes = base64.b64encode(f.read()).decode("utf-8")

        try:
            response = requests.post(
                f"{BASE_URL}/usuarios/",
                json={
                    "username": txt_nuevo_usuario.value,
                    "password": txt_nueva_password.value,
                    "imagen_perfil": imagen_bytes
                }
            )
            if response.status_code == 200:
                txt_nuevo_usuario.value = ""
                txt_nueva_password.value = ""
                txt_confirmar_password.value = ""
                txt_error_registro.value = "Usuario registrado exitosamente"
                txt_error_registro.color = COLORS["success"]
                page.go("/")
            else:
                error_detail = response.json().get("detail", "Error al registrar usuario")
                txt_error_registro.value = error_detail
                txt_error_registro.color = COLORS["error"]
            page.update()
        except requests.RequestException:
            txt_error_registro.value = "Error de conexión con el servidor"
            page.update()

    def logout():
        page.client_storage.set("token", "")
        page.client_storage.set("username", "")
        page.go("/")

    def mostrar_tareas(e):
        token = page.client_storage.get("token")
        if not token:
            page.go("/")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/tareas/",
            headers=headers
        )
        
        if response.status_code == 200:
            tareas = response.json()
            if tareas:
                lista_tareas.controls = [
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.CircleAvatar(
                                        content=ft.Text(
                                            tarea.get("propietario", {}).get("username", "")[0].upper() if tarea.get("propietario", {}).get("username") else "",
                                            color=ft.colors.WHITE,
                                            weight=ft.FontWeight.BOLD
                                        ),
                                        bgcolor=COLORS["primary"],
                                        radius=20
                                    ),
                                    ft.Text(
                                        tarea.get("propietario", {}).get("username", ""),
                                        size=16,
                                        weight=ft.FontWeight.W_500
                                    ),
                                ], spacing=10),
                                ft.Divider(height=1, color=ft.colors.BLACK26),
                                ft.Row([
                                    ft.Text(
                                        tarea["texto"],
                                        size=16,
                                        weight=ft.FontWeight.W_500,
                                        expand=True
                                    ),
                                    ft.IconButton(
                                        ft.icons.DELETE_OUTLINE,
                                        icon_color=COLORS["error"],
                                        on_click=lambda _, t=tarea["id"]: eliminar_tarea(t)
                                    )
                                ]),
                                ft.Row([
                                    ft.Container(
                                        content=ft.Text(
                                            tarea["categoria"],
                                            size=12,
                                            color=ft.colors.WHITE,
                                            weight=ft.FontWeight.W_500
                                        ),
                                        bgcolor=CATEGORY_COLORS.get(tarea["categoria"], COLORS["primary"]),
                                        border_radius=15,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            tarea["estado"],
                                            size=12,
                                            color=ft.colors.BLACK,
                                            weight=ft.FontWeight.W_500
                                        ),
                                        bgcolor=ft.colors.BLACK12,
                                        border_radius=15,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    ),
                                    ft.Dropdown(
                                        options=[
                                            ft.dropdown.Option("Sin Empezar"),
                                            ft.dropdown.Option("Empezada"),
                                            ft.dropdown.Option("Finalizada")
                                        ],
                                        value=tarea["estado"],
                                        on_change=lambda e, t=tarea["id"]: actualizar_estado_tarea(t, e.control.value)
                                    )
                                ], spacing=10)
                            ]),
                            padding=15,
                            bgcolor=COLORS["card"],
                        ),
                        elevation=3,
                        surface_tint_color=COLORS["card"]
                    ) for tarea in tareas
                ]
            else:
                lista_tareas.controls = [
                    ft.Container(
                        content=ft.Text(
                            "No hay tareas disponibles",
                            size=16,
                            color=ft.colors.BLACK45
                        ),
                        alignment=ft.alignment.center
                    )
                ]
        else:
            lista_tareas.controls = [
                ft.Container(
                    content=ft.Text(
                        "Error al cargar las tareas",
                        size=16,
                        color=COLORS["error"]
                    ),
                    alignment=ft.alignment.center
                )
            ]
        page.update()

    def crear_tarea(e):
        try:
            token = page.client_storage.get("token")
            if not token:
                page.go("/")
                return

            if not txt_nueva_tarea.value:
                return

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{BASE_URL}/tareas/",
                json={
                    "texto": txt_nueva_tarea.value,
                    "categoria": dd_categoria.value,
                    "estado": dd_estado.value
                },
                headers=headers
            )
            
            if response.status_code == 200:
                txt_nueva_tarea.value = ""
                dd_categoria.value = CategoriaEnum.OTROS.value
                dd_estado.value = "Sin Empezar"
                mostrar_tareas(None)
                page.update()
            else:
                print("Error al crear la tarea:", response.status_code)
        except requests.RequestException as e:
            print("Error de conexión:", e)
            page.update()

    def route_change(route):
        page.views.clear()
        
        if page.route == "/" or page.route == "":
            page.views.append(
                ft.View(
                    "/",
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(ft.icons.TASK_ALT, size=64, color=COLORS["primary"]),
                                    ft.Text("Bienvenido", size=32, weight=ft.FontWeight.BOLD, color=COLORS["primary"]),
                                    txt_usuario,
                                    txt_password,
                                    ft.Container(height=10),
                                    ft.ElevatedButton(
                                        "Iniciar Sesión",
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            bgcolor=COLORS["primary"],
                                            color=ft.colors.WHITE,
                                        ),
                                        width=300,
                                        on_click=login
                                    ),
                                    ft.TextButton(
                                        "¿No tienes cuenta? Regístrate",
                                        on_click=lambda _: page.go("/registro")
                                    ),
                                    txt_error,
                                ],
                                spacing=20,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=40,
                            bgcolor=COLORS["card"],
                            border_radius=10,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                )
            )
        elif page.route == "/registro":
            page.views.append(
                ft.View(
                    "/registro",
                    [
                        ft.AppBar(
                            title=ft.Text("Registro de Usuario", color=ft.colors.WHITE),
                            bgcolor=COLORS["primary"],
                            leading=ft.IconButton(
                                ft.icons.ARROW_BACK,
                                on_click=lambda _: page.go("/"),
                                icon_color=ft.colors.WHITE
                            )
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(ft.icons.PERSON_ADD, size=64, color=COLORS["primary"]),
                                    txt_nuevo_usuario,
                                    txt_nueva_password,
                                    txt_confirmar_password,
                                    ft.ElevatedButton(
                                        "Seleccionar Imagen",
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                        ),
                                        on_click=seleccionar_imagen
                                    ),
                                    imagen_perfil,
                                    ft.ElevatedButton(
                                        "Registrar",
                                        style=ft.ButtonStyle(
                                            shape=ft.RoundedRectangleBorder(radius=8),
                                            bgcolor=COLORS["primary"],
                                            color=ft.colors.WHITE,
                                        ),
                                        width=300,
                                        on_click=registrar_usuario
                                    ),
                                    txt_error_registro,
                                ],
                                spacing=20,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=40,
                            margin=ft.margin.only(top=20),
                            bgcolor=COLORS["card"],
                            border_radius=10,
                        ),
                    ]
                )
            )
        elif page.route == "/tareas":
            page.views.append(
                ft.View(
                    "/tareas",
                    [
                        ft.AppBar(
                            title=ft.Text("Mis Tareas", color=ft.colors.WHITE),
                            bgcolor=COLORS["primary"],
                            actions=[
                                ft.IconButton(
                                    icon=ft.icons.LOGOUT,
                                    icon_color=ft.colors.WHITE,
                                    tooltip="Cerrar sesión",
                                    on_click=lambda _: logout()
                                )
                            ]
                        ),
                        ft.Container(
                            content=ft.Column([
                                # Header con información del usuario
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Row(
                                            [
                                                imagen_perfil,
                                                ft.Text(
                                                    page.client_storage.get("username"),
                                                    size=20,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=COLORS["primary"]
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.START,
                                            spacing=10,
                                        ),
                                        padding=15,
                                    ),
                                    margin=ft.margin.only(bottom=20)
                                ),
                                # Card para crear nueva tarea
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Text(
                                                "Nueva Tarea",
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=COLORS["primary"]
                                            ),
                                            ft.Divider(height=1, color=ft.colors.BLACK12),
                                            txt_nueva_tarea,
                                            ft.Row(
                                                [
                                                    dd_categoria,
                                                    dd_estado,
                                                    ft.IconButton(
                                                        icon=ft.icons.ADD_CIRCLE,
                                                        icon_color=COLORS["primary"],
                                                        icon_size=40,
                                                        tooltip="Agregar tarea",
                                                        on_click=crear_tarea
                                                    ),
                                                ],
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            ),
                                        ], spacing=15),
                                        padding=20,
                                    ),
                                    margin=ft.margin.only(bottom=20),
                                ),
                                # Lista de tareas
                                lista_tareas,
                            ]),
                            padding=20,
                        ),
                    ],
                )
            )
            mostrar_tareas(None)
        
        page.update()

    def eliminar_tarea(tarea_id: int):
        try:
            token = page.client_storage.get("token")
            if not token:
                page.go("/")
                return

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.delete(
                f"{BASE_URL}/tareas/{tarea_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                mostrar_tareas(None)
            else:
                print(f"Error al eliminar tarea: {response.status_code}")
            page.update()
        except requests.RequestException as e:
            print("Error de conexión:", e)
            page.update()

    def actualizar_estado_tarea(tarea_id: int, nuevo_estado: str):
        try:
            token = page.client_storage.get("token")
            if not token:
                page.go("/")
                return

            headers = {"Authorization": f"Bearer {token}"}
            response = requests.put(
                f"{BASE_URL}/tareas/{tarea_id}",
                params={"estado": nuevo_estado},
                headers=headers
            )
            
            if response.status_code == 200:
                mostrar_tareas(None)
            else:
                print(f"Error al actualizar estado: {response.status_code}")
            page.update()
        except requests.RequestException as e:
            print("Error de conexión:", e)
            page.update()

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main,port=8550)