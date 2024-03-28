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
loader = CSVLoader(file_path="./test_csv.csv")
documents = loader.load()


embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(documents, embeddings)

# 2. Function for similarity search
def retrieve_info(query):
    flag = True
    docs_and_scores = db.similarity_search_with_score(query, k=4)
    print(docs_and_scores)
    counter = 0
    most_similar_docs = ""
    bigger_score = 1
    page_contents_array = []
    for doc in docs_and_scores:
        if doc[-1] < 0.4:
            if doc[-1] < bigger_score:
              bigger_score = doc[-1]
            page_contents_array.append(doc[0].page_content)
    print(bigger_score)
    if bigger_score > 0.4:
      flag = False
    print(page_contents_array)
    return page_contents_array, flag


# 3. Setup LLMChain & prompts
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

template = """
You are a happy representative.
I will share a prospect's message with you and you will give me the best answer that
I should send to this prospect based on past best practies,
and you will follow ALL of the rules below:

1/ Response should be very similar or even identical to the past best practies,
in terms of length, ton of voice, logical arguments and other details

Below is a message I received from the prospect:
{message}

Here is a list of best practies of how we normally respond to prospect in similar scenarios:
{best_practice}

Please write the best response that I should send to this prospect:
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
