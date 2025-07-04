from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash
import sqlite3
import os
from werkzeug.utils import secure_filename

lider = Blueprint('lider', __name__)

# Crear tarea
@lider.route('/crear_tarea', methods=['POST'])
def crear_tarea():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    curso_destino = request.form['curso_destino']
    fecha_vencimiento = request.form['fecha_vencimiento']
    prioridad = request.form['prioridad']
    estado = request.form['estado']

    archivo = request.files['archivo']
    if archivo and archivo.filename != '':
        filename = secure_filename(archivo.filename)
        ruta_archivo = f"archivos/{filename}"
        archivo.save(os.path.join('static', ruta_archivo))
    else:
        ruta_archivo = None

    cursor.execute('INSERT INTO tareas (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                   (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo))

    conn.commit()
    conn.close()

    flash('Tarea creada exitosamente')
    return redirect(url_for('lider.lideres'))

# Mostrar tareas
@lider.route('/lideres')
def lideres():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row

    grupo_lider = session.get('grupo')  # El grupo al que pertenece el líder

    # Tareas solo del grupo del líder
    tareas = conn.execute('SELECT * FROM tareas WHERE curso_destino = ?', (grupo_lider,)).fetchall()

    # Proyectos SIN FILTRO para que sigan apareciendo todos
    proyectos = conn.execute('SELECT * FROM Proyecto').fetchall()
    
    # Solo usuarios del grupo del líder
    usuarios_por_grupo = {grupo_lider: []}
    usuarios = conn.execute('SELECT nombre_completo, nombre_usuario, correo, grupo FROM Usuario WHERE grupo = ?', (grupo_lider,)).fetchall()
    for usuario in usuarios:
        usuarios_por_grupo[grupo_lider].append(usuario)

    conn.close()

    return render_template('lider.html', tareas=tareas, proyectos=proyectos, usuarios_por_grupo=usuarios_por_grupo)


# Editar tarea
@lider.route('/editar_tarea', methods=['POST'])
def editar_tarea():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    id_tarea = request.form['id']
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    curso_destino = request.form['curso_destino']
    fecha_vencimiento = request.form['fecha_vencimiento']
    prioridad = request.form['prioridad']
    estado = request.form['estado']

    archivo = request.files['archivo']
    ruta_archivo = None

    if archivo and archivo.filename != '':
        filename = secure_filename(archivo.filename)
        ruta_archivo = f"archivos/{filename}"
        archivo.save(os.path.join('static', ruta_archivo))

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    if ruta_archivo:
        cursor.execute('''
            UPDATE tareas 
            SET titulo = ?, descripcion = ?, curso_destino = ?, fecha_vencimiento = ?, prioridad = ?, estado = ?, ruta_archivo = ?
            WHERE id = ?
        ''', (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo, id_tarea))
    else:
        cursor.execute('''
            UPDATE tareas 
            SET titulo = ?, descripcion = ?, curso_destino = ?, fecha_vencimiento = ?, prioridad = ?, estado = ?
            WHERE id = ?
        ''', (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, id_tarea))

    conn.commit()
    conn.close()

    flash('Tarea actualizada exitosamente')
    return redirect(url_for('lider.lideres'))

# Eliminar tarea
@lider.route('/eliminar_tarea/<int:id>', methods=['POST'])
def eliminar_tarea(id):
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM tareas WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Tarea eliminada exitosamente')
    return redirect(url_for('lider.lideres'))

@lider.route('/crear_proyecto', methods=['POST'])
def crear_proyecto():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO proyectos (nombre, descripcion, fecha_inicio, fecha_fin) VALUES (?, ?, ?, ?)',
                   (nombre, descripcion, fecha_inicio, fecha_fin))
    conn.commit()
    conn.close()

    flash('Proyecto creado exitosamente', 'success')
    return redirect(url_for('lider.lideres'))  # Esto debe estar así para recargar la vista

@lider.route('/eliminar_proyecto/<int:id>', methods=['POST'])
def eliminar_proyecto(id):
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    # Desvincular las tareas del proyecto eliminado
    cursor.execute('UPDATE tareas SET id_proyecto = NULL WHERE id_proyecto = ?', (id,))

    cursor.execute('DELETE FROM proyectos WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Proyecto eliminado exitosamente', 'success')
    return redirect(url_for('lider.lideres'))

@lider.route('/asignar_tarea_a_proyecto', methods=['POST'])
def asignar_tarea_a_proyecto():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    tarea_id = request.form['tarea_id']
    proyecto_id = request.form['proyecto_id']

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE tareas SET id_proyecto = ? WHERE id = ?', (proyecto_id, tarea_id))
    conn.commit()
    conn.close()

    flash('Tarea asignada exitosamente al proyecto', 'success')
    return redirect(url_for('lider.lideres'))

@lider.route('/notificaciones')
def ver_notificaciones():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))
    usuario = session['usuario']
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # Obtener id del usuario actual (líder)
    cur.execute('SELECT id FROM Usuario WHERE nombre_usuario = ?', (usuario,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return 'Usuario no encontrado', 404
    id_lider = row['id']
    # Obtener notificaciones para el líder
    cur.execute('SELECT * FROM notificaciones WHERE id_usuario = ? ORDER BY id DESC', (id_lider,))
    notificaciones = cur.fetchall()
    conn.close()
    return {'notificaciones': [dict(n) for n in notificaciones]}

@lider.route('/notificaciones/marcar_leida', methods=['POST'])
def marcar_notificacion_leida():
    if 'usuario' not in session:
        return {'success': False, 'error': 'No autenticado'}, 401
    data = request.get_json()
    notificacion_id = data.get('id')
    if not notificacion_id:
        return {'success': False, 'error': 'ID requerido'}, 400
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    cur.execute('UPDATE notificaciones SET leido = 1 WHERE id = ?', (notificacion_id,))
    conn.commit()
    conn.close()
    return {'success': True}

@lider.route('/obtener_perfil')
def obtener_perfil():
    if 'usuario' not in session:
        return jsonify({'error': 'No autenticado'}), 401

    usuario_id = session['usuario']  # Ahora tratamos esto como el ID
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    perfil = conn.execute('SELECT * FROM Usuario WHERE id = ?', (usuario_id,)).fetchone()
    conn.close()

    if perfil:
        return jsonify({
            'id': perfil['id'],
            'nombre': perfil['nombre_completo'],
            'email': perfil['correo']
        })
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404


@lider.route('/actualizar_perfil', methods=['POST'])
def actualizar_perfil():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    id_usuario = request.form['id']
    nombre = request.form['nombre']
    email = request.form['email']
    nueva_contrasena = request.form['nueva_contrasena']
    confirmar_contrasena = request.form['confirmar_contrasena']
    imagen = request.files.get('nueva_imagen')

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    # Actualizar nombre y correo
    cursor.execute('UPDATE Usuario SET nombre_completo = ?, correo = ? WHERE id = ?', (nombre, email, id_usuario))

    # Actualizar contraseña si se desea
    if nueva_contrasena and nueva_contrasena == confirmar_contrasena:
        contraseña_encriptada = generate_password_hash(nueva_contrasena)
        cursor.execute('UPDATE Usuario SET contraseña = ? WHERE id = ?', (contraseña_encriptada, id_usuario))

    # Guardar imagen de perfil si se subió
    if imagen and imagen.filename:
        filename = secure_filename(f"{id_usuario}_{imagen.filename}")
        ruta_imagen = f"avatars/{filename}"
        imagen.save(os.path.join('static', ruta_imagen))
        cursor.execute('UPDATE Usuario SET imagen = ? WHERE id = ?', (ruta_imagen, id_usuario))

    conn.commit()
    conn.close()

    return redirect(url_for('lider.lideres'))
