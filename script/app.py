import streamlit as st

import pandas as pd
import sqlite3

import os
from dotenv import load_dotenv

from utils import *
from ingredients import *

load_dotenv(override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")


def generate_recipe(query):
    dish = get_dish(query)
    return dish


def fetch_db(ingredients_db_path):
    conn = sqlite3.connect(ingredients_db_path)
    query = "SELECT * FROM ingredients"
    df = pd.read_sql_query(query, conn)
    return df


def generate_recipe_callback(query):
    st.session_state["generated_recipe"] = generate_recipe(query)


def app():
    current_dir = os.getcwd()
    ingredients_db_path = os.path.join(current_dir, "data", "ingredients.db")
    print(f"Ingredients DB Path: {ingredients_db_path}")

    query = "请你根据我现有的食材以及食材数量，推荐【一道菜】。告诉我所需食材以及相对应的克数。"

    st.title("Recipe Recommendation System")

    st.write("#### Available Ingredients in the Database")
    df = fetch_db(ingredients_db_path)
    ingredients_table = st.dataframe(df)

    if "generated_recipe" not in st.session_state:
        st.session_state["generated_recipe"] = ""

    st.button(
        "Generate a Recipe for Me", on_click=generate_recipe_callback, args=(query,)
    )

    if st.session_state["generated_recipe"]:
        st.write("## Generated Recipe")
        st.text(st.session_state["generated_recipe"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Accept this Recipe"):
                st.success("Recipe accepted!")
                st.success("Ingredients removed from the database....")
                print(st.session_state["generated_recipe"])
                remove_ingredients(
                    st.session_state["generated_recipe"], ingredients_db_path
                )
                st.session_state["generated_recipe"] = ""  # Reset recipe
                ingredients_table.dataframe(fetch_db(ingredients_db_path))
        with col2:
            if st.button("Regenerate"):
                st.session_state["generated_recipe"] = generate_recipe(query)
                st.rerun()

    st.write("### Add New Ingredient to the Database")
    new_ingredient = st.text_input("Ingredient Name")
    new_quantity = st.number_input("Quantity (in grams)", step=1)

    if st.button("Add Ingredient"):
        if new_ingredient and new_quantity > 0:
            insert_ingredient(ingredients_db_path, new_ingredient, new_quantity)
            st.success(
                f"Added {new_ingredient} ({new_quantity} grams) to the database."
            )
            ingredients_table.dataframe(fetch_db(ingredients_db_path))
        else:
            st.error("Please enter a valid ingredient name and quantity.")


if __name__ == "__main__":
    app()
