from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import sqlite3
import os
from datetime import datetime

trabajador_blueprint = Blueprint('trabajador', __name__)

@trabajador_blueprint.route('/trabajador')
def trabajador():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    grupo_usuario = session.get('grupo')
    print(f"Grupo del usuario logueado: {grupo_usuario}")

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    tareas = conn.execute('''
        SELECT * FROM tareas
        WHERE TRIM(LOWER(curso_destino)) = TRIM(LOWER(?))
    ''', (grupo_usuario,)).fetchall()
    conn.close()

    print(f"Tareas encontradas: {tareas}")

    # Formatear fecha_vencimiento a YYYY-MM-DD para el calendario
    tareas_list = []
    for t in tareas:
        tarea_dict = dict(t)
        fecha = tarea_dict.get('fecha_vencimiento')
        if fecha:
            try:
                # Intenta parsear fechas tipo DD/MM/YYYY o similares
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

    return render_template('trabajador.html', tareas=tareas_list)

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
    # Guardar archivo en carpeta con prefijo de id de tarea
    carpeta_destino = os.path.join('static', 'archivos_tareas')
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
    nombre_archivo = f"{tarea_id}_{archivo.filename}"
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
    archivo.save(ruta_destino)
    # Marcar tarea como completada automáticamente
    try:
        conn = sqlite3.connect('gestor_de_tareas.db')
        cur = conn.cursor()
        cur.execute('UPDATE tareas SET estado = ? WHERE id = ?', ('completado', tarea_id))
        conn.commit()
        conn.close()
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



