import pymysql

DB_CONFIG = {
    "host": "127.0.0.1",      # localhost ki jagah 127.0.0.1 use karo
    "port": 3306,
    "user": "root",
    "password": "root123",           # Agar password hai to yahan likho
    "charset": "utf8mb4",
    "autocommit": True,
    "cursorclass": pymysql.cursors.DictCursor
}


def get_connection():
    config = DB_CONFIG.copy()
    config["database"] = "library"
    return pymysql.connect(**config)


def get_noida_connection():
    config = DB_CONFIG.copy()
    config["database"] = "library_noida"
    return pymysql.connect(**config)


def get_delhi_connection():
    config = DB_CONFIG.copy()
    config["database"] = "library_delhi"
    return pymysql.connect(**config)


def get_mumbai_connection():
    config = DB_CONFIG.copy()
    config["database"] = "library_mumbai"
    return pymysql.connect(**config)