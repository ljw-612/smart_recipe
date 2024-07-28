from dotenv import load_dotenv
from PyPDF2 import PdfReader
from sklearn.metrics.pairwise import cosine_similarity

from langchain.docstore.document import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import DistanceStrategy

from openai import OpenAI
import os
from dotenv import load_dotenv

from tqdm.notebook import tqdm
import pandas as pd
from typing import Optional, List, Tuple
from datasets import Dataset
import matplotlib.pyplot as plt

import gc


# Load the environment variables
load_dotenv()

# Initialize the OpenAI API client
openai_api_key = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=openai_api_key)

MARKDOWN_SEPARATORS = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
]

EMBEDDING_MODEL_NAME = "thenlper/gte-small"


def extract_text(pdf_files):
    """
    Function to extract the text from a PDF file

    Args:
        pdf_file (file): The PDF files to extract the text from

    Returns:
        text (str): The extracted text from the PDF file
    """

    # Initialize the raw text variable
    text = ""

    # Iterate over the documents
    for pdf_file in pdf_files:

        # Read the PDF file
        pdf_reader = PdfReader(pdf_file)

        # Extract the text from the PDF pages and add it to the raw text variable
        for page in pdf_reader.pages:
            text += page.extract_text()

    return text


def split_documents(
    chunk_size: int,
    knowledge_base: List[LangchainDocument],
    tokenizer_name: Optional[str] = EMBEDDING_MODEL_NAME,
) -> List[LangchainDocument]:
    """
    Split documents into chunks of maximum size `chunk_size` tokens and return a list of documents.
    """
    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        AutoTokenizer.from_pretrained(tokenizer_name),
        chunk_size=chunk_size,
        chunk_overlap=int(chunk_size / 10),
        add_start_index=True,
        strip_whitespace=True,
        separators=MARKDOWN_SEPARATORS,
    )

    docs_processed = []
    for doc in knowledge_base:
        docs_processed += text_splitter.split_documents([doc])

    # Remove duplicates
    unique_texts = {}
    docs_processed_unique = []
    for doc in docs_processed:
        if doc.page_content not in unique_texts:
            unique_texts[doc.page_content] = True
            docs_processed_unique.append(doc)

    return docs_processed_unique


def get_vector_db(
    raw_text: str,
):
    RAW_KNOWLEDGE_BASE = [
        LangchainDocument(
            page_content=raw_text, metadata={"source": "food imcompatibility"}
        )
    ]
    docs_processed = split_documents(
        512,  # We choose a chunk size adapted to our model
        RAW_KNOWLEDGE_BASE,
        tokenizer_name=EMBEDDING_MODEL_NAME,
    )
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        # multi_process=True,
        # model_kwargs={"device": "cuda"},
        encode_kwargs={
            "normalize_embeddings": True
        },  # Set `True` for cosine similarity
    )
    KNOWLEDGE_VECTOR_DATABASE = FAISS.from_documents(
        docs_processed, embedding_model, distance_strategy=DistanceStrategy.COSINE
    )
    return KNOWLEDGE_VECTOR_DATABASE


def answer_with_rag(query: str, db: FAISS, client: OpenAI, k=2):
    retrieved_docs = db.similarity_search(query=query, k=k)
    print(
        "\n==================================Top document=================================="
    )
    print(retrieved_docs[0].page_content)

    retrieved_docs_text = [doc.page_content for doc in retrieved_docs]
    context = "\nExtracted documents:\n"
    context += "".join(
        [f"Document {str(i)}:::\n" + doc for i, doc in enumerate(retrieved_docs_text)]
    )
    RAG_PROMPT_TEMPLATE = [
        {
            "role": "system",
            "content": """Using the information contained in the context,
    give a comprehensive answer to the question.
    Respond only to the question asked, response should be concise and relevant to the question.""",
        },
        {
            "role": "user",
            "content": """Context:
    {context}
    ---
    Now here is the question you need to answer.

    Question: {question}""".format(
                context=context, question=query
            ),
        },
    ]

    gc.collect()

    completion = client.chat.completions.create(
        model="LLaMA_CPP", messages=RAG_PROMPT_TEMPLATE
    )
    # answer = completion.choices[0].message.content
    print(completion.choices[0].message)
    # return answer


if __name__ == "__main__":
    raw_text = extract_text(pdf_files=["../data/data.pdf"])

    KNOWLEDGE_VECTOR_DATABASE = get_vector_db(raw_text)

    client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key=openai_api_key)

    query = "鲫鱼最好不和什么一起吃？"

    answer = answer_with_rag(
        query=query,
        db=KNOWLEDGE_VECTOR_DATABASE,
        client=client,
    )
