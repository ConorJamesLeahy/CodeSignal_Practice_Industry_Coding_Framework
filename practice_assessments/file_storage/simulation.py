import json
import math
import string
import re
import random
import sys
import traceback
import functools
from collections import OrderedDict
from datetime import datetime, timedelta

import numpy
import sortedcontainers

files = {}
operations_history = []

def simulate_coding_framework(list_of_lists):
    """
    Simulates a coding framework operation on a list of lists of strings.

    Parameters:
    list_of_lists (List[List[str]]): A list of lists containing strings.
    """
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
            elif cmd[0] == "FILE_SEARCH":
                result = FILE_SEARCH(cmd[1])
                results.append(result)
            elif cmd[0] == "FILE_UPLOAD_AT":
                ttl = cmd[4] if len(cmd) > 4 else None
                result = FILE_UPLOAD_AT(cmd[1], cmd[2], cmd[3], ttl)
                results.append(result)
            elif cmd[0] == "FILE_GET_AT":
                result = FILE_GET_AT(cmd[1], cmd[2])
                results.append(result)
            elif cmd[0] == "FILE_COPY_AT":
                result = FILE_COPY_AT(cmd[1], cmd[2], cmd[3])
                results.append(result)
            elif cmd[0] == "FILE_SEARCH_AT":
                result = FILE_SEARCH_AT(cmd[1], cmd[2])
                results.append(result)
            elif cmd[0] == "ROLLBACK":
                result = ROLLBACK(cmd[1])
                results.append(result)
        except Exception as e:
            results.append(str(e))
        
    return results


def FILE_UPLOAD(file_name, file_size):
    """
    Uploads a file with a given name and size.

    Parameters:
    file_name (str): The name of the file.
    file_size (str): The size of the file.
    """
    if file_name in files:
        raise RuntimeError("File already exists")
    files[file_name] = file_size
    return f"uploaded {file_name}"
    
def FILE_GET(file_name):
    """
    Gets a file with a given name.

    Parameters:
    file_name (str): The name of the file.
    """
    if file_name not in files:
        return None
    #return files[file_name]
    return f"got {file_name}"

def FILE_COPY(source, dest):
    """
    Copies a file from a source to a destination.

    Parameters:
    source (str): The name of the source file.
    dest (str): The name of the destination file.
    """
    if source not in files:
        raise RuntimeError("Source does not exist")
    files[dest] = files[source]
    return f"copied {source} to {dest}"

def FILE_SEARCH(prefix):
    """
    Find the top 10 files starting with the provided prefix. 

    Parameters:
    prefix (str): The prefix to search for.
    """
    found_files = []
    for file_name in files:
        if file_name.startswith(prefix):
            found_files.append(file_name)
    
    found_files.sort(key = lambda x: (len(x),x), reverse = True)
    found_files = found_files[:10]
    return f"found [{', '.join(found_files)}]"


def FILE_UPLOAD_AT(timestamp, file_name, file_size, ttl = 'None'):
    """
    Uploads a file with a given name and size.

    Parameters:
    timestamp (str): The timestamp of the file upload.
    file_name (str): The name of the file.
    file_size (str): The size of the file.
    tttl (int): The time-to-live of the file.
    """
    operations_history.append({
        'type': 'upload',
        'timestamp': timestamp,
        'file_name': file_name,
        'size': file_size,
        'ttl': ttl
    })
    if file_name in files:
        raise RuntimeError("File already exists")
    files[file_name] = {
        'size': file_size,
        'timestamp': timestamp,
        'ttl': ttl
    }
    return f"uploaded at {file_name}"


def FILE_GET_AT(timestamp, file_name):
    """
    Gets a file with a given name.

    Parameters:
    timestamp (str): The timestamp of the file get.
    file_name (str): The name of the file.
    """
    if file_name not in files:
        return "file not found"
    file = files[file_name]
    if file['ttl']:
        expiry = datetime.strptime(file['timestamp'], "%Y-%m-%dT%H:%M:%S") + timedelta(seconds=file['ttl'])
        if datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") > expiry:
            return "file not found"
    return f"got at {file_name}"
    
    

def FILE_COPY_AT(timestamp, source, dest):
    """
    Copies a file from a source to a destination.

    Parameters:
    timestamp (str): The timestamp of the file copy.
    source (str): The name of the source file.
    dest (str): The name of the destination file.
    """
    operations_history.append({
        'type': 'copy',
        'timestamp': timestamp,
        'source': source,
        'dest': dest
    })
    
    if source not in files:
        raise RuntimeError("Source does not exist")
    file = files[source]
    if file['ttl']:
        expiry = datetime.strptime(file['timestamp'], "%Y-%m-%dT%H:%M:%S") + timedelta(seconds=file['ttl'])
        if datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S") > expiry:
            raise RuntimeError("Source does not exist")
    files[dest] = file.copy()
    files[dest]['timestamp'] = timestamp
    return f"copied at {source} to {dest}"
    
    
def FILE_SEARCH_AT(timestamp, prefix):
    """
    Find the top 10 files starting with the provided prefix. 

    Parameters:
    timestamp (str): The timestamp of the file search.
    prefix (str): The prefix to search for.
    """
    found_files = []
    current = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    
    for file_name, file_data in files.items():
        if not file_name.startswith(prefix):
            continue
            
        file_time = datetime.strptime(file_data['timestamp'], "%Y-%m-%dT%H:%M:%S")
        if file_time > current:
            continue
            
        if file_data['ttl'] is not None:
            expiry = file_time + timedelta(seconds=file_data['ttl'])
            if current > expiry:
                continue
        found_files.append(file_name)
    
    found_files.sort(key=lambda x: (-len(files[x]['size']), x))
    found_files = found_files[:10]
    return f"found at [{', '.join(found_files)}]"

def ROLLBACK(timestamp):
    target_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    
    # Keep only operations up to target time
    valid_ops = [op for op in operations_history if datetime.strptime(op['timestamp'], "%Y-%m-%dT%H:%M:%S") <= target_time]
    operations_history.clear()
    operations_history.extend(valid_ops)
    
    # Rebuild files state
    files.clear()
    for op in valid_ops:
        if op['type'] == 'upload':
            files[op['file_name']] = {
                'size': op['size'],
                'timestamp': op['timestamp'],
                'ttl': op['ttl']
            }
        elif op['type'] == 'copy':
            if op['source'] in files:
                files[op['dest']] = files[op['source']].copy()
                files[op['dest']]['timestamp'] = op['timestamp']
    
    return f"rollback to {timestamp}"

#x = simulate_coding_framework([["FILE_UPLOAD", "Cars.txt", "200kb"], ["FILE_GET", "Cars.txt"], ["FILE_COPY", "Cars.txt", "Cars2.txt"], ["FILE_GET", "Cars2.txt"]])
#print(x) 

#x = simulate_coding_framework([["FILE_UPLOAD", "Foo.txt", "100kb"], 
#                            ["FILE_UPLOAD", "Bar.csv", "200kb"], 
#                            ["FILE_UPLOAD", "Baz.pdf", "300kb"],
#                            ["FILE_SEARCH", "Ba"]])
#print(x)