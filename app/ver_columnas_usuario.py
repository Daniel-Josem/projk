import sqlite3

def mostrar_columnas_usuario():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(Usuario)")
    columnas = cur.fetchall()
    for col in columnas:
        print(f"Columna: {col[1]}")
    conn.close()

if __name__ == '__main__':
    mostrar_columnas_usuario()
