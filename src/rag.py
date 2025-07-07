### This file to handle embedding and vector storage using ###

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os
from utils import load_document

def setup_rag(data_path):
    # Load and chunk documents 
    document = load_document(data_path)
    
    # Create embedding 
    embeddings = HuggingFaceEmbeddings(model_name = "intfloat/multilingual-e5-small")
    
    # Create FAISS vector store 
    vector_store = FAISS.from_documents(documents=document, embedding = embeddings)
    
    # Create bộ retriever 
    retriever = vector_store.as_retriever(search_kwargs = {"k": 1})
    
    template = """ Dựa trên thông tin sau {context}
    
    Trả lời câu hỏi: {question}
    
    "Tôi không tìm thấy thông tin liên quan trong cơ sở tri thức. Hãy cung cấp thông tin cho tôi được không? Cảm ơn bạn!!
    """
    prompt = PromptTemplate.from_template(template)
    
    # Initialize Gemini LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))

    # Create RAG Chain
    rag_chain = (
        {"context": retriever | (lambda docs: "\n".join(doc.page_content for doc in docs)), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain
    
def query_rag(rag_chain, question):
    return rag_chain.invoke(question)

# data_path = "D:\STUDY\DISCORD_BOT\Documents\information_client_basic.docx"
    
if __name__ == "__main__":
    file_path = "D:\STUDY\DISCORD_BOT\Documents\information_client_basic.docx"
    rag_chain = setup_rag(file_path)
    print("Nhập câu hỏi bạn muốn hỏi: ")
    question = input()
    response = query_rag(rag_chain, question)
    print(response)