import psycopg2

def create_db(conn):
    with conn.cursor() as cur:

        cur.execute("""
        CREATE TABLE IF NOT EXISTS client (
            client_id SERIAL PRIMARY KEY,
            first_name VARCHAR(20) NOT NULL,
            last_name VARCHAR(20) NOT NULL,
            email VARCHAR(60)
            );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phone (
            phone_number VARCHAR(60),
            client_id INTEGER REFERENCES client(client_id)
            );
        """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute(f"""
                INSERT INTO client(first_name, last_name, email)
                VALUES ('{first_name}', '{last_name}', '{email}')
                RETURNING client_id;
                """)
        client_id = cur.fetchone()[0]
        if phones != None:
            for phone in phones:
                cur.execute(f"""
                        INSERT INTO phone
                        VALUES ('{phone}', '{client_id}');
                        """)
            conn.commit()

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute(f"""
                    INSERT INTO phone
                    VALUES ('{phone}', '{client_id}');
                    """)
        conn.commit()
def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        changes = f'client_id = {client_id}'
        if first_name != None:
            changes += f", first_name = '{first_name}'"
        if last_name != None:
            changes += f", last_name = '{last_name}'"
        if email != None:
            changes += f", email = '{email}'"
        cur.execute(f"""
                    UPDATE client
                    SET {changes}
                    WHERE client_id = {client_id}
                    """)
        conn.commit()
        if phones != None:
            delete_phones(conn, client_id)
            for phone in phones:
                add_phone(conn, client_id, phone)
            conn.commit()
def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute(f"""                                            
                    DELETE FROM phone                               
                    WHERE client_id = {client_id} AND phone_number = '{phone}';                
                    """)
        conn.commit()

def delete_client(conn, client_id):
    delete_phones(conn, client_id)
    with conn.cursor() as cur:
        cur.execute(f"""                                                           
                    DELETE FROM client                                              
                    WHERE client_id = {client_id};    
                    """)
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        conditions = '1 > 0'
        if first_name != None:
            conditions += f" AND c.first_name = '{first_name}'"
        if last_name != None:
            conditions += f" AND c.last_name = '{last_name}'"
        if email != None:
            conditions += f" AND c.email = '{email}'"
        if phone != None:
            conditions += f" AND p.phone_number = '{phone}'"
        cur.execute(f"""                                                     
                    SELECT DISTINCT c.client_id FROM client c
                    JOIN phone p ON c.client_id = p.client_id                                      
                    WHERE {conditions}
                    ORDER BY c.client_id;                           
                    """)                                                     
        return [i[0] for i in cur.fetchall()]


def delete_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        DROP TABLE phone;
        DROP TABLE client;
        """)
        conn.commit()

def delete_phones(conn, client_id):
    with conn.cursor() as cur:
        cur.execute(f"""                                                        
                    DELETE FROM phone                                           
                    WHERE client_id = {client_id}; 
                    """)
        conn.commit()

password = '' # введите свой пароль PostgresSQL
with psycopg2.connect(database="clients_db", user="postgres", password=password) as conn:
#    delete_db(conn)
    create_db(conn)
    add_client(conn, 'Petr', 'Ivanov', 'ivanov@gmail.com', ['89001234567', '89002345678'])
    add_client(conn, 'Petr', 'Petrov', 'petrov@gmail.com', ['89003456789'])
    add_client(conn, 'Sidor', 'Sidorov', 'sidorov@gmail.com')
    add_client(conn, 'Fedor', 'Fedorov', 'fedorov@gmail.com', ['2356789'])
    add_phone(conn, 3, '89004567890')
    change_client(conn, 3, first_name = 'MrSidr')
    change_client(conn, 2, last_name = 'Pupkin', email = 'pupkin@gmail.com', phones = ['2246789', '2896758'])
    delete_phone(conn, 1, '89002345678')
    delete_client(conn, 4)
    print(find_client(conn, first_name = 'Petr'))

conn.close()