# -*- coding: utf-8 -*-

import unittest
import json

from zope.component import getMultiAdapter

from rt.bulkmodify.testing import BULK_MODIFY_INTEGRATION_TESTING

from .base import BaseTestCase
from .base import re_pattern
from .base import re_subn_pattern

class TestViewBatchSearch(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING
    
    def setUp(self):
        BaseTestCase.setUp(self)
        self.view = getMultiAdapter((self.layer['portal'],
                                     self.layer['request']),
                                     name=u"batchSearch")

    def test_missing_parameters(self):
        portal = self.layer['portal']
        request = self.layer['request']
        view = self.view
        # no params
        self.assertEqual(json.loads(view()), [])
        # only content_type
        view.request.set('content_type', ['foo'])
        self.assertEqual(json.loads(view()), [])
        # only query
        view.request.set('content_type', [])
        view.request.set('searchQuery', 'foo')
        # both
        self.assertEqual(json.loads(view()), [])
        view.request.set('content_type', ['foo'])
        view.request.set('searchQuery', 'foo')
        self.assertNotEqual(json.loads(view()), [])
        # an existing type, but query
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', '')
        self.assertEqual(json.loads(view()), [])

    def test_simple_search(self):
        portal = self.layer['portal']
        request = self.layer['request']
        view = self.view
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', re_pattern)
        results = json.loads(view())
        
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]['title'], 'Page 1')
        self.assertEqual(results[0]['text'],
                         u'... dolor <span class="mark">&lt;a target="_blank" href="http://loripsum.net/"&gt;sit amet, consectetur adipisicing elit&lt;/a&gt;</span>, sed d...')
        self.assertEqual(results[2]['title'], 'Page 2')
        self.assertEqual(results[2]['text'],
                         u'...ongue. <span class="mark">&lt;a target="_blank" href="http://loripsum.net/"&gt;Duis ac augue diam&lt;/a&gt;</span>, digni...')

    def test_batching(self):
        portal = self.layer['portal']
        request = self.layer['request']
        view = self.view
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', re_pattern)
        view.request.set('b_size', 1)
        self.assertEqual(len(json.loads(view())), 2)
        view.request.set('b_start', 1)
        self.assertEqual(len(json.loads(view())), 2)
        view.request.set('b_start', 2)
        self.assertEqual(json.loads(view()), None)


class TestViewBatchReplace(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING
    
    def setUp(self):
        BaseTestCase.setUp(self)
        self.view = getMultiAdapter((self.layer['portal'],
                                     self.layer['request']),
                                     name=u"batchReplace")

    def test_missing_parameters(self):
        portal = self.layer['portal']
        request = self.layer['request']
        view = self.view
        # no params
        self.assertEqual(json.loads(view()), [])
        view.request.set('content_type', ['foo'])
        # only content_type
        self.assertEqual(json.loads(view()), [])
        # only query
        view.request.set('content_type', [])
        view.request.set('searchQuery', 'foo')
        self.assertEqual(json.loads(view()), [])
        # only replace query
        view.request.set('searchQuery', '')
        view.request.set('replaceQuery', '')
        self.assertEqual(json.loads(view()), [])
        # all three paarameters
        view.request.set('content_type', ['foo'])
        view.request.set('searchQuery', 'foo')
        view.request.set('replaceQuery', 'foo')
        self.assertNotEqual(json.loads(view()), 'foo')
        # an existing type, but no queries
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', '')
        view.request.set('replaceQuery', '')

    def test_simple_replace(self):
        portal = self.layer['portal']
        request = self.layer['request']
        view = self.view
        view.request.set('content_type', ['Document', ])
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', re_subn_pattern)
        results = json.loads(view())

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0]['title'], 'Page 1')
        self.assertEqual(results[0]['old'],
                         u'<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>')
        self.assertEqual(results[0]['new'],
                         u'<a href="http://loripsum.net/" class="external-link">sit amet, consectetur adipisicing elit</a>')
        self.assertEqual(results[2]['title'], 'Page 2')
        self.assertEqual(results[2]['old'],
                         u'<a target="_blank" href="http://loripsum.net/">Duis ac augue diam</a>')
        self.assertEqual(results[2]['new'],
                         u'<a href="http://loripsum.net/" class="external-link">Duis ac augue diam</a>')


class TestViewReplaceText(BaseTestCase):

    layer = BULK_MODIFY_INTEGRATION_TESTING
    
    def setUp(self):
        BaseTestCase.setUp(self)
        portal = self.layer['portal']
        self.view = getMultiAdapter((self.layer['portal'],
                                     self.layer['request']),
                                     name=u"replaceText")
        self.ids1 = ["%s-0" % '/'.join(portal['page1'].getPhysicalPath()[2:]),
                     "%s-1" % '/'.join(portal['page1'].getPhysicalPath()[2:])]
        self.ids2 = ["%s-0" % '/'.join(portal['news1'].getPhysicalPath()[2:])]
        self.ids3 = ["%s-0" % '/'.join(portal['page2'].getPhysicalPath()[2:]),
                     "%s-1" % '/'.join(portal['page2'].getPhysicalPath()[2:])]
        self.ids4 = ["%s-0" % '/'.join(portal['link1'].getPhysicalPath()[2:])]

    def test_missing_parameters(self):
        portal = self.layer['portal']
        request = self.layer['request']
        view = self.view
        # no params
        self.assertEqual(json.loads(view()), [])
        # only ids
        view.request.set('id', self.ids1)
        self.assertEqual(json.loads(view()), [])

    def test_single_subn(self):
        portal = self.layer['portal']
        request = self.layer['request']
        view = self.view
        view.request.set('id', self.ids1[1:])
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', re_subn_pattern)
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())
        self.assertEqual(json.loads(view()), [{"status": "OK"}]) 
        self.assertFalse('<a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a href="http://loripsum.net/" class="external-link">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())

    def test_multiple_subn(self):
        portal = self.layer['portal']
        request = self.layer['request']
        view = self.view
        view.request.set('id', self.ids1)
        view.request.set('searchQuery', re_pattern)
        view.request.set('replaceQuery', re_subn_pattern)
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())
        self.assertEqual(json.loads(view()), [{"status": "OK"}, {"status": "OK"}]) 
        self.assertFalse('<a target="_blank" href="http://loripsum.net/">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertFalse('<a target="_blank" href="http://loripsum.net/">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())
        self.assertTrue('<a href="http://loripsum.net/" class="external-link">reprehenderit in voluptate velit</a>' in portal.page1.getText())
        self.assertTrue('<a href="http://loripsum.net/" class="external-link">sit amet, consectetur adipisicing elit</a>' in portal.page1.getText())

    def test_unknow_type(self):
        portal = self.layer['portal']
        request = self.layer['request']
        view = self.view
        view.request.set('id', self.ids4)
        view.request.set('searchQuery', 'foo')
        view.request.set('replaceQuery', 'bar')
        self.assertEqual(json.loads(view()),
                         [{u'status': u'error', u'message': u"Don't know hot to handle http://nohost/plone/link1"}])

