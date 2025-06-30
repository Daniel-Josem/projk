from flask import Flask, render_template, session, redirect, url_for
import sqlite3
from app.login import login_blueprint
from app.admin import api_blueprint
from app.lider import lider
from app.trabajador import trabajador_blueprint
from app.recuperar import recuperar_bp

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Registrar los Blueprints
app.register_blueprint(login_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(lider)
app.register_blueprint(trabajador_blueprint)
app.register_blueprint(recuperar_bp)

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

# Crear tabla proyectos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS proyectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        descripcion TEXT,
        grupo TEXT NOT NULL,
        estado TEXT DEFAULT 'activo',
        fecha_inicio TEXT,
        fecha_fin TEXT
    );
    ''')
    # Insertar proyectos por defecto si no existen
    proyectos_defecto = [
        ('Torre Prado', 'Construcción de edificio residencial Torre Prado.', 'Grupo1', '2025-07-01'),
        ('Torre Milton', 'Infraestructura residencial de alto nivel.', 'Grupo2', '2025-07-01'),
        ('Fiscalía Medellin', 'Ampliación sede judicial Medellín.', 'Grupo3', '2025-07-01'),
        ('San Velente', 'Complejo habitacional San Velente.', 'Grupo4', '2025-07-01'),
        ('Anay Beauty', 'Diseño y obra para la sede Anay Beauty.', 'Grupo5', '2025-07-01')
    ]

    for nombre, descripcion, grupo, fecha_inicio in proyectos_defecto:
        cursor.execute('''
            INSERT OR IGNORE INTO proyectos (nombre, descripcion, grupo, fecha_inicio)
            VALUES (?, ?, ?, ?)
        ''', (nombre, descripcion, grupo, fecha_inicio))


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
  # Verificar si la columna 'fecha_registro' ya existe en la tabla tareas
    cursor.execute("PRAGMA table_info(tareas);")
    columnas = [columna[1] for columna in cursor.fetchall()]

    if 'fecha_registro' not in columnas:
        cursor.execute("ALTER TABLE tareas ADD COLUMN fecha_registro DATE")
        cursor.execute("UPDATE tareas SET fecha_registro = DATE('now') WHERE fecha_registro IS NULL")
        print("Columna 'fecha_registro' agregada a la tabla tareas.")


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

# Insertar tareas de demostracion si no existen
#Añadido por majo
def insertar_tareas_demo():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    # Verifica si ya existen tareas para evitar duplicados
    cursor.execute("SELECT COUNT(*) FROM tareas")
    total = cursor.fetchone()[0]

    if total == 0:
        cursor.execute('''
            INSERT INTO tareas (
                titulo, descripcion, id_proyecto, id_usuario_asignado, fecha_vencimiento, fecha_registro
            ) VALUES (?, ?, ?, ?, ?, DATE('now'))
        ''', ('Revisión de planos', 'Revisar diseño estructural', 1, 2, '2025-07-10'))

        conn.commit()
        print("Tarea de prueba insertada correctamente.")
    else:
        print("Ya existen tareas, no se insertaron duplicados.")

    conn.close()

insertar_tareas_demo()
def crear_usuario_asignado_demo():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # Verificar si ya existe un usuario con ID 2
    cursor.execute("SELECT id FROM Usuario WHERE id = 2")
    usuario = cursor.fetchone()

    if not usuario:
        # Crear un usuario de prueba con ID 2
        cursor.execute('''
            INSERT INTO Usuario (id, nombre_completo, nombre_usuario, documento, correo, contraseña, rol, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (2, 'Trabajador Demo', 'demo_user', '987654321', 'demo@empresa.com', '1234', 'trabajador', 'activo'))
        conn.commit()
        print("✅ Usuario de prueba con ID 2 creado.")
    else:
        print("ℹ️ Usuario con ID 2 ya existe.")

    conn.close()
crear_usuario_asignado_demo()

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
