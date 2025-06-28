from flask import Blueprint, jsonify
import sqlite3
import os

api_blueprint = Blueprint('api', __name__)

def get_db_connection():
    conn = sqlite3.connect('gestor_de_tareas.db')
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

@api_blueprint.route('/api/lider/count')
def api_lider_count():
    conn = get_db_connection()
    cnt = conn.execute('SELECT COUNT(*) FROM Usuario WHERE rol="lider" AND estado="activo"').fetchone()[0]
    conn.close()
    return jsonify(count=cnt)

@api_blueprint.route('/api/trabajadores/count')
def api_trabajadores_count():
    conn = get_db_connection()
    cnt = conn.execute('SELECT COUNT(*) FROM Usuario WHERE estado="activo"').fetchone()[0]
    conn.close()
    return jsonify(count=cnt)
