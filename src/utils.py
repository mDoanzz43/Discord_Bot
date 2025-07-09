### This file to load and chunk documents to support for embedding data ###

from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def load_document(file_path):
    loader = UnstructuredWordDocumentLoader(file_path)
    documents = loader.load() # Create loader to load data
    
    # split to chunks 
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
    return text_splitter.split_documents(documents)


# file_path = "D:\STUDY\DISCORD_BOT\Documents\information_client_basic.docx"    
# if not os.path.exists(file_path):
#     print("File hasn't exist")
# else: 
#     print(load_document(file_path))
