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

from ..utils import logger
from ..base import (
    BaseKVStorage,
    BaseVectorStorage,
    DocStatusStorage,
    DocStatus,
    DocProcessingStatus,
    BaseGraphStorage,
)

if sys.platform.startswith("win"):
    import asyncio.windows_events

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
