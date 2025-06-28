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
    tareas = conn.execute('SELECT * FROM tareas').fetchall()
    conn.close()

    return render_template('lider.html', tareas=tareas)

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
