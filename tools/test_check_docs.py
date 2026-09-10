import tempfile
import unittest
from pathlib import Path

from check_docs import check, parse_document, rebuild_toc


class DocumentationChecks(unittest.TestCase):
    def test_fenced_heading_not_a_heading(self):
        doc = parse_document('# A\n```python\n# not a heading\n```\n')
        self.assertEqual([h['title'] for h in doc[2]], ['A'])
        self.assertEqual(doc[4], [])

    def test_unclosed_fence(self):
        self.assertEqual(parse_document('# A\n```java\nclass A {}\n')[4][0]['kind'],
                         'unclosed_fence')
        self.assertEqual(parse_document('```')[4][0]['kind'], 'unclosed_fence')

    def test_tilde_and_long_fences(self):
        self.assertEqual(parse_document('~~~~java\n```\n~~~~\n')[4], [])

    def test_fence_language_required(self):
        issues = parse_document('```\nplain text\n```\n')[4]
        self.assertEqual(issues, [{'kind': 'missing_fence_language', 'line': 1}])
        self.assertEqual(parse_document('```text\nplain text\n```\n')[4], [])

    def test_duplicate_heading_collision(self):
        anchors = [h['anchor'] for h in parse_document('## A\n## A\n## A-1\n## A\n')[2]]
        self.assertEqual(anchors, ['a', 'a-1', 'a-1-1', 'a-2'])

    def test_explicit_anchor(self):
        self.assertIn('manual', parse_document('<a id="manual"></a>\n')[3])

    def test_rebuild_preserves_body_and_idempotent(self):
        body = '## 1. 新标题\n\n正文\n```java\n# not heading\n```\n### 子项\n内容\n'
        text = '# 文档\n\n## 目录\n- [旧标题](#missing)\n\n' + body
        updated = rebuild_toc(text)
        self.assertTrue(updated.endswith(body))
        self.assertNotIn('#missing', updated)
        self.assertEqual(updated, rebuild_toc(updated))

    def test_removed_toc_heading_does_not_consume_slug(self):
        text = '# Title\n## 目录\n### 第一篇\n[old](#bad)\n## 第一篇\n正文\n'
        updated = rebuild_toc(text)
        self.assertIn('[第一篇](#第一篇)', updated)
        self.assertNotIn('#第一篇-1', updated)
        self.assertEqual(rebuild_toc(updated), updated)

    def test_no_toc_no_write(self):
        self.assertEqual(rebuild_toc('# A\n## B\nbody\n'), '# A\n## B\nbody\n')

    def test_cross_file_and_fragment_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'a.md').write_text('[ok](b.md#标题)\n[bad](b.md#nope)\n'
                                     '![image](missing.png)\n', encoding='utf-8')
            (root / 'b.md').write_text('## 标题\n', encoding='utf-8')
            report = check(root)
            self.assertEqual(sorted(i['kind'] for i in report['issues']),
                             ['missing_anchor', 'missing_file'])

    def test_build_excluded_and_rendered_ids(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as output:
            root = Path(folder)
            (root / 'build').mkdir()
            (root / 'build' / 'bad.md').write_text('[x](missing.md)', encoding='utf-8')
            (root / 'a.md').write_text('## 标题\n', encoding='utf-8')
            report = check(root, render_dir=Path(output))
            self.assertEqual(report['documents'], 1)
            self.assertEqual(report['issues'], [])
            self.assertIn('id="标题"', (Path(output) / 'a.md.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
