import sys
import pytest
from collections import Counter
from io import BytesIO

import warcio.utils as utils
from . import get_test_file

try:
    from multidict import CIMultiDict, MultiDict
except ImportError:
    pass


class TestUtils(object):
    def test_headers_to_str_headers(self):
        result = [('foo', 'bar'), ('baz', 'barf')]

        header_dict = {'foo': b'bar', b'baz': 'barf'}
        ret = utils.headers_to_str_headers(header_dict)
        assert Counter(ret) == Counter(result)

        aiohttp_raw_headers = ((b'foo', b'bar'), (b'baz', b'barf'))
        assert Counter(utils.headers_to_str_headers(aiohttp_raw_headers)) == Counter(result)

    @pytest.mark.skipif('multidict' not in sys.modules, reason='requires multidict be installed')
    def test_multidict_headers_to_str_headers(self):
        result = [('foo', 'bar'), ('baz', 'barf')]

        aiohttp_headers = MultiDict(foo='bar', baz=b'barf')
        ret = utils.headers_to_str_headers(aiohttp_headers)
        assert Counter(ret) == Counter(result)

        # This case-insensitive thingie titlecases the key
        aiohttp_headers = CIMultiDict(Foo='bar', Baz=b'barf')
        titlecase_result = [('Foo', 'bar'), ('Baz', 'barf')]

        ret = utils.headers_to_str_headers(aiohttp_headers)
        assert Counter(ret) == Counter(titlecase_result)

    def test_open_or_default(self):
        default_fh = BytesIO(b'NOTWARC/1.0\r\n')

        with utils.open_or_default(get_test_file('example.warc'), 'rb', default_fh) as fh:
            assert fh.readline().decode('utf-8') == 'WARC/1.0\r\n'

        with utils.open_or_default(None, 'rb', default_fh) as fh:
            assert fh.readline().decode('utf-8') == 'NOTWARC/1.0\r\n'

        default_fh.seek(0)
        with utils.open_or_default(default_fh, 'rb', None) as fh:
            assert fh.readline().decode('utf-8') == 'NOTWARC/1.0\r\n'

