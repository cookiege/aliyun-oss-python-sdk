# -*- coding: utf-8 -*-

import random
import string
import oss2

DT_BYTES = 0
DT_FILE = 1
CHUNK_SIZE = 8192


def random_string(n):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(n))


def random_bytes(n):
    return oss2.to_bytes(random_string(n))


def bucket():
    return oss2.Bucket(oss2.Auth('fake-access-key-id', 'fake-access-key-secret'),
                                  'http://oss-cn-hangzhou.aliyuncs.com', 'my-bucket')


class RequestInfo(object):
    def __init__(self):
        self.data = None
        self.resp = None
        self.size = None


MTIME_STRING = 'Fri, 11 Dec 2015 13:01:41 GMT'
MTIME = 1449838901


def merge_headers(dst, src):
    if not src:
        return

    for k, v in src.items():
        dst[k] = v


def r4delete(in_status=204, in_headers=None):
    headers = oss2.CaseInsensitiveDict({
        'Server': 'AliyunOSS',
        'Date': 'Fri, 11 Dec 2015 11:40:31 GMT',
        'Content-Length': '0',
        'Connection': 'keep-alive',
        'x-oss-request-id': '566AB62EB06147681C283D73'
    })

    merge_headers(headers, in_headers)
    return MockResponse(in_status, headers, b'')


def r4head(length, in_status=200, in_headers=None):
    headers = oss2.CaseInsensitiveDict({
        'Server': 'AliyunOSS',
        'Date': 'Fri, 11 Dec 2015 11:40:31 GMT',
        'Content-Type': 'application/javascript',
        'Content-Length': str(length),
        'Connection': 'keep-alive',
        'Vary': 'Accept-Encoding',
        'x-oss-request-id': '566AB62EB06147681C283D73',
        'Accept-Ranges': 'bytes',
        'ETag': '"E5831D5EBC7AAF5D6C0D20259FE141D2"',
        'Last-Modified': MTIME_STRING,
        'x-oss-object-type': 'Normal'
    })

    merge_headers(headers, in_headers)

    return MockResponse(in_status, headers, b'')


def r4get(body, in_status=200, in_headers=None):
    resp = r4head(len(body), in_status=in_status, in_headers=in_headers)
    resp.body = body

    return resp


def r4put(in_status=200, in_headers=None):
    headers = oss2.CaseInsensitiveDict({
        'Server': 'AliyunOSS',
        'Date': 'Fri, 11 Dec 2015 11:40:30 GMT',
        'Content-Length': '0',
        'Connection': 'keep-alive',
        'x-oss-request-id': '566AB62E9C30F8552526DADF'
    })

    merge_headers(headers, in_headers)

    return MockResponse(in_status, headers, b'')


def do4put(req, timeout, in_headers=None, req_info=None, data_type=None):
    resp = r4put(in_headers=in_headers)

    if req_info:
        req_info.req = req
        req_info.resp = resp
        req_info.size = get_length(req.data)
        req_info.data = read_data(req.data, data_type)

    return resp


def read_file(fileobj):
    result = b''

    while True:
        content = fileobj.read(CHUNK_SIZE)
        if content:
            result += content
        else:
            return result


def read_data(data, data_type):
    if data_type == DT_BYTES:
        return data
    elif data_type == DT_FILE:
        return read_file(data)
    else:
        raise RuntimeError('wrong data type: {0}'.format(data_type))


def get_length(data):
    try:
        return len(data)
    except TypeError:
        return None


class MockResponse(object):
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = oss2.CaseInsensitiveDict(headers)
        self.body = oss2.to_bytes(body)

        self.offset = 0

    def read(self, amt=None):
        if self.offset >= len(self.body):
            return ''

        if amt is None:
            end = len(self.body)
        else:
            end = min(len(self.body), self.offset + amt)

        content = self.body[self.offset:end]
        self.offset = end
        return content

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        return self.read(8192)
