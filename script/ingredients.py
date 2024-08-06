import os
import sqlite3


def check_db_exists(database_name):
    return os.path.exists(database_name)


def create_database(database_name):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute(
        "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='ingredients'"
    )
    if c.fetchone()[0] == 0:
        c.execute(
            """CREATE TABLE ingredients 
            (id INTEGER PRIMARY KEY, 
            name TEXT, 
            amount REAL)"""
        )
    conn.commit()
    print("Table created.")


def insert_ingredient(database_name, name, amount):
    conn = sqlite3.connect(database_name)
    c = conn.cursor()
    c.execute("SELECT * FROM ingredients WHERE name=?", (name,))
    result = c.fetchone()  # result: (id[0], name[1], amount[2])

    if result:
        new_quantity = result[2] + amount
        c.execute("UPDATE ingredients SET amount=? WHERE name=?", (new_quantity, name))
    else:
        c.execute(
            "INSERT INTO ingredients (name, amount) VALUES (?, ?)", (name, amount)
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    database_name = "../data/ingredients.db"

    test_ingredient = [
        ("面粉", 250),
        ("糖", 200),
        ("鸡蛋", 300),
        ("茄子", 500),
        ("猪肉", 500),
        ("鸡肉", 500),
        ("牛肉", 500),
        ("羊肉", 500),
    ]

    if not check_db_exists(database_name):
        print("Creating database...")

        create_database(database_name)
        print("Inserting ingredients...")
        for ingredient in test_ingredient:
            insert_ingredient(database_name, ingredient[0], ingredient[1])
    else:
        print("Inserting ingredients...")
        for ingredient in test_ingredient:
            insert_ingredient(database_name, ingredient[0], ingredient[1])
