import sqlite3

# Mostrar las notificaciones más recientes y el id_usuario asociado
def mostrar_notificaciones():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    cur.execute('SELECT id, mensaje, id_usuario, leido FROM notificaciones ORDER BY id DESC LIMIT 20')
    rows = cur.fetchall()
    print('ID | id_usuario | leido | mensaje')
    for row in rows:
        print(f'{row[0]:<3} | {row[2]:<10} | {row[3]:<5} | {row[1]}')
    conn.close()

# Mostrar los líderes y su grupo
def mostrar_lideres():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    cur.execute("SELECT id, nombre_usuario, grupo FROM Usuario WHERE rol = 'lider'")
    rows = cur.fetchall()
    print('ID | nombre_usuario | grupo')
    for row in rows:
        print(f'{row[0]:<3} | {row[1]:<15} | {row[2]}')
    conn.close()

# Mostrar tareas y su curso_destino
def mostrar_tareas():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    cur.execute('SELECT id, titulo, curso_destino FROM tareas ORDER BY id DESC LIMIT 20')
    rows = cur.fetchall()
    print('ID | titulo | curso_destino')
    for row in rows:
        print(f'{row[0]:<3} | {row[1]:<30} | {row[2]}')
    conn.close()

if __name__ == '__main__':
    print('--- Notificaciones recientes ---')
    mostrar_notificaciones()
    print('\n--- Líderes ---')
    mostrar_lideres()
    print('\n--- Tareas recientes ---')
    mostrar_tareas()
