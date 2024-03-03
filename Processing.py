import os
import base64
import office365
import time
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from requests.exceptions import ConnectionError
from office365.sharepoint.files.file import File
from langchain.vectorstores.qdrant import Qdrant
import qdrant_client
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential



def download_file(context, file_url, download_path):

    with open(download_path, "wb") as local_file:
        response = File.open_binary(context, file_url)
        local_file.write(response.content)
    print(f"File downloaded to: {download_path}")


def download_files_from_list(item, download_path, file_link_dict, ctx, max_retries=3, retry_delay=5):
    
    retry_count = 0

    while retry_count < max_retries:
        
        try:

            if isinstance(item, office365.sharepoint.listitems.listitem.ListItem):
                
                #print(item.properties)

                if item.properties['FileSystemObjectType'] == 0:  # It is a file
                    file = item.file  # Access the file property
                    file_url = file.serverRelativeUrl
                    file_name = file.name  # Extract file name
                    ctx.load(file)  # Make sure to load the file property
                    ctx.execute_query()

                    # download the file into local directory
                    path = os.path.join(download_path, os.path.basename(file_url))
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    download_file(ctx, file_url, path)

                    # Update the file link dictionary
                    file_link = f"https://yourDomain/:b:/r{file_url}" #TODO: replace this with your domain link.
                    file_link_dict[file_name] = file_link

                elif item.properties['FileSystemObjectType'] == 1:  # It is a folder

                    title = item.properties['Title']
                    print(title)
                    if title:
                        path = f"policies/{title}" #TODO: replace this with your path.
                        folder = ctx.web.get_folder_by_server_relative_path(path)
                        ctx.load(folder)
                        try:
                            ctx.execute_query()
                        except:
                            print("Something wrong with this folder!!!!!!!!!!!!!!")
                            print(title)
                            print(item.properties)

                        # Retrieve items from the folder
                        folder_files = folder.files
                        ctx.load(folder_files)
                        ctx.execute_query()

                        for file_item in folder_files:
                            download_files_from_list(file_item, download_path, file_link_dict, ctx)

                        # Retrieve subfolders in the folder
                        folder_folders = folder.folders
                        ctx.load(folder_folders)
                        ctx.execute_query()

                        for folder_item in folder_folders:
                            # Recursively call the function for each file in the folder
                            download_files_from_list(folder_item, download_path, file_link_dict, ctx)
                    else:
                        print("This list item has no title, the properties are: ")
                        print(item.properties)

            elif isinstance(item, office365.sharepoint.folders.folder.Folder):

                print(item.properties)

                folder_url = item.properties["ServerRelativeUrl"]
                folder = ctx.web.get_folder_by_server_relative_path(folder_url)
                ctx.load(folder)
                ctx.execute_query()

                # Retrieve items from the folder
                folder_files = folder.files
                ctx.load(folder_files)
                ctx.execute_query()

                for file_item in folder_files:
                    download_files_from_list(file_item, download_path, file_link_dict, ctx)

                # Retrieve subfolders in the folder
                folder_folders = folder.folders
                ctx.load(folder_folders)
                ctx.execute_query()

                for folder_item in folder_folders:
                    # Recursively call the function for each file in the folder
                    download_files_from_list(folder_item, download_path, file_link_dict, ctx)

            elif isinstance(item, office365.sharepoint.files.file.File):

                file_url = item.serverRelativeUrl
                file_name = item.name  # Extract file name
                ctx.load(item)  # Make sure to load the file property
                ctx.execute_query()

                # download the file into local directory
                path = os.path.join(download_path, os.path.basename(file_url))
                os.makedirs(os.path.dirname(path), exist_ok=True)
                download_file(ctx, file_url, path)

                # Update the file link dictionary
                file_link = f"https://youDomain/:b:/r{file_url}" #TODO: replace this with your domain link.
                file_link_dict[file_name] = file_link

            else:
                print("warning, strange item")
            
            # If download is successful, break out of the loop
            break

        except ConnectionError as e:
            print(f"ConnectionError occurred: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying... Attempt {retry_count}/{max_retries}")
                time.sleep(retry_delay)  # Wait for retry_delay seconds before retrying
            else:
                print(f"Max retries reached. Moving to the next file.")
                # Optionally log this failure for later review
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Handle other types of exceptions if necessary
            break

# Write the Dictionary to Another Python Script
def write_dict_to_file(file_link_dict, filename='file_links.py'):
    
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path for the new file
    file_path = os.path.join(script_directory, filename)

    with open(file_path, 'w') as file:
        file.write('file_links = ' + str(file_link_dict))


def extract_text_from_path(path):
    
    # delete URLs from downloaded files
    # Iterate over all files in the directory
    for filename in os.listdir(path):
        # Construct the full file path
        file_path = os.path.join(path, filename)

        # Check if the file ends with .url and delete it
        if filename.endswith('.url'):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except OSError as e:
                print(f"Error: {file_path} : {e.strerror}")

    loader = DirectoryLoader(path, show_progress=True, use_multithreading=True, sample_size=10000)
    docs = loader.load()
    print("Num of documents processed: ", len(docs))

    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)

    return all_splits


def embed_and_upload(all_splits, script_directory):

    # load OpenAI API key
    load_openai_api_key()

    # create vector store
    embeddings = OpenAIEmbeddings()

    doc_store = Qdrant.from_documents(
        documents=all_splits, 
        embedding=embeddings,
        url=os.getenv("QDRANT_HOST"),
        prefer_grpc=True,
        api_key=os.getenv("QDRANT_API_KEY"),
        collection_name="all-docs-test",
        force_recreate=True,
    )

    '''
    # Store vectors locally
    embedding_storage_path = os.path.join(script_directory, "qdrant_embeddings")
    qdrant = Qdrant.from_documents(
        documents=all_splits,
        embedding=embeddings,
        path=embedding_storage_path,
        collection_name="all-docs-test",
    )
    '''


def create_qdrant_client_and_collection():

    # create a qdrant client
    client = qdrant_client.QdrantClient(
        url=os.getenv("QDRANT_HOST"),
        api_key=os.getenv("QDRANT_API_KEY"),
        timeout=10.0, # need to increase timeout limit to avoid timeout
    )

    # create a collection using the client object
    vectors_config = qdrant_client.http.models.VectorParams(
        size=1536, # size of the vector, should be the same as embedding size, instructor-xl:768, OpenAI: 1536
        distance=qdrant_client.http.models.Distance.COSINE  # distance metrix to use, cosine similarity
    )

    client.recreate_collection(
        collection_name="all-docs-test",
        vectors_config=vectors_config
    )

    return client


def load_openai_api_key():

    base64_string = os.getenv("ENCODED_KEY")
    base64_bytes = base64_string.encode("ascii")
    key_bytes = base64.b64decode(base64_bytes)
    openai_key = key_bytes.decode("ascii")
    os.environ['OPENAI_API_KEY'] = openai_key


def main():

    load_dotenv()

    # SharePoint credentials and site information
    username = os.getenv("SHAREPOINT_USERNAME")
    password = os.getenv("SHAREPOINT_PASSWORD")
    base_path = os.getenv("SHAREPOINT_BASEPATH")

    ctx = ClientContext(base_path).with_credentials(UserCredential(username, password))

    print("--------------CONNECT TO SHAREPOINT SUCCESS----------------")
    

    sp_list = ctx.web.lists.get_by_title("policies") #TODO: replace this with your title.
    list_items = sp_list.items
    ctx.load(list_items)
    ctx.execute_query()

    # Initialize dictionary
    file_link_dict = {}

    # Get the current script directory
    script_directory = os.path.dirname(os.path.realpath(__file__))

    # Name of the new folder under the script directory
    download_folder_name = "DownloadedPolicyFiles"
    download_directory = os.path.join(script_directory, download_folder_name)

    # Create the download directory if it doesn't exist
    os.makedirs(download_directory, exist_ok=True)
    
    # download files
    for item in list_items:
        #print(item.properties["Title"])
        download_files_from_list(item, download_directory, file_link_dict, ctx)

    print("--------------FILE DOWNLOAD SUCCESS----------------")

    # write the file:link dictionary into a Python script
    write_dict_to_file(file_link_dict)

    print("--------------PYTHON FILE:LINKS DICT COLLECTED----------------")

    all_splits = extract_text_from_path(download_directory)
    #chunks = get_text_chunks(raw_text)

    print("--------------TEXT EXTRACTION SUCCESS----------------")

    embed_and_upload(all_splits, script_directory)

    print("--------------EMBEDDING SUCCESS----------------")
    print("--------------CONGRATULATIONS!----------------")



if __name__ == '__main__':
    main()
