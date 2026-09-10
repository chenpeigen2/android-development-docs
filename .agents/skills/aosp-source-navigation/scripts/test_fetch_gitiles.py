import base64
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import fetch_gitiles as tool


class Response(io.BytesIO):
    status = 200


class GitilesTests(unittest.TestCase):
    def test_project_path_and_ref_are_not_duplicated(self):
        url = tool.build_url('platform/frameworks/base', 'refs/tags/android-17.0.0_r1',
                             'core/java/android/view/Window.java', 'text')
        self.assertEqual(url, 'https://android.googlesource.com/platform/frameworks/base/'
                         '+/refs/tags/android-17.0.0_r1/core/java/android/view/Window.java?format=TEXT')

    def test_mutable_refs_rejected(self):
        for ref in ['main', 'refs/heads/main', 'android-latest-release', 'abc1234']:
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                tool.build_url('platform/art', ref, 'runtime', 'tree')
        self.assertIn('/' + 'a' * 40 + '/', tool.build_url('platform/art', 'a' * 40, '', 'tree'))

    def test_invalid_paths_rejected(self):
        for path in ['../a', '/a', 'a//b', 'a?format=TEXT', 'a#10', 'a\nb', 'C:/a']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                tool.build_url('platform/art', 'refs/tags/test', path, 'text')

    def test_text_preserves_utf8_and_lines(self):
        text = '// 中文\nclass A {}\n'.encode('utf-8')
        content, tree = tool.decode_payload(base64.b64encode(text), 'text')
        self.assertEqual(content, text)
        self.assertIsNone(tree)

    def test_tree_strips_xssi_and_retains_git_id(self):
        raw = b")]}'\n" + json.dumps({'id': 'abc', 'entries': [{'name': 'A.java'}]}).encode()
        content, tree = tool.decode_payload(raw, 'tree')
        self.assertEqual(tree, 'abc')
        self.assertEqual(json.loads(content)['entries'][0]['name'], 'A.java')

    def test_empty_or_error_page_is_not_evidence(self):
        for raw, kind in [(b'', 'text'), (b'<html>error</html>', 'text'), (b'{}', 'tree')]:
            with self.subTest(kind=kind, raw=raw), self.assertRaises(ValueError):
                tool.decode_payload(raw, kind)

    def test_fetch_writes_verifiable_provenance(self):
        source = b'class A {}\n'
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(tool, 'urlopen', return_value=Response(base64.b64encode(source))):
                result = tool.fetch('platform/art', 'refs/tags/test', 'A.java', 'text', Path(folder))
            self.assertEqual(Path(result['body']).read_bytes(), source)
            self.assertEqual(result['sha256'], hashlib.sha256(source).hexdigest())
            self.assertEqual(json.loads(Path(result['metadata']).read_text('utf-8')), result)
            self.assertEqual(result['http_status'], 200)

    def test_refs_have_distinct_cache_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            results = []
            for ref in ['refs/tags/one', 'refs/tags/two']:
                with patch.object(tool, 'urlopen', return_value=Response(base64.b64encode(b'hello'))):
                    results.append(tool.fetch('platform/art', ref, 'A.java', 'text', Path(folder)))
            self.assertNotEqual(results[0]['body'], results[1]['body'])

    def test_http_failure_does_not_create_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder) / 'cache'
            error = HTTPError('https://android.googlesource.com/not-found', 404, 'Not Found', {}, None)
            with patch.object(tool, 'urlopen', side_effect=error), self.assertRaises(HTTPError):
                tool.fetch('platform/art', 'refs/tags/test', 'A.java', 'text', dest)
            self.assertFalse(dest.exists())

    def test_response_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(tool, 'MAX_BYTES', 3), patch.object(tool, 'urlopen', return_value=Response(b'1234')):
                with self.assertRaisesRegex(ValueError, 'exceeds'):
                    tool.fetch('platform/art', 'refs/tags/test', 'A.java', 'text', Path(folder))


if __name__ == '__main__':
    unittest.main()
