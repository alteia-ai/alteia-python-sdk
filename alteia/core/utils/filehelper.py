"""
Helper class containing functions that assist in working with files.
"""
import os

from urllib3.response import HTTPResponse

BLOCK_SIZE = 4096


def write_stream_as_file(file_path, response: HTTPResponse):
    """
    serialize the object to a file. The response comes from the Connection response allowing streaming response
    """
    with open(file_path, 'wb') as f:
        for chunk in response.stream(BLOCK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def get_base_name_without_extension(file_path):
    if file_path == '' or file_path is None:
        return ''

    split = os.path.splitext(os.path.basename(file_path))
    if len(split) == 0:
        return ''

    return split[0]


def get_file_extension(filename):
    split_fn = os.path.splitext(filename)

    if len(split_fn[1]) <= 1:
        raise Exception('Invalid Local File extension ' + filename)

    return split_fn[1][1:].lower()


def read_file(file_path, encoding='utf-8'):
    file_handler = open(
            file=os.path.abspath(os.path.expanduser(file_path)),
            mode='r',
            encoding=encoding)

    content = file_handler.read()
    file_handler.close()
    return content
