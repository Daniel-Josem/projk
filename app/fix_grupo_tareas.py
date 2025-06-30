import sqlite3

# Cambia el curso_destino de todas las tareas a 'Operaciones'
def actualizar_tareas_a_operaciones():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    cur.execute("UPDATE tareas SET curso_destino = 'Operaciones'")
    conn.commit()
    print('Todas las tareas ahora tienen curso_destino = Operaciones')
    conn.close()

if __name__ == '__main__':
    actualizar_tareas_a_operaciones()
