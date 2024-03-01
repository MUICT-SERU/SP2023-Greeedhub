from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import json
import re

from tests.functional.sqlalchemy import BaseTestCase


class TestBreakdown(BaseTestCase):
    def setUp(self):
        super(TestBreakdown, self).setUp()

        ar_fixtures = self.ar_fu.fixup(data=[{}, {}, {
            'title': 'some title',
            'is_visible': True,
        }])

        au_fixtures = self.au_fu.fixup(data=[
            {
                'articles': ar_fixtures[:2],
            },
            {
                'articles': ar_fixtures[-1:],
            }
        ])

    def _standardize_white_space(self, s):
        return re.sub(re.compile('^[ ]+', re.MULTILINE), '', s.strip())

    def test_get_current_fixtures_json(self):
        json_dict = json.loads(self.m_fu.get_current_json_breakdown())
        self.assertEqual(json_dict, self.json_dict)

    def test_get_fixtures_json_in_different_order(self):
        self.SqlAlchemyModelFixtureUpper.all_fixtures_order = ['Author', 'Article']
        json_dict = json.loads(self.m_fu.get_current_json_breakdown())
        expected_json_dict = self.json_dict[3:] + self.json_dict[:3]
        self.assertEqual(json_dict, expected_json_dict)

    def test_writes_as_sql(self):
        query = self.m_fu.breakdown_to_sql(self.m_fu.get_all_fixtures())
        self.assertEqual(
            self._standardize_white_space(query),
            self._standardize_white_space("""
                INSERT INTO article (id, is_visible, main_author_id, title) VALUES
                (250, NULL, 150, NULL),
                (251, NULL, 150, NULL),
                (252, true, 151, 'some title');

                INSERT INTO author (id) VALUES
                (150),
                (151);
            """)
        )

    def test_writes_as_sql_in_different_order(self):
        self.SqlAlchemyModelFixtureUpper.all_fixtures_order = ['Author', 'Article']
        query = self.m_fu.breakdown_to_sql(self.m_fu.get_all_fixtures())
        self.assertEqual(
            self._standardize_white_space(query),
            self._standardize_white_space("""
                INSERT INTO author (id) VALUES
                (150),
                (151);

                INSERT INTO article (id, is_visible, main_author_id, title) VALUES
                (250, NULL, 150, NULL),
                (251, NULL, 150, NULL),
                (252, true, 151, 'some title');
            """)
        )
