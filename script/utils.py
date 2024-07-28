import sqlite3
import pandas as pd

from openai import OpenAI
import os
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.chat_models import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase


load_dotenv(override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")


def get_ingredients_from_db(db_path):
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM ingredients"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def fetch_ingredients_content(db_path):
    ingredients_df = get_ingredients_from_db(db_path)
    ingredients_list = ingredients_df.to_dict('records')
    context = "Here are the ingredients available:\n"
    for ingredient in ingredients_list:
        context += f"{ingredient['name']}: {ingredient['amount']}克\n"
    
    available_ingredients = ", ".join([ingredient['name'] for ingredient in ingredients_list])
    
    return context, available_ingredients

def fetch_food_incompatibilities_content(emb_model_path, db_path, aviailable_ingredients, k=5): 
    EMBEDDING_MODEL_NAME = "thenlper/gte-small"
    embedding_model = HuggingFaceEmbeddings(
        model_name=emb_model_path,
        # model_name="../embedding_model/gte-small",
        # multi_process=True,
        # model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},  # Set `True` for cosine similarity
    )
    KNOWLEDGE_VECTOR_DATABASE = FAISS.load_local(
        db_path,
        # "../data/food_incomp",
        embeddings=embedding_model,
        allow_dangerous_deserialization=True,
    )
    retrieved_docs = KNOWLEDGE_VECTOR_DATABASE.similarity_search(
        query=aviailable_ingredients,
        k=k,
    )
    return retrieved_docs

def recommend_dish(query, ingredients_context, available_ingredients, incompatibitlies_context):
    # client = OpenAI(
    #     base_url="http://127.0.0.1:8080/v1",
    #     api_key=openai_api_key
    # )
    client = OpenAI(
        api_key=openai_api_key,
    )
    retrieved_docs_text = [
        doc.page_content for doc in incompatibitlies_context
    ]
    context = "\nExtracted documents:\n"
    context += "".join(
        [f"Document {str(i)}:::\n" + doc for i, doc in enumerate(retrieved_docs_text)]
    )
    # print(ingredients_context)
    # print("----------------")
    # print(incompatibitlies_context[0].page_content)
    RAG_PROMPT_TEMPLATE = [
        {
            "role": "system",
            "content": """Using the information contained in the context,
            give a comprehensive answer to the question.
            Respond only to the question asked, response should be concise and relevant to the question.
            Please provide the ingredients and the amount needed for the dish.
            Please provide your answers in Chinese!!!""",
        },
        {
            "role": "user",
            "content": """食物相克信息:
            {context}\n
            
            我现有的食材:
            {ingredients_context}\n
            ---
            你需要严格通过以下格式返回结果：
            ```
            菜名：
            食材和用量：
            ```
            ---
            Now here is the question you need to answer.
            
            Question: {question}""".format(
                context=context, 
                ingredients_context=ingredients_context, 
                question=query
                ),
        },
    ]
    completion = client.chat.completions.create(
        # model="LLaMA_CPP",
        model="gpt-3.5-turbo",
        messages=RAG_PROMPT_TEMPLATE,
        # temperature=0.1
        )
    return completion.choices[0].message.content

def remove_ingredients(dish, ingredients_db_path):
    db = SQLDatabase.from_uri("sqlite:///" + ingredients_db_path)
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        api_key=openai_api_key,
    )
    
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,
    )
    
    agent_executor.invoke(
        {
            "input": """根据菜谱，从数据库中移除被使用的材料以及相应的数量。
                    菜谱：{dish}""".format(dish=dish),
        }
    )
    print("Ingredients removed successfully.")

def get_dish(query):
    current_dir = os.getcwd()
    ingredients_db_path = os.path.join(current_dir, "data", "ingredients.db")
    food_incompatibilities_db_path = os.path.join(current_dir, "data", "food_incomp")
    emb_model_path = os.path.join(current_dir, "embedding_model", "gte-small")
    # ingredients_db_path = "../data/ingredients.db"
    # food_incompatibilities_db_path = "../data/food_incomp"
    
    print("Fetching ingredients content...\n")
    ingredients_context, available_ingredients = fetch_ingredients_content(ingredients_db_path)
    
    print("Fetching food incompatibilities content...\n")
    incompatibitlies_context = fetch_food_incompatibilities_content(emb_model_path, food_incompatibilities_db_path, available_ingredients)
    
    print("Recommend dish...\n")
    dish = recommend_dish(query, ingredients_context, available_ingredients, incompatibitlies_context)
    return dish


def main(query):
    ingredients_db_path = "../data/ingredients.db"
    food_incompatibilities_db_path = "../data/food_incomp"
    emb_model_path = "../embedding_model/gte-small"
    
    print("Fetching ingredients content...\n")
    ingredients_context, available_ingredients = fetch_ingredients_content(ingredients_db_path)
    
    print("Fetching food incompatibilities content...\n")
    incompatibitlies_context = fetch_food_incompatibilities_content(emb_model_path, food_incompatibilities_db_path, available_ingredients)
    
    print("Recommend dish...\n")
    dish = recommend_dish(query, ingredients_context, available_ingredients, incompatibitlies_context)
    print(dish)

    print("Removing ingredients...\n")
    remove_ingredients(dish, ingredients_db_path)

if __name__ == "__main__":
    query = "请你根据我现有的食材以及食材数量，推荐【一道菜】。告诉我所需食材以及相对应的克数。"
    main(query)
