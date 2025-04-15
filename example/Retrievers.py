import json
import os
import uuid
from pathlib import Path
from typing import Iterable, Literal

# import textract
from elasticsearch.helpers import bulk
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.retrievers import ElasticSearchBM25Retriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_text_splitters import CharacterTextSplitter
from tqdm.auto import tqdm


class CustomElasticSearchBM25Retriever(ElasticSearchBM25Retriever):
    
    @classmethod
    def create(
        cls, elasticsearch_url: str, index_name: str, login: str, password: str, max_num_retrieved_docs: int = 10, k1: float = 2.0, b: float = 0.75
    ) -> ElasticSearchBM25Retriever:
        """
        Create a ElasticSearchBM25Retriever from a list of texts.

        Args:
            elasticsearch_url: URL of the Elasticsearch instance to connect to.
            index_name: Name of the index to use in Elasticsearch.
            k1: BM25 parameter k1.
            b: BM25 parameter b.

        Returns:

        """
        from elasticsearch import Elasticsearch

        # Create an Elasticsearch client instance
        es = Elasticsearch(
            elasticsearch_url, 
            verify_certs=False,
            ssl_show_warn=False, 
            basic_auth=(login, password),
        )  

        cls.max_num_retrieved_docs = max_num_retrieved_docs
        
        return cls(client=es, index_name=index_name)
    
    def add_documents(
        self,
        documents: Iterable[Document],
        refresh_indices: bool = True,
    ) -> list[str]:
        requests = []
        ids = []
        for doc in documents:
            _id = str(uuid.uuid4())
            
            request = {
                "_op_type": "index",
                "_index": self.index_name,
                "_id": _id,
                "content": doc.page_content,
                "metadata": doc.metadata if doc.metadata else {},
            }
            ids.append(_id)
            requests.append(request)
        
        bulk(self.client, requests)

        if refresh_indices:
            self.client.indices.refresh(index=self.index_name)
        
        return ids
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        query_dict = {"query": {"match": {"content": query}}}
        res = self.client.search(index=self.index_name, body=query_dict, size=self.max_num_retrieved_docs)

        docs = []
        for r in res["hits"]["hits"]:
            docs.append(Document(page_content=r["_source"]["content"], metadata=r["_source"]["metadata"]))
        return docs
    
    


def parse_files(file_paths: Iterable[str | os.PathLike]) -> list[Document]:
    documents = []
    for file_path in tqdm(file_paths, desc="Parsing files"):
        file_format = Path(file_path).suffix.lower()
        match file_format:
            case '.pdf':
                documents.extend(get_documents_from_pdf(file_path))
            case '.json':
                documents.extend(get_documents_from_json(file_path))
            case '.doc':
                documents.extend(get_documents_from_doc(file_path))  
            case _:
                raise ValueError(f"Неподдерживаемый тип файла: {file_path} ({file_format})")
    return documents


def get_retriever(retriever_type: Literal['bm25'] | None) -> BaseRetriever | None:
    match retriever_type:
        case 'bm25':
            retriever = CustomElasticSearchBM25Retriever
        case None:
            return None
        case _:
            raise ValueError(f"Неизвестный тип retriever: {retriever_type}")
        
    return retriever


def get_documents_from_json(path_to_data: str | os.PathLike) -> list[Document]:
    with open(path_to_data, 'r') as f:
        data = json.load(f)
    
    documents = [Document(
        id=str(record['id']), #FIXME: all ids is None after invoking
        page_content=record['title'] + '\n' + record['text'] if record['title'] else record['text'],
        metadata={
            'references': record['references'],
            'updated': record['updated'],
            'url': record['url'],
        }
    # ) for record in tqdm(data, desc=f"Загрузка данных из {path_to_data}")]
    ) for record in data]
    
    return documents


def get_documents_from_pdf(path_to_data: str | os.PathLike) -> list[Document]:
    try:
        loader = PyPDFLoader(path_to_data)
        docs = loader.load()
    except Exception as e:
        raise ValueError(f"Error loading PDF file {path_to_data}:\n{e}")
    
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=200)
    docs_split = text_splitter.split_documents(docs)
    
    return docs_split


def get_documents_from_doc(path_to_data: str | os.PathLike) -> list[Document]:
    raise NotImplementedError
    # try:
    #     text = textract.process(path_to_data).decode('utf-8')
    # except Exception as e:
    #     raise ValueError(f"Error loading DOC file {path_to_data}:\n{e}")

    # doc = Document(page_content=text, metadata={"source": path_to_data})

    # text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=200)
    # docs_split = text_splitter.split_documents([doc])

    # return docs_split
