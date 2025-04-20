import asyncio
import inspect
import json
import os
import time
from dataclasses import dataclass
from typing import Union, List, Dict, Set, Any, Tuple


import numpy as np

import sys
from tqdm.asyncio import tqdm as tqdm_async
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from minirag.utils import logger
from minirag.base import (
    BaseKVStorage,
    BaseVectorStorage,
    DocStatusStorage,
    DocStatus,
    DocProcessingStatus,
    BaseGraphStorage,
)


import pipmaster as pm

if not pm.is_installed("elasticsearch[async]"):
    pm.install("elasticsearch[async]==8.12.0") # NEEDS to be identical to the database ver; currently 8.12.0

import elasticsearch

if sys.platform.startswith("win"):
    import asyncio.windows_events

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@dataclass
class ESKVStorage(BaseKVStorage):
    pass


@dataclass
class ESVectorStorage(BaseVectorStorage):
    pass


@dataclass
class ESDocStatusStorage(DocStatusStorage):
    pass


class ESGraphQueryException(Exception):
    pass


@dataclass
class ESGraphStorage(BaseGraphStorage):
    pass


from info import ES_Info
import logging
import requests

def main():

    logging.basicConfig(level=logging.DEBUG)

    print(ES_Info.host.value, ES_Info.credentials.value, ES_Info.api_key.value)
    es = elasticsearch.Elasticsearch(
        ES_Info.host.value,
        verify_certs=False,
        ssl_show_warn=False,
        api_key=ES_Info.api_key.value
    )

    if es.ping():
        print("Connection successful")
    else:
        print("No connection")

    print(es.info())

    url = f"{ES_Info.host.value}/test_index"
    headers = {
        "Authorization": f"ApiKey {ES_Info.api_key.value}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    print(response.status_code, response.text)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)
