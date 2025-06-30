from flask import Blueprint, jsonify, request,render_template,send_file
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from fpdf import FPDF
from unidecode import unidecode
from datetime import datetime
import sqlite3
import os

api_blueprint = Blueprint('api', __name__)

#Esto permite que SQLite espere unos segundos antes de lanzar el error de "locked":
def get_db_connection():
    conn = sqlite3.connect('gestor_de_tareas.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# --- Crea usuarios de prueba si no existen ---
def crear_usuarios_prueba():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verifica si hay usuarios
    cursor.execute('SELECT COUNT(*) FROM Usuario')
    total = cursor.fetchone()[0]

    if total == 0:
        cursor.execute('''
            INSERT INTO Usuario (nombre_completo, nombre_usuario, documento, correo, contraseña, rol, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("Pedro Lider", "pedro_l", "1111", "pedro@example.com", "1234", "lider", "activo"))

        cursor.execute('''
            INSERT INTO Usuario (nombre_completo, nombre_usuario, documento, correo, contraseña, rol, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("Marta Trabajadora", "marta_t", "2222", "marta@example.com", "1234", "trabajador", "activo"))

        conn.commit()

    conn.close()

# Ejecutar una vez al importar este archivo
crear_usuarios_prueba()

#Contador de lideres activos
@api_blueprint.route('/api/lider/count')
def api_lider_count():
    conn = get_db_connection()
    cnt = conn.execute('SELECT COUNT(*) FROM Usuario WHERE rol="lider" AND estado="activo"').fetchone()[0]
    conn.close()
    return jsonify(count=cnt)

#Contador de trabajadores activos
@api_blueprint.route('/api/trabajadores/count')
def api_trabajadores_count():
    conn = get_db_connection()
    cnt = conn.execute('SELECT COUNT(*) FROM Usuario WHERE estado="activo" AND rol="trabajador"').fetchone()[0]
    conn.close()
    return jsonify(count=cnt)


# 1. Ruta para registrar un lider
@api_blueprint.route('/api/lideres/crear', methods=['POST'])
def registrar_lider():
    data = request.get_json()

    nombre = data.get('nombre')
    apellido = data.get('apellido')
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')
    documento = data.get('documento')
    grupo = data.get('grupo')
    proyecto = data.get('proyecto')
    correo = data.get('correo')
    telefono = data.get('telefono')
    direccion = data.get('direccion')

    nombre_completo = f"{nombre} {apellido}"
    contrasena_hash = generate_password_hash(contrasena)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verificar si el usuario ya existe
            existe = cursor.execute("SELECT id FROM Usuario WHERE nombre_usuario = ?", (usuario,)).fetchone()
            if existe:
                return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

            # Insertar nuevo líder
            cursor.execute('''
                INSERT INTO Usuario (
                    nombre_completo,
                    nombre_usuario,
                    documento,
                    correo,
                    contraseña,
                    rol,
                    estado,
                    grupo,
                    proyecto,
                    telefono,
                    direccion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre_completo,
                usuario,
                documento,
                correo,
                contrasena_hash,
                'lider',
                'activo',
                grupo,
                proyecto,
                telefono,
                direccion
            ))

            conn.commit()

        return jsonify({"message": "Líder registrado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# 2. Ruta para inactivar líder
@api_blueprint.route('/api/lider/inactivar/<int:id>', methods=['POST'])
def inactivar_lider(id):
    with get_db_connection() as conn:
        conn.execute("UPDATE Usuario SET estado = 'inactivo' WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"message": "Líder inactivado"}), 200

# 3. Ruta para obtener los datos de un líder específico (por ID), usada para cargar el formulario de edición
@api_blueprint.route('/api/lider/<int:id>')
def obtener_lider(id):
    with get_db_connection() as conn:
        lider = conn.execute("SELECT * FROM Usuario WHERE id = ? AND rol = 'lider'", (id,)).fetchone()

    if lider:
        return jsonify(dict(lider))
    else:
        return jsonify({"error": "Líder no encontrado"}), 404

# 4. Ruta para actualizar un lider
@api_blueprint.route('/api/lider/actualizar', methods=['POST'])
def actualizar_lider():
    data = request.get_json()
    id = data.get('id')

    campos = ['nombre_completo', 'nombre_usuario', 'documento', 'correo', 'grupo', 'proyecto', 'telefono', 'direccion']
    valores = [data.get(c) for c in campos]

    with get_db_connection() as conn:
        conn.execute(f'''
            UPDATE Usuario SET
                nombre_completo = ?,
                nombre_usuario = ?,
                documento = ?,
                correo = ?,
                grupo = ?,
                proyecto = ?,
                telefono = ?,
                direccion = ?
            WHERE id = ? AND rol = 'lider'
        ''', (*valores, id))
        conn.commit()

    return jsonify({"message": "Líder actualizado correctamente"})

# 5. Ruta para obtener todos los líderes activos
@api_blueprint.route('/api/lideres')
def obtener_lideres():
    with get_db_connection() as conn:
        lideres = conn.execute("SELECT * FROM Usuario WHERE rol = 'lider' AND estado = 'activo'").fetchall()
    return jsonify([dict(l) for l in lideres])

# 6.Ruta para obtener todos los trabajadores activos
@api_blueprint.route('/api/trabajadores')
def obtener_trabajadores():
    with get_db_connection() as conn:
        trabajadores = conn.execute("SELECT * FROM Usuario WHERE rol = 'trabajador' AND estado = 'activo'").fetchall()
    return jsonify([dict(t) for t in trabajadores])


# 7. Ruta para inactivar trabahadores
@api_blueprint.route('/api/trabajador/inactivar/<int:id>', methods=['POST'])
def inactivar_trabajador(id):
    with get_db_connection() as conn:
        conn.execute("UPDATE Usuario SET estado = 'inactivo' WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"message": "Trabajador inactivado"}), 200

# 8. Ruta para obtener los datos de un trabajador específico (por ID), usada para cargar el formulario de edición
@api_blueprint.route('/api/trabajador/<int:id>')
def obtener_trabajador(id):
    with get_db_connection() as conn:
        trabajador = conn.execute("SELECT * FROM Usuario WHERE id = ? AND rol = 'trabajador' AND estado = 'activo'", (id,)).fetchone()

    if trabajador:
        return jsonify(dict(trabajador))
    else:
        return jsonify({"error": "Trabajador no encontrado o inactivo"}), 404


# 9. Ruta para actualizar un trabajador
@api_blueprint.route('/api/trabajador/actualizar', methods=['POST'])
def actualizar_trabajador():
    data = request.get_json()
    id = data.get('id')

    campos = ['nombre_completo', 'nombre_usuario', 'documento', 'correo', 'grupo', 'proyecto', 'telefono', 'direccion']
    valores = [data.get(c) for c in campos]

    with get_db_connection() as conn:
        conn.execute('''
            UPDATE Usuario SET
                nombre_completo = ?,
                nombre_usuario = ?,
                documento = ?,
                correo = ?,
                grupo = ?,
                proyecto = ?,
                telefono = ?,
                direccion = ?
            WHERE id = ? AND rol = 'trabajador'
        ''', (*valores, id))
        conn.commit()

    return jsonify({"message": "Trabajador actualizado correctamente"})

# 10.  Ruta para actualizar el perfil del administrador
@api_blueprint.route('/perfil/actualizar', methods=['POST'])
def actualizar_perfil():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    imagen = request.files.get('imagen')

    ruta_final = None
    if imagen:
        nombre_archivo = secure_filename(imagen.filename)
        ruta = os.path.join('static/avatars', nombre_archivo)
        imagen.save(ruta)
        ruta_final = f'/static/avatars/{nombre_archivo}'

    # Aquí puedes agregar la lógica para actualizar en la base de datos si es necesario

    return jsonify({
        'nombre': nombre,
        'descripcion': descripcion,
        'imagen': ruta_final
    })

@api_blueprint.route('/api/proyecto/<nombre_proyecto>')
def info_proyecto(nombre_proyecto):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Líder asignado al proyecto
    cursor.execute("""
        SELECT nombre_completo FROM Usuario
        WHERE rol = 'lider' AND proyecto = ?
    """, (nombre_proyecto,))
    lider = cursor.fetchone()

    # Total de tareas del proyecto
    cursor.execute("SELECT COUNT(*) FROM tareas WHERE id_proyecto = ?", (nombre_proyecto,))
    total_tareas = cursor.fetchone()[0]

    # Tareas enviadas (completadas)
    cursor.execute("SELECT COUNT(*) FROM tareas WHERE id_proyecto = ? AND estado = 'enviada'", (nombre_proyecto,))
    tareas_completadas = cursor.fetchone()[0]

    # Trabajadores con tareas pendientes
    cursor.execute("""
        SELECT DISTINCT U.nombre_completo
        FROM tareas T
        JOIN Usuario U ON T.id_usuario_asignado = U.id
        WHERE T.id_proyecto = ? AND T.estado = 'pendiente' AND U.rol = 'trabajador'
    """, (nombre_proyecto,))
    trabajadores_pendientes = [fila[0] for fila in cursor.fetchall()]

    conn.close()

    return jsonify({
        'lider': lider['nombre_completo'] if lider else 'No asignado',
        'total': total_tareas,
        'completadas': tareas_completadas,
        'pendientes': total_tareas - tareas_completadas,
        'trabajadores': trabajadores_pendientes
    })

class PDF(FPDF):
    def set_project_name(self, nombre):
        self.project_name = unidecode(nombre)

    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, f"Informe del proyecto: {self.project_name}", 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def title_section(self, lider_nombre, fecha):
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f"Líder del proyecto: {unidecode(lider_nombre)}", 0, 1)
        self.cell(0, 10, f"Fecha de generación: {fecha}", 0, 1)
        self.ln(5)

    def table_section(self, tareas):
        self.set_font('Arial', 'B', 12)
        self.cell(60, 10, 'Tarea', 1)
        self.cell(40, 10, 'Fecha vencimiento', 1)
        self.cell(40, 10, 'Fecha registro', 1)
        self.cell(50, 10, 'Asignado a', 1)
        self.ln()

        self.set_font('Arial', '', 11)
        for tarea in tareas:
            self.cell(60, 10, unidecode(tarea['titulo'].replace("–", "-"))[:30], 1)
            self.cell(40, 10, tarea['fecha_vencimiento'], 1)
            self.cell(40, 10, tarea['fecha_registro'], 1)
            self.cell(50, 10, unidecode(tarea['nombre_completo'].replace("–", "-"))[:30], 1)
            self.ln()

    def no_tasks_message(self):
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, "No hay tareas pendientes en este proyecto.", 0, 1)

@api_blueprint.route('/api/proyecto/<nombre_proyecto>/pdf')
def generar_pdf_proyecto(nombre_proyecto):
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Obtener ID del proyecto desde su nombre
    cursor.execute("SELECT id FROM proyectos WHERE nombre = ?", (nombre_proyecto,))
    proyecto = cursor.fetchone()
    if not proyecto:
        return jsonify({"error": "Proyecto no encontrado"}), 404

    id_proyecto = proyecto['id']

    # Buscar líder del proyecto
    cursor.execute("SELECT nombre_completo FROM Usuario WHERE proyecto = ? AND rol = 'lider'", (nombre_proyecto,))
    lider = cursor.fetchone()
    lider_nombre = lider['nombre_completo'] if lider else 'No asignado'

    # Tareas pendientes del proyecto usando ID
    cursor.execute('''
        SELECT T.titulo, T.fecha_vencimiento, T.fecha_registro, U.nombre_completo
        FROM tareas T
        JOIN Usuario U ON T.id_usuario_asignado = U.id
        WHERE T.id_proyecto = ? AND T.estado = 'pendiente'
    ''', (id_proyecto,))
    tareas_pendientes = cursor.fetchall()
    conn.close()

    # Crear PDF
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.set_project_name(nombre_proyecto)
    pdf.add_page()
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    pdf.title_section(lider_nombre, fecha_actual)

    if tareas_pendientes:
        pdf.table_section(tareas_pendientes)
    else:
        pdf.no_tasks_message()

    # Guardar archivo
    nombre_archivo = f"informe_{nombre_proyecto.replace(' ', '_')}.pdf"
    ruta_pdf = os.path.join('static', nombre_archivo)
    
    try:
        pdf.output(ruta_pdf)
    except UnicodeEncodeError as e:
        print("❌ Error al guardar PDF por caracteres no compatibles:", e)
        return jsonify({"error": "No se pudo generar el PDF por caracteres especiales."}), 500

    return send_file(ruta_pdf, as_attachment=True)

@api_blueprint.route('/api/proyecto/<nombre_proyecto>')
def obtener_avance_proyecto(nombre_proyecto):
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM proyectos WHERE nombre = ?", (nombre_proyecto,))
    proyecto = cursor.fetchone()

    if not proyecto:
        return jsonify({'error': 'Proyecto no encontrado'}), 404

    id_proyecto = proyecto['id']

    cursor.execute("SELECT COUNT(*) FROM tareas WHERE id_proyecto = ?", (id_proyecto,))
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tareas WHERE id_proyecto = ? AND estado = 'completada'", (id_proyecto,))
    completadas = cursor.fetchone()[0]

    # Obtener líder asignado
    cursor.execute("SELECT nombre_completo FROM Usuario WHERE proyecto = ? AND rol = 'lider'", (nombre_proyecto,))
    lider = cursor.fetchone()
    lider_nombre = lider['nombre_completo'] if lider else "No asignado"

    # Obtener trabajadores con tareas pendientes
    cursor.execute('''
        SELECT DISTINCT U.nombre_completo
        FROM tareas T
        JOIN Usuario U ON T.id_usuario_asignado = U.id
        WHERE T.id_proyecto = ? AND T.estado = 'pendiente'
    ''', (id_proyecto,))
    trabajadores = [fila['nombre_completo'] for fila in cursor.fetchall()]

    conn.close()

    avance = round((completadas / total) * 100, 2) if total > 0 else 0

    return jsonify({
        'avance': avance,
        'total': total,
        'completadas': completadas,
        'lider': lider_nombre,
        'trabajadores': trabajadores
    })
