import requests
import json
import time
import os
import xml.etree.ElementTree as ET
import utils
from dotenv import load_dotenv

load_dotenv()
CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
KEYWORDS = os.getenv("KEYWORDS")

output_paths = [f"biblio_output/{KEYWORDS}"]
for output_path in output_paths:
    os.makedirs(output_path, exist_ok=True)
keywords = [KEYWORDS]
keywords_mapping = zip(keywords, output_paths)

access_token = utils.get_access_token(CLIENT_KEY, CLIENT_SECRET)
token_time = time.time()

if access_token:
    for keyword, output_path in keywords_mapping:
        with open(os.path.join('search_patents', f"{keyword}_1_2000.json"), "r") as f:
            publication_references = json.load(f)
            for doc in publication_references:
                if time.time() - token_time >= 900:
                    access_token = utils.get_access_token(CLIENT_KEY, CLIENT_SECRET)
                    token_time = time.time()
                    print("Access token regenerado.")

                doc_id = doc['document-id']
                doc_number = doc_id['doc-number']['$']
                doc_kind_code = doc_id['kind']['$']
                doc_country = doc_id['country']['$']
                doc_metadata = f"{doc_country}{doc_number}"
                filename = f"{doc_metadata}.json"
                if not utils.file_exists_in_any_subfolder(filename, output_paths):
                    print(f"Obteniendo biblio para {doc_metadata}")
                    time.sleep(5)
                    while True:
                        try: 
                            response = utils.get_patent_biblio(doc_metadata, access_token)
                            if isinstance(response, str):
                                break
                            elif response:
                                print(f'Response: {response}')
                                biblio_dict = utils.xml_to_dict(response)
                                with open(os.path.join(output_path, filename), "w") as f:
                                    json.dump(biblio_dict, f, indent=4, ensure_ascii=False)
                                print(f"Guardado {output_path}/{filename}")
                                break
                        except Exception as e:
                            if "104" in str(e):
                                print("Error 104 detectado, esperando 120 segundos antes de reintentar...")
                                time.sleep(300)
                            else:
                                raise e
                else:
                    print(f"{output_path}/{filename} ya existe, omitiendo")
