# Copyright (c) 2003, IOPEN Technologies Ltd.
# Author: richard@iopen.co.nz
#
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass, PersistentMapping
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

class CustomProperties(SimpleItem, PropertyManager):
    """ A simple properties object for creating just a property sheet.
    
    """
    meta_type = "Custom Properties"
    manage_options = PropertyManager.manage_options + \
                     SimpleItem.manage_options

    def __init__(self, id, title="Custom Properties"):
        """ Initialize the properties.
           
        """
        self.id = id
        self.title = title

    def _updateProperty(self, id, value):
        """ Hook for updating a particular property.
        
        """
        # the check method should return the value to be stored or
        # raise an Exception
        check_method = getattr(self, 'check_%s' % id, None)
        if check_method:
            value = check_method(value)
        # use the regular property sheets storage
        PropertyManager._updateProperty(self, id, value)

        # run a reindex if we are CatalogAware
        if hasattr(self, 'reindex_object'):
            self.reindex_object()

    # an example of using foo -- DOCUMENT ME PROPERLY!
    #def check_foo(self, value):
    #    """ Check the value for foo """
    #    return 'foobar'

manage_addCustomPropertiesForm = PageTemplateFile(
    'zpt/manage_addCustomProperties.zpt',
    globals(),
    __name__='manage_addCustomPropertiesForm')

def manage_addCustomProperties(self, id, title='Custom Properties',
                                     REQUEST=None):
    """ Add a CustomProperties to a container.

    """
    ob = CustomProperties(id, title)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self,REQUEST)
    
InitializeClass(CustomProperties)
def initialize(context):
    context.registerClass(
        CustomProperties,
        permission="Add CustomProperties",
        constructors=(manage_addCustomPropertiesForm,
                      manage_addCustomProperties),
        )
