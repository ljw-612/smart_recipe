import os
import sqlite3
import pytest
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from script.utils import get_ingredients_from_db, remove_ingredients
from script.ingredients import insert_ingredient


@pytest.fixture
def setup_database():
    # Create a temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    conn = sqlite3.connect(temp_db.name)
    cursor = conn.cursor()

    # Create ingredients table
    cursor.execute(
        """
        CREATE TABLE ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount INTEGER NOT NULL
        )
    """
    )
    conn.commit()

    # Insert some initial data
    cursor.executemany(
        """
        INSERT INTO ingredients (name, amount) VALUES (?, ?)
    """,
        [("糖", 200), ("牛肉", 500), ("羊肉", 500), ("猪肉", 1000)],
    )
    conn.commit()
    conn.close()

    yield temp_db.name

    os.remove(temp_db.name)


def test_get_ingredients_from_db(setup_database):
    db_path = setup_database
    ingredients_df = get_ingredients_from_db(db_path)
    assert len(ingredients_df) == 4
    assert ingredients_df["name"].tolist() == ["糖", "牛肉", "羊肉", "猪肉"]
    assert ingredients_df["amount"].tolist() == [200, 500, 500, 1000]


def test_insert_ingredient(setup_database):
    db_path = setup_database
    insert_ingredient(db_path, "鸡蛋", 300)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingredients WHERE name = ?", ("鸡蛋",))
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[1] == "鸡蛋"
    assert result[2] == 300


# def test_remove_ingredients(setup_database):
#     db_path = setup_database
#     sample_dish = """
#     菜名：红烧肉
#     食材和用量：糖 200克，猪肉 500克
#     """
#     remove_ingredients(sample_dish, db_path)
#     ingredients_df = get_ingredients_from_db(db_path)
#     print(ingredients_df)
#     assert ingredients_df['name'].tolist() == ['糖', '牛肉', '羊肉', '猪肉']
#     assert ingredients_df['amount'].tolist() == [0, 500, 500, 500]


if __name__ == "__main__":
    pytest.main()
