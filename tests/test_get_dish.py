import os
import sqlite3
import pytest
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from script.utils import get_dish

# def test_get_dish():
#     query = "请你根据我现有的食材以及食材数量，推荐【一道菜】。告诉我所需食材以及相对应的克数。"
#     dish = get_dish(query)
    
#     assert type(dish) == str
#     assert "菜名" in dish
#     assert "食材和用量" in dish