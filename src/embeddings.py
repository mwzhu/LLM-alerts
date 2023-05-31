import os
from dotenv import load_dotenv
import numpy as np
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import DocArrayHnswSearch
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
import re
from langchain.vectorstores import FAISS
import json
import requests
import json
load_dotenv()
openAiApiKey = os.getenv("OPENAI_API_KEY")


# The get_similar_embeddings function
def get_similar_embeddings(query='whats price of eth', k=3, vector_dir='vectordb-visuals'):
    embeddings = OpenAIEmbeddings(openai_api_key=openAiApiKey)
    db = FAISS.load_local(vector_dir, embeddings=embeddings)

    # get similar embeddings
    similar_embeddings = db.similarity_search_with_score(query, k=k)

    result = []
    for doc, score in similar_embeddings:
        # Combine page_content and metadata into a string
        combined_string = doc.page_content + ' ' + ' '.join([f'{k}:{v}' for k, v in doc.metadata.items()])
        result.append(combined_string)

    return result

# USAGE:
# result = get_similar_embeddings('whats price of eth', k=2. 'vectordb-visuals')
# print(result)

# FOR CREATING VECTOR STORE (INCLUDING UPDATES)
# Split the examples into tuples of (user_input, command)
def split_into_tuples(string):
    pattern = r'===========\n(.*?)\n\+(.*?)\+'
    matches = re.findall(pattern, string, re.DOTALL)

    # Create tuples of (user_input, command)
    tuples = [(match[0].strip(), match[1].strip()) for match in matches]

    return tuples

# The create_vector_store function
def create_vector_store(inputFile=None, outputDirectory=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    inputFile = os.path.join(current_dir, 'examples.txt')

    examples = TextLoader(inputFile).load()
    examples_string = examples[0].page_content
    examples = split_into_tuples(examples_string)

    # Create embeddings of (vector, metadata) tuples
    texts = []
    metadatas = []
    for user_input, command in examples:
        texts.append(user_input)
        metadatas.append(json.loads(command))
    
    embeddings = OpenAIEmbeddings(openai_api_key=openAiApiKey)

    # Create the vector store using DocArrayHnswSearch
    db = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
    db.save_local(outputDirectory)
    print('Vector store created at: ', outputDirectory)

    return db



# usage:
# db = create_vector_store(inputFile='examples.txt', outputDirectory='vectordb-visuals')
# print(db)
