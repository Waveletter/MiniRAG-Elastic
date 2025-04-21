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


