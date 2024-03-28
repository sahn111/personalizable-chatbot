import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from generate_response_service import generate_response
import time
load_dotenv()

st.title("Fitness Center Chat Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.sidebar:
    st.info("Merhaba, şuanda bulunduğunuz sayfadaki salon bilgilerinin tamamı rastgele bir biçimde GPT-4 tarafından oluşturulmuştur.")

    st.info("""
        Birazdan konuşacağınız chatbotun çalışma prensibi şu şekildedir\n
    
        Belirli bir dosyanın içinde gelebilecek sorulara verilecek cevaplar tutulmaktadır.\n
        Embedding yöntemi ile gireceğiniz soruya en yakın 3 soru kalıbı bulunarak bunların cevaplarını alırız.
        GPT-3.5 kullanarak elimizde olan tahmini 3 cevabı size anlamlı bir bütün olarak döndürmeye çalışmaktayız.

        Sorduğunuz sorunun konu dışı olduğunu fark ederse bot bu sorunun cevabını bilmediğini belirtmelidir.

        Her bir soru-cevabın tahmini ortalama ücreti 0,0006$ olmaktadır. 
    """)

    st.error("Dikkat! Chatbot hala test aşamasındadır\
                ve hata yapabilmektedir. Edindiğiniz bilgilere riayet etmeyiniz.")

    st.info(
    """
    Created by Ali Sahin.\n

    Tech Stack:\n
        - Streamlit
        - Python
        - OpenAI
        - langchain
            \t* FAISS
            \t* LLMChain
    """)

    with st.spinner("Bot Hazırlanıyor..."):
        time.sleep(5)
        st.success("Hazır!")

# Accept user input
if prompt := st.chat_input("Soru sorun..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

 # Display assistant response in chat message container
    with st.chat_message("assistant"):
        stream = generate_response(st.session_state.messages[-1]["content"])
        response = st.write(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})