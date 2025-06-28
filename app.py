from flask import Flask, render_template, session, redirect, url_for
import sqlite3
from app.login import login_blueprint
from app.admin import api_blueprint
from app.lider import lider
from app.trabajador import trabajador_blueprint

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Registrar los Blueprints
app.register_blueprint(login_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(lider)
app.register_blueprint(trabajador_blueprint)

# Crear tablas y agregar columna 'grupo' si no existe
def crear_tabla_usuario():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    # Crear la tabla Usuario sin la columna grupo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        nombre_usuario TEXT NOT NULL UNIQUE,
        documento TEXT NOT NULL UNIQUE,
        correo TEXT NOT NULL UNIQUE,
        contraseña TEXT NOT NULL,
        rol TEXT DEFAULT 'trabajador',
        estado TEXT DEFAULT 'activo'
    )''')

    # Verificar si la columna 'grupo' ya existe
    cursor.execute("PRAGMA table_info(Usuario);")
    columnas = [columna[1] for columna in cursor.fetchall()]

    if 'grupo' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN grupo TEXT')
        print("Columna 'grupo' agregada a la tabla Usuario.")
        
    if 'proyecto' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN proyecto TEXT')
        print("Columna 'proyecto' agregada a la tabla Usuario.")

    if 'telefono' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN telefono TEXT')
        print("Columna 'telefono' agregada a la tabla Usuario.")
    
    if 'direccion' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN direccion TEXT')
        print("Columna 'direccion' agregada a la tabla Usuario.")

    # Crear tabla lider
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lider (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      usuario_id INTEGER UNIQUE NOT NULL,
      experiencia TEXT,
      materia TEXT,
      lider TEXT,
      telefono TEXT,
      direccion TEXT,
      FOREIGN KEY(usuario_id) REFERENCES Usuario(id) ON DELETE CASCADE
    );''')

    # Crear tabla tareas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tareas (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      titulo TEXT NOT NULL,
      descripcion TEXT,
      fecha_vencimiento DATE,
      prioridad TEXT,
      estado TEXT DEFAULT 'pendiente',
      id_proyecto INTEGER,
      id_usuario_asignado INTEGER,
      ruta_archivo TEXT,
      curso_destino TEXT,
      FOREIGN KEY(id_usuario_asignado) REFERENCES Usuario(id) ON DELETE SET NULL
    );''')

    # Crear tabla mensajes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emisor_id INTEGER,
    emisor TEXT,
    receptor_id INTEGER,
    mensaje TEXT,
    tipo TEXT DEFAULT 'texto', 
    sticker TEXT, 
    imagen_url TEXT, 
    audio_url TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );''')

    # Crear tabla notificaciones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notificaciones (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      mensaje TEXT NOT NULL,
      leido INTEGER DEFAULT 0,
      fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
      id_usuario INTEGER,
      FOREIGN KEY(id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE
    );''')

    conn.commit()
    conn.close()

# Ejecutar la función al iniciar la app
crear_tabla_usuario()

# Rutas principales
@app.route('/')
def landing():
    return render_template('landingpage.html')

@app.route('/administrador')
def administrador():
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('grupo', None)  # Opcional: limpiar también el grupo
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True)
