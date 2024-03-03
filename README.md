# Policy_Docs_ChatBot
This is a ChatBot that answers questions about policy documents. Note that the user needs to update information like setting environment variables (API keys, SharePoint user and password) and update domain names where necessary with their own to make it work.

In detail, the ChatBot works in the following way:

**Document Embedding**
A pre-processing program called “PolicyDocProcessing.ipynb” extracts the text from all PDF files – this Python program runs locally and against PDFs downloaded to the local machine. (documents on the Policy hub, all Word, PDFs and Excel documents, everything other than the HTML pages in the Policy Hub). “PolicyDocProcessing.ipynb” then divides the input documents into equal-length chunks of text. Then, “PolicyDocProcessing.ipynb” uses the OpenAIEmbedding() method to encode each chunk as a numerical vector. The embeddings capture the semantic similarities between chunks of text. A detailed explanation of embeddings can be found here: https://www.tensorflow.org/text/guide/word_embeddings

**Build a vector store**
The second step in “PolicyDocProcessing.ipynb” is to build a vector database to store the generated vectors resulting from the embeddings from the OpenAIEmbeddings(). There are several platforms that could be considered for this purpose; the chatbot uses Qdrant (https://qdrant.tech/) because it is free and has adequate performance for small-scale documents. Besides vector storage on the cloud, vector databases also provide an efficient similarity search that can find the most relevant vectors (document chunks) from the database given a query vector (a question embedding). 

**Question answering**
When the user asks a question to the ChatBot app, the question is embedded using the same embedding method OpenAIEmbeddings() used above for storing the document chunks, and the vector store performs a semantic search to find the most relevant chunks in the vector database to the question posed. The top results and the questions are sent to OpenAI to generate the final answer. The LangChain library connects the vector store and the OpenAI LLM. Note that this template inherently restricts the language model only to answer questions about the given context. General questions, that might be asked of ChatGPT, can be posed but cannot be answered by the app. When asked something not within scope, like “What is the capital of Boliva?” Franklin will respond with, “I don't know the answer to the question as it is unrelated to the provided context and chat history.”.
