import sqlite3

usuario_id = input('ID de usuario a consultar: ')
conn = sqlite3.connect('gestor_de_tareas.db')
cursor = conn.cursor()
cursor.execute('SELECT id, mensaje, leido, fecha, id_usuario FROM notificaciones WHERE id_usuario = ? ORDER BY id DESC', (usuario_id,))
notificaciones = cursor.fetchall()
conn.close()

if notificaciones:
    print(f"Notificaciones para usuario {usuario_id}:")
    for n in notificaciones:
        print(f"ID: {n[0]}, Mensaje: {n[1]}, Leído: {n[2]}, Fecha: {n[3]}")
else:
    print(f"No hay notificaciones para el usuario {usuario_id}.")
