#import streamlit as st
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# 1. Vectorise the sales response csv data
loader = CSVLoader(file_path="test_csv.csv")
documents = loader.load()

embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(documents, embeddings)

# 2. Function for similarity search
def retrieve_info(query):
    flag = True
    docs_and_scores = db.similarity_search_with_score(query, k=4)
    bigger_score = 1
    page_contents_array = []
    for doc in docs_and_scores:
        if doc[-1] < 0.4:
            if doc[-1] < bigger_score:
              bigger_score = doc[-1]
            page_contents_array.append(doc[0].page_content)
    if bigger_score > 0.4:
      flag = False
    return page_contents_array, flag

# 3. Setup LLMChain & prompts
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

template = """
As a customer service representative dedicated to happy answers, 
your task is to craft responses to prospects by closely following established best practices.
When you receive a message from a prospect, 
you must analyze it and then respond in a manner that mirrors the style, tone, and argumentation of previously successful interactions. 
This approach ensures consistency and leverages proven strategies to engage and convert prospects.

Instructions for crafting a response:
1. Ensure your reply closely aligns with or directly mirrors the established best practices. 
This includes matching the length, tone of voice, logical structure, and other relevant details that have historically contributed to successful communications.

2. If user greets you, you greet back and do nothing more.

3. Speak non-formally

Below is a message from a prospect that requires your attention:
{message}

Accompanying this message, you’ll find a compilation of best practices that have been effective in similar situations:
{best_practice}

Based on the information provided, draft the ideal response to send to this prospect, 
ensuring it embodies the principles and characteristics of the outlined best practices.
"""

prompt = PromptTemplate(
    input_variables=["message", "best_practice"],
    template=template
)

chain = LLMChain(llm=llm, prompt=prompt)


# 4. Retrieval augmented generation
def generate_response(message):
    best_practice, flag = retrieve_info(message)
    if flag:
      response = chain.run(message=message, best_practice=best_practice)
    else:
      response = "Malesef istediğiniz bilgiye sahip değilim"
    return response
