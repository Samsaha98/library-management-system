import pymysql

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root123",
    "charset": "utf8mb4",
    "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor
}


# Main Database
def get_connection():
    config = DB_CONFIG.copy()
    config["database"] = "library"
    return pymysql.connect(**config)


# Noida Database
def get_noida_connection():
    config = DB_CONFIG.copy()
    config["database"] = "library_noida"
    return pymysql.connect(**config)


# Delhi Database
def get_delhi_connection():
    config = DB_CONFIG.copy()
    config["database"] = "library_delhi"
    return pymysql.connect(**config)


# Mumbai Database
def get_mumbai_connection():
    config = DB_CONFIG.copy()
    config["database"] = "library_mumbai"
    return pymysql.connect(**config)


# Campus Helper
def get_campus_connection(campus):

    campus = campus.lower()

    if campus == "noida":
        return get_noida_connection()

    elif campus == "delhi":
        return get_delhi_connection()

    elif campus == "mumbai":
        return get_mumbai_connection()

    else:
        return get_noida_connection()