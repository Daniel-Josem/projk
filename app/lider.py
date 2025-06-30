from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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
        # Asegurar que la carpeta exista antes de guardar
        os.makedirs(os.path.join('static', 'archivos'), exist_ok=True)
        archivo.save(os.path.join('static', ruta_archivo))
    else:
        ruta_archivo = None

    cursor.execute('INSERT INTO tareas (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                   (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo))
    tarea_id = cursor.lastrowid
    # Notificación a trabajador si hay usuario asignado
    id_usuario_asignado = request.form.get('id_usuario_asignado')
    if id_usuario_asignado:
        mensaje = f'Se te ha asignado una nueva tarea: {titulo}'
        cursor.execute('INSERT INTO notificaciones (mensaje, id_usuario) VALUES (?, ?)', (mensaje, id_usuario_asignado))
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
    tareas = conn.execute('SELECT * FROM tareas').fetchall()
    proyectos = conn.execute('SELECT * FROM proyectos').fetchall()
    # Obtener usuarios agrupados por grupo
    usuarios_por_grupo = {}
    usuarios = conn.execute('SELECT nombre_completo, nombre_usuario, correo, grupo FROM Usuario WHERE grupo IS NOT NULL AND grupo != ""').fetchall()
    for usuario in usuarios:
        grupo = usuario['grupo']
        if grupo not in usuarios_por_grupo:
            usuarios_por_grupo[grupo] = []
        usuarios_por_grupo[grupo].append(usuario)
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




