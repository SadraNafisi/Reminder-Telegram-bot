import psycopg2

def connect_database():
    conn = psycopg2.connect(database='postgres',
                            user='root',
                            host='himalayas.liara.cloud',
                            password='M5cdvDnzgYo8Y9sW9FDJz3ra',
                            port=31190)
    return conn
def retrieve_Query(query):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows
def dml_Query(query): #data manuplating language form
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    conn.close()