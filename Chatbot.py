import streamlit as st
import base64
from file_links import file_links
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA
from langchain.vectorstores import Qdrant
from htmlTemplates import css, bot_template, user_template, banner, footer
from langchain.prompts import PromptTemplate
import qdrant_client
import os


# embedding using OPENAI, and get vectors from Qdrant
def get_vector_store_openai():

    # initiate a client
    client = qdrant_client.QdrantClient(
        url=os.getenv("QDRANT_HOST"),
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=10.0, # need to increase timeout limit to avoid timeout
    )

    embeddings = OpenAIEmbeddings()

    vectorstore = Qdrant(
        client=client, 
        collection_name="all-docs-test", 
        embeddings=embeddings, # the embedding method to be used
    )

    return vectorstore


# this function creates a conversation chain with the given llm, memory object and embedding vectors
def get_conversation_chain(vectorstore):

    llm = ChatOpenAI(temperature=0.0, model="gpt-4") # default: gpt-3.5-turbo

    my_memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True, input_key="question")

    template = """
    Your name is Kenji.
    You are a helpful and very friendly assistant that try your best to provide relevant information about the policies, protocols, procedures,
    work instructions, and forms and templates to employees regarding their questions.
    Use the following pieces of context information to answer the question at the end, you should anwser in markdown language,
    your answer should only be based on the chat history and given context, sometimes the context may contain unrelated information.
    If you don't know the answer, just say that you don't know, don't try to make up an answer. Remember that your responds should be friendly and enthusiastic.
    Chat histoty: {chat_history}
    Context information: {context}
    Question: {question}
    Helpful Answer:
    """

    my_prompt = PromptTemplate(
        template=template,
        input_variables=["chat_history", "context", "question"]
    )

    retriever=vectorstore.as_retriever(search_kwargs={"k": 6})

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        verbose=True,
        chain_type_kwargs={
            "prompt": my_prompt,
            "verbose": True,
            "memory": my_memory
        },
        return_source_documents=True,
    )
    
    return qa_chain


# this function handles user input, print out user / robot conversation blocks using pre-defined HTML templates
def handle_user_input(user_question):

    output = st.session_state.chain({'query': user_question}) # "question" for ConversationalRetrievalChain

    history = st.session_state.chain.combine_documents_chain.memory
    # update chat_history
    st.session_state.chat_history = history.chat_memory.messages  # response["chat_history"] for ConversationalRetrievalChain
    
    sources = output["source_documents"]
    doc_set = [] # source file names : links
    doc_links = ""

    for doc in sources:
        source_path = doc.metadata["source"]
        source_file_name = os.path.basename(source_path)
        if source_file_name not in doc_set:
            # get links of files
            try:
                doc_set.append(source_file_name)
                url = file_links[source_file_name]
                doc_links += f'<a href="{url}" target="_blank">{source_file_name}</a>'
            except KeyError:
                print("Error, can't find url link to the file: {source_file_name}")
                doc_links += "Sorry, no links can be provided for this question."
    
    st.session_state.doc_links_hist.append(doc_links)

    # Display the entire chat history in pairs from end to start
    chat_len = len(st.session_state.chat_history)
    # Ensure chat_len is even; if not, something is wrong (since questions and answers should be in pairs)
    if chat_len % 2 == 0:
        for i in range(chat_len - 1, 0, -2):  # Start from the end, move in steps of 2
            user_msg = st.session_state.chat_history[i-1]
            robot_msg = st.session_state.chat_history[i]
            
            # Retrieve the corresponding document links for the current bot response
            doc_links_for_response = st.session_state.doc_links_hist[i // 2]

            # Display user message
            st.write(user_template.replace("{{MSG}}", user_msg.content), unsafe_allow_html=True)
            # Display robot message with document links
            bot_response = bot_template.replace("{{MSG}}", robot_msg.content)
            bot_response = bot_response.replace("{{DOCS}}", doc_links_for_response)
            st.write(bot_response, unsafe_allow_html=True)

    else:
        st.write("Chat history has an odd number of messages which shouldn't happen (it should always be pairs of user and robot messages).")


def main():
    # allow apps to access env variables inside .env document
    load_dotenv()
    base64_string = os.getenv("ENCODED_KEY")
    base64_bytes = base64_string.encode("ascii")
    key_bytes = base64.b64decode(base64_bytes)
    openai_key = key_bytes.decode("ascii")
    os.environ['OPENAI_API_KEY'] = openai_key

    # streamlit config
    st.set_page_config(page_title="ChatBot Kenji", layout="wide")

    st.write(css, unsafe_allow_html=True)

    st.write(banner, unsafe_allow_html=True)

    st.header("ChatBot Kenji 🐻")


    # initialise session_state objects
    if "chain" not in st.session_state:
        # get embeddings
        vectorstore = get_vector_store_openai()
        # initiate conversation chain
        st.session_state.chain = get_conversation_chain(vectorstore)
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = None
    if 'doc_links_hist' not in st.session_state:
        st.session_state.doc_links_hist = []

    user_question = st.text_input(
        "Hi! My name's Kenji. I've read all the detail in ALL Uniting's policies, procedures, work instructions, forms and templates. What would you like to know?"
    ) # ask user to input a question

    if user_question:
        handle_user_input(user_question)

    st.write(footer, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
