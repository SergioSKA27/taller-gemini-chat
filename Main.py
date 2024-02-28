import streamlit as st
import google.generativeai as genai
from time import sleep
import asyncio

genai.configure(api_key=st.secrets["GEN_AI_KEY"])


@st.cache_resource
def load_genmodel():
    return genai.GenerativeModel("gemini-pro")


def stream_text():
    """Stream text to the app"""
    for w in st.session_state.text_stream.split(" "):
        yield w + " "
        sleep(0.05)


async def generate_response(prompt,model=load_genmodel()):
    with st.spinner("Generando Respuesta..."):
        await asyncio.sleep(.1)
        response = model.generate_content(prompt)
    return response.text



if 'chatHistory' not in st.session_state:
    st.session_state.chatHistory = []

if 'firstTime' not in st.session_state:
    st.session_state.firstTime = ''



if 'text_stream' not in st.session_state:
    st.session_state.text_stream = ""

if 'stream_last' not in st.session_state:
    st.session_state.stream_last = True

if st.session_state.chatHistory == [] and st.session_state.firstTime == '':
    gretting =  asyncio.run(generate_response("Presentate con el usuario y dale la bienvenida, eres un chatbot que responde preguntas sobre programación, ciencia de datos, matemáticas y temas relacionados."))
    st.session_state.firstTime = gretting
    st.session_state.text_stream = gretting

    with st.chat_message("assistant"):
        st.write_stream(stream_text)
else:
    with st.chat_message("assistant"):
        st.write(st.session_state.firstTime)


prompt = st.chat_input("Escribe tu mensaje")


for message in st.session_state.chatHistory:
    if message['role'] == 'user':
        with st.chat_message("user"):
            if message == st.session_state.chatHistory[-1] and st.session_state.stream_last:
                st.session_state.text_stream = message['parts'][0]
                st.write_stream(stream_text)
                st.session_state.stream_last = False
            else:
                st.write(message['parts'][0])
    else:
        with st.chat_message("assistant"):
            if message == st.session_state.chatHistory[-1] and st.session_state.stream_last:
                st.session_state.text_stream = message['parts'][0]
                st.write_stream(stream_text)
                st.session_state.stream_last = False
            else:
                st.write(message['parts'][0])

if prompt and prompt != '':
    question =  {
        'role': 'user',
        'parts': [prompt]
    }

    st.session_state.chatHistory.append(question)

    try:
        response =  asyncio.run(generate_response(st.session_state.chatHistory))
        r = {
            'role': 'model',
            'parts': [response]
        }
        st.session_state.chatHistory.append(r)
        st.session_state.stream_last = True
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
        del st.session_state.chatHistory[-1]
        st.rerun()
