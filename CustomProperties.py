# Copyright (c) 2003, IOPEN Technologies Ltd.
# Author: richard@iopen.co.nz
#
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass, PersistentMapping
from OFS import SimpleItem, PropertyManager

class CustomProperties(SimpleItem.SimpleItem, PropertyManager.PropertyManager):
    """ A simple properties object for creating just a property sheet.
    
    """
    meta_type = "Custom Properties"
    manage_options = PropertyManager.PropertyManager.manage_options + \
                     SimpleItem.SimpleItem.manage_options

    def __init__(self, id, title="Custom Properties"):
        """ Initialize the properties.
           
        """
        self.id = id
        self.title = title

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
