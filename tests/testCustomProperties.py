# Copyright IOPEN Technologies Ltd., 2003
# richard@iopen.net
#
# For details of the license, please see LICENSE.
#
# You MUST follow the rules in README_STYLE before checking in code
# to the head. Code which does not follow the rules will be rejected.  
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
        setattr(self.cp, 'content_type', lambda: 'application/pdf')
        self.cp.manage_addProperty('dc:Format', '', 'string')
        self.cp.manage_addPropertyMapping({'dc:Format': 'content_type'})
        self.cp.manage_changePropertyMode('dc:Format', 'r')
        try:
            apply(self.cp.manage_changeProperties, (), {'dc:Format': 'foo'})
            self.fail('Should have raised a "BadRequest"')
        except 'BadRequest':
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
