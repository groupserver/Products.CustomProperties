# Copyright (C) 2003,2004 IOPEN Technologies Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You MUST follow the rules in STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('CustomProperties')

from Products.CustomProperties.CustomProperties import CustomProperties
class TestCustomProperties(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        self.folder._setObject('CustomProperties', 
                               CustomProperties('CustomProperties','Custom Properties'))
        
        self.cp = getattr(self.folder, 'CustomProperties', None)
        
    def afterClear(self):
        pass    

    def test_01_exists(self):
        self.failUnless(self.cp)

    def test_02_addProperty(self):
        self.cp.manage_addProperty('dc:Title', 'Hello', 'string')
        self.assertEqual(self.cp.getProperty('dc:Title'), 'Hello')
        
    def test_03_delProperty(self):
        self.cp.manage_addProperty('dc:Title', 'Hello', 'string')
        self.cp.manage_delProperties(['dc:Title'])
        self.failIf(self.cp.hasProperty('dc:Title'))

    def test_04_addCallableProperty(self):
        setattr(self.cp, 'dc:Description', lambda: 'Hello')
        self.cp.manage_addProperty('dc:Description', '', 'string')
        self.assertEqual(self.cp.getProperty('dc:Description'), 'Hello')

    def test_05_delCallableProperty(self):
        setattr(self.cp, 'dc:Description', lambda: 'Hello')
        self.cp.manage_addProperty('dc:Description', '', 'string')
        self.cp.manage_delProperties(['dc:Description'])
        self.failIf(self.cp.hasProperty('dc:Description'))
        
    def test_06_addMappedProperty(self):
        setattr(self.cp, 'content_type', 'application/pdf')
        self.cp.manage_addProperty('dc:Format', '', 'string')
        self.cp.manage_addPropertyMapping({'dc:Format': 'content_type'})
        self.assertEqual(self.cp.getProperty('dc:Format'), 'application/pdf')
   
    def test_07_delMappedCallableProperty(self):
        setattr(self.cp, 'content_type', lambda: 'application/pdf')
        self.cp.manage_addProperty('dc:Format', '', 'string')
        self.cp.manage_addPropertyMapping({'dc:Format': 'content_type'})
        self.cp.manage_delProperties(['dc:Format'])
        self.failIf(self.cp.hasProperty('dc:Format'))
        self.failIf(self.cp._property_mapping.has_key('dc:Format'))

    def test_08_addMappedCallableProperty(self):
        setattr(self.cp, 'content_type', lambda: 'application/pdf')
        self.cp.manage_addProperty('dc:Format', '', 'string')
        self.cp.manage_addPropertyMapping({'dc:Format': 'content_type'})
        self.assertEqual(self.cp.getProperty('dc:Format'), 'application/pdf')
        
    def test_09_delMappedCallableProperty(self):
        setattr(self.cp, 'content_type', lambda: 'application/pdf')
        self.cp.manage_addProperty('dc:Format', '', 'string')
        self.cp.manage_addPropertyMapping({'dc:Format': 'content_type'})
        self.cp.manage_delProperties(['dc:Format'])
        self.failIf(self.cp.hasProperty('dc:Format'))
        self.failIf(self.cp._property_mapping.has_key('dc:Format'))

    def test_10_changePropertyMode(self):
        from zExceptions import BadRequest
        setattr(self.cp, 'content_type', lambda: 'application/pdf')
        self.cp.manage_addProperty('dc:Format', '', 'string')
        self.cp.manage_addPropertyMapping({'dc:Format': 'content_type'})
        self.cp.manage_changePropertyMode('dc:Format', 'r')
        try:
            apply(self.cp.manage_changeProperties, (), {'dc:Format': 'foo'})
            self.fail('Should have raised a "BadRequest"')
        except ('BadRequest', BadRequest): # older Zope versions used a string exception
            pass
        self.cp.manage_changePropertyMode('dc:Format', 'w')
        try:
            apply(self.cp.manage_changeProperties, (), {'dc:Format': 'foo'})
        except:
            self.fail('Should not have raised an Exception')

    def test_11_directSettingOfMappedProperty(self):
        setattr(self.cp, 'content_type', 'application/pdf')
        self.cp.manage_addProperty('dc:Format', '', 'string')
        self.cp.manage_addPropertyMapping({'dc:Format': 'content_type'})
        
        self.assertEqual(getattr(self.cp, 'dc:Format', None), 'application/pdf')
        
        setattr(self.cp, 'content_type', 'application/wibble')
        self.assertEqual(getattr(self.cp, 'dc:Format', None), 'application/wibble')
        self.assertEqual(getattr(self.cp, 'content_type', None), 'application/wibble')
        setattr(self.cp, 'dc:Format', 'application/pdf')
        self.assertEqual(getattr(self.cp, 'dc:Format', None), 'application/pdf')
        self.assertEqual(getattr(self.cp, 'content_type', None), 'application/pdf')
        
    
if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCustomProperties))
        return suite
