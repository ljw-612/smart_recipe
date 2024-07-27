import streamlit as st
import openai

import pandas as pd
import sqlite3

import os
from dotenv import load_dotenv

from utils import *

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

def app():
    ingredients_db_path = "../data/ingredients.db"
    
    
    query = "请你根据我现有的食材以及食材数量，推荐【一道菜】。告诉我所需食材以及相对应的克数。"
    
    st.title("Recipe Recommendation System")
    
    st.write("#### Available Ingredients in the Database")
    df = fetch_db(ingredients_db_path)
    st.dataframe(df)
    
    if 'generated_recipe' not in st.session_state:
        st.session_state['generated_recipe'] = ""

    st.button("Generate a Recipe for Me", on_click=generate_recipe_callback, args=(query,))

    if st.session_state['generated_recipe']:
        st.write("## Generated Recipe")
        st.text(st.session_state['generated_recipe'])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Accept this Recipe"):
                st.success("Recipe accepted!")
                st.success("Ingredients removed from the database....")
                print(st.session_state['generated_recipe'])
                remove_ingredients(st.session_state['generated_recipe'], ingredients_db_path)
                st.session_state['generated_recipe'] = ""  # Reset recipe
                st.dataframe(fetch_db(ingredients_db_path))
        with col2:
            if st.button("Regenerate"):
                st.session_state['generated_recipe'] = generate_recipe(query)
                st.experimental_rerun()
                # print("re generated recipe: ", st.session_state['generated_recipe'])


def generate_recipe_callback(query):
    st.session_state['generated_recipe'] = generate_recipe(query)
    

if __name__ == "__main__":
    app()