import mariadb

def get_connection():
    try:
        conn = mariadb.connect(
            user="your_user",
            password="your_password",
            host="localhost",
            port=3306,
            database="your_database"
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None
