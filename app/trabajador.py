from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import sqlite3
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

trabajador_blueprint = Blueprint('trabajador', __name__)

@trabajador_blueprint.route('/trabajador')
def trabajador():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    usuario_id = session.get('usuario')  # id del usuario autenticado
    grupo_usuario = session.get('grupo')
    print(f"ID usuario logueado: {usuario_id}, Grupo: '{grupo_usuario}'")

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    # Mostrar tareas asignadas por usuario o por grupo
    cursos = conn.execute('SELECT DISTINCT curso_destino FROM tareas').fetchall()
    print('Valores curso_destino en tareas:')
    for c in cursos:
        print(f"'{c['curso_destino']}'")
    tareas = conn.execute('''
        SELECT * FROM tareas
        WHERE id_usuario_asignado = ? OR TRIM(LOWER(curso_destino)) = TRIM(LOWER(?))
    ''', (usuario_id, grupo_usuario)).fetchall()
    # Obtener proyectos
    proyectos = conn.execute('SELECT * FROM proyectos').fetchall()
    conn.close()

    print(f"Tareas encontradas: {tareas}")

    # Formatear fecha_vencimiento a YYYY-MM-DD para el calendario
    tareas_list = []
    for t in tareas:
        tarea_dict = dict(t)
        fecha = tarea_dict.get('fecha_vencimiento')
        if fecha:
            try:
                dt = datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                try:
                    dt = datetime.strptime(fecha, '%d/%m/%Y')
                except ValueError:
                    try:
                        dt = datetime.strptime(fecha, '%d-%m-%Y')
                    except ValueError:
                        dt = None
            if dt:
                tarea_dict['fecha_vencimiento'] = dt.strftime('%Y-%m-%d')
        tareas_list.append(tarea_dict)

    return render_template('trabajador.html', tareas=tareas_list, proyectos=proyectos)

def notificar_lider_tarea_completada(tarea_id):
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    # Obtener info de la tarea y el usuario asignado
    cur.execute('SELECT titulo, id_usuario_asignado, curso_destino FROM tareas WHERE id = ?', (tarea_id,))
    tarea = cur.fetchone()
    if not tarea:
        conn.close()
        return
    titulo, id_usuario_asignado, curso_destino = tarea
    # Buscar líder por grupo (curso_destino) o por proyecto si lo tienes
    cur.execute('''
        SELECT id, correo FROM Usuario
        WHERE rol = 'lider' AND TRIM(LOWER(grupo)) = TRIM(LOWER(?))
    ''', (curso_destino,))
    lider = cur.fetchone()
    if not lider:
        conn.close()
        return
    id_lider, correo_lider = lider
    # Insertar notificación en la base de datos
    mensaje = f'La tarea "{titulo}" ha sido completada por el trabajador.'
    cur.execute('INSERT INTO notificaciones (mensaje, id_usuario) VALUES (?, ?)', (mensaje, id_lider))
    conn.commit()
    conn.close()
    # Enviar correo
    try:
        from app.email_service import enviar_notificacion_lider
        enviar_notificacion_lider(correo_lider, 'Tarea completada', mensaje)
    except Exception as e:
        print('Error enviando email al líder:', e)

# --- API para marcar tarea como completada ---
@trabajador_blueprint.route('/api/tarea/completar/<int:tarea_id>', methods=['POST'])
def completar_tarea(tarea_id):
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    try:
        conn = sqlite3.connect('gestor_de_tareas.db')
        cur = conn.cursor()
        cur.execute('UPDATE tareas SET estado = ? WHERE id = ?', ('completado', tarea_id))
        conn.commit()
        conn.close()
        notificar_lider_tarea_completada(tarea_id)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 500

# --- API para subir archivo a tarea ---
@trabajador_blueprint.route('/api/tarea/subir-archivo/<int:tarea_id>', methods=['POST'])
def subir_archivo_tarea(tarea_id):
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    if 'archivo' not in request.files:
        return jsonify({'ok': False, 'msg': 'No se envió archivo'}), 400
    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({'ok': False, 'msg': 'Nombre de archivo vacío'}), 400
    carpeta_destino = os.path.join('static', 'archivos_tareas')
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
    nombre_archivo = f"{tarea_id}_{archivo.filename}"
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
    archivo.save(ruta_destino)
    try:
        conn = sqlite3.connect('gestor_de_tareas.db')
        cur = conn.cursor()
        cur.execute('UPDATE tareas SET estado = ? WHERE id = ?', ('completado', tarea_id))
        conn.commit()
        conn.close()
        notificar_lider_tarea_completada(tarea_id)
    except Exception as e:
        return jsonify({'ok': False, 'msg': f'Archivo subido pero error al marcar completada: {str(e)}'}), 500
    return jsonify({'ok': True, 'nombre': nombre_archivo, 'url': '/' + ruta_destino.replace('\\', '/')})

# --- API para obtener detalles de tarea ---
@trabajador_blueprint.route('/api/tarea/<int:tarea_id>')
def api_tarea_detalle(tarea_id):
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    tarea = conn.execute('SELECT * FROM tareas WHERE id = ?', (tarea_id,)).fetchone()
    archivos = []
    # Si tienes una tabla de archivos, aquí deberías consultarla. Si no, deja vacío o busca en carpeta.
    # Ejemplo: buscar archivos en static/archivos_tareas/ que empiecen con el id de la tarea
    carpeta = os.path.join('static', 'archivos_tareas')
    if os.path.exists(carpeta):
        for nombre in os.listdir(carpeta):
            if nombre.startswith(f'{tarea_id}_') or nombre.startswith(f'{tarea_id}-') or nombre.startswith(f'{tarea_id}'):  # Ajusta según tu convención
                archivos.append({
                    'nombre': nombre,
                    'url': f'/static/archivos_tareas/{nombre}'
                })
    conn.close()
    if not tarea:
        return jsonify({'ok': False, 'msg': 'Tarea no encontrada'}), 404
    tarea_dict = dict(tarea)
    tarea_dict['archivos'] = archivos
    return jsonify(tarea_dict)

# --- API para obtener todas las tareas del usuario ---
@trabajador_blueprint.route('/api/tareas')
def api_tareas_usuario():
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    usuario_id = session.get('usuario')
    grupo_usuario = session.get('grupo')
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    tareas = conn.execute('''
        SELECT * FROM tareas
        WHERE id_usuario_asignado = ? OR TRIM(LOWER(curso_destino)) = TRIM(LOWER(?))
    ''', (usuario_id, grupo_usuario)).fetchall()
    conn.close()
    tareas_list = []
    for t in tareas:
        tarea_dict = dict(t)
        fecha = tarea_dict.get('fecha_vencimiento')
        if fecha:
            try:
                dt = datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                try:
                    dt = datetime.strptime(fecha, '%d/%m/%Y')
                except ValueError:
                    try:
                        dt = datetime.strptime(fecha, '%d-%m-%Y')
                    except ValueError:
                        dt = None
            if dt:
                tarea_dict['fecha_vencimiento'] = dt.strftime('%Y-%m-%d')
        # Buscar todos los archivos asociados a la tarea
        carpeta = os.path.join('static', 'archivos_tareas')
        archivos = []
        if os.path.exists(carpeta):
            for nombre in os.listdir(carpeta):
                if nombre.startswith(f"{t['id']}_") or nombre.startswith(f"{t['id']}-") or nombre.startswith(f"{t['id']}"):
                    archivos.append({
                        'nombre': nombre,
                        'url': f'/static/archivos_tareas/{nombre}'
                    })
        tarea_dict['archivos'] = archivos
        # (Opcional) Mantener ruta_archivo para compatibilidad, pero solo el primero
        tarea_dict['ruta_archivo'] = archivos[0]['nombre'] if archivos else None
        tareas_list.append(tarea_dict)
    return jsonify(tareas_list)

# --- API para obtener notificaciones del trabajador ---
@trabajador_blueprint.route('/api/notificaciones')
def api_notificaciones_trabajador():
    if 'usuario' not in session:
        return jsonify({'ok': False, 'msg': 'No autorizado'}), 401
    usuario_id = session.get('usuario')
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    notificaciones = conn.execute('SELECT * FROM notificaciones WHERE id_usuario = ? ORDER BY id DESC', (usuario_id,)).fetchall()
    conn.close()
    return jsonify({'ok': True, 'notificaciones': [dict(n) for n in notificaciones]})



