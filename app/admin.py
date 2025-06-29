from flask import Blueprint, jsonify, request,render_template
from werkzeug.security import generate_password_hash
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
                proyecto = ?
            WHERE id = ? AND rol = 'trabajador'
        ''', (*valores, id))
        conn.commit()

    return jsonify({"message": "Trabajador actualizado correctamente"})
