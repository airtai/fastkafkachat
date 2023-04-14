# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/Helper.ipynb.

# %% auto 0
__all__ = ['get_all_links_from_website', 'get_service_context', 'write_compressed_json', 'load_compressed_json']

# %% ../nbs/Helper.ipynb 1
from pathlib import Path
from typing import *
import gzip
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from llama_index import (
    GPTSimpleVectorIndex,
    SimpleDirectoryReader,
    LLMPredictor,
    ServiceContext,
)

# %% ../nbs/Helper.ipynb 3
def get_all_links_from_website(start_url: str, visited: Optional[set] = None) -> Set[str]:
    """Get a set of all links (URLs) found on the given website, starting from the given start URL.
    
    Args:
        start_url: The starting URL of the website.
        visited: Optional. A set of URLs that have already been visited. Defaults to an empty set.

    Returns:
        A set of all links found on the website.
    """
    if visited is None:
        visited = set()

    req = Request(start_url)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")
    
    base_url = urlparse(start_url).scheme + '://' + urlparse(start_url).hostname #type: ignore
    
    links = set()
    for link in soup.find_all('a', href=True):
        url = urljoin(base_url, link['href']).split("#")[0].strip("/")
        if urlparse(url).hostname == urlparse(start_url).hostname:
            links.add(url)
            
    visited.add(start_url)
    for link in links:
        if link not in visited:
            visited |= get_all_links_from_website(link, visited)
    
    return visited

# %% ../nbs/Helper.ipynb 5
def get_service_context() -> ServiceContext:
    """Return a service context object initialized with an LLM predictor based on the gpt-3.5-turbo model
    
    Returns:
        A ServiceContext object with an LLMPredictor and a chunk size limit.
    """
    llm_predictor = LLMPredictor(
        llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    )
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, chunk_size_limit=512
    )
    
    return service_context

# %% ../nbs/Helper.ipynb 7
def write_compressed_json(json_string: str, file_path: str) -> None:
    """Compresses a JSON string and writes it to disk at the specified file path with a .gz extension.
    
    Args:
        json_string: The JSON string to compress and write to disk.
        file_path: The path to write the compressed JSON file to, without the .gz extension.
    """
    with gzip.open(file_path + '.gz', 'wb') as f_out:
        json_bytes = json_string.encode('utf-8')
        f_out.write(json_bytes)
        
        
def load_compressed_json(gziped_json_file_path: str) -> str:
    """Load a compressed JSON file from disk and returns its contents as a string.
    
    Args:
        gziped_json_file_path: The path to the compressed JSON file to read.
    """
    with gzip.open(gziped_json_file_path, 'rb') as f:
        json_bytes = f.read()
        json_str = json_bytes.decode('utf-8')
        return json_str