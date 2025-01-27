import json
import math
import string
import re
import random
import sys
import traceback
import functools
from collections import OrderedDict

import numpy
import sortedcontainers


# Global dictionary to store files and their sizes
files = {}

def FILE_UPLOAD(file_name, size):
    if file_name in files:
        raise RuntimeError("File already exists")
    files[file_name] = size
    return f"uploaded {file_name}"

def FILE_GET(file_name):
    if file_name in files:
        return f"got {file_name}"
    return None

def FILE_COPY(source, dest):
    if source not in files:
        raise RuntimeError("Source file does not exist")
    files[dest] = files[source]
    return f"copied {source} to {dest}"

def simulate_coding_framework(list_of_lists):
    results = []
    for cmd in list_of_lists:
        try:
            if cmd[0] == "FILE_UPLOAD":
                result = FILE_UPLOAD(cmd[1], cmd[2])
                results.append(result)
            elif cmd[0] == "FILE_GET":
                result = FILE_GET(cmd[1])
                results.append(result)
            elif cmd[0] == "FILE_COPY":
                result = FILE_COPY(cmd[1], cmd[2])
                results.append(result)
        except Exception as e:
            results.append(str(e))
    return results
