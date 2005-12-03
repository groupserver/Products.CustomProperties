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
# You MUST follow the rules in http://iopen.net/STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
#
from AccessControl import getSecurityManager, ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass, PersistentMapping
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from cgi import escape

class CustomProperties(SimpleItem, PropertyManager):
    """ A simple properties object for creating just a property sheet.
    
    """
    security = ClassSecurityInfo()
    
    version = 0.98
    
    meta_type = "Custom Properties"
    manage_options = PropertyManager.manage_options + \
                     SimpleItem.manage_options
    _property_mapping = {}
    
    def __init__(self, id, title="Custom Properties"):
        """ Initialize the properties.
           
        """
        self._property_mapping = {}
        self._p_changed = 1
        
        self.id = id
        self.title = title

    def __setattr__(self, name, value):
        d = self.__dict__
        if name[0] == '_':
            return SimpleItem.__setattr__(self, name, value)
        
        pm = d.get('_property_mapping', {})
        d[name] = value
        
        if hasattr(self, 'check_%s' % name):
            value = getattr(self, 'check_%s' % name)(value)
        
        mp = pm.get(name, None)
        if mp and mp != name:
            setattr(self, mp, value)
            setattr(self, '_p_changed', 1)
        else:
            SimpleItem.__setattr__(self, name, value)
    
    def __getattr__(self, name):
        d = self.__dict__
        
        pm = d.get('_property_mapping', {})        
        try:
            if pm.has_key(name):
                return self.__dict__[pm[name]]
            
            return self.__dict__[name]
        except:
            raise AttributeError, escape(name)

    def getProperty(self, id, d=None):
        """ Get the property 'id', returning the optional second
            argument or None if no such property is found.
    
            Additionally checks to see if there is a mapping between our
            property and another attribute, and if so, gets that attribute 
            instead.
            
        """
        if self.hasProperty(id):
            if self._property_mapping.has_key(id):
                p = getattr(self, self._property_mapping[id])
            else:
                p = getattr(self, id)
            if callable(p):
                p = p()
                
            return p
        
        return d
        
    def propertyValues(self):
        """ Return a list of actual property objects.
            
            Modified from the original version to get the property with the
            getProperty method, to enable overriding there.
             
        """
        return map(lambda i,s=self: s.getProperty(i['id']), self._properties)
 
    def propertyItems(self):
        """ Return a list of (id,property) tuples.
        
            Modified from the original version to get the property with the
            getProperty method, to enable overriding there.
            
        """
        return map(lambda i,s=self: (i['id'], s.getProperty(i['id'])),
                                    self._properties)
        
    def valid_property_id(self, id):
        """ A modification of the PropertyManager version. We actually
            sometimes _need_ to have an existing property, to handle
            callable properties for instance.
            
        """
        if self.hasProperty(id):
            return 0
        if not id or id[:1]=='_' or (id[:3]=='aq_') \
           or (' ' in id) or escape(id) != id:
            return 0
        return 1

    def _updateProperty(self, id, value):
        """ Hook for updating a particular property.
        
        """
        self._p_changed = 1
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
        
    def _setPropValue(self, id, value):
        """ Overrides the PropertyManager method of the same name.
        
            If the property concerned is callable, it tries to set it with
            set_NameOfProperty(value).
            
            Note: no exception is thrown if we can't set the property with
            set_NameOfProperty.
            
        """
        self._p_changed = 1
        self._wrapperCheck(value)
        
        if self._property_mapping.has_key(id):
            id = self._property_mapping[id]
        # check to see if the property already exists, and if it does, check
        # our callable hook
        p = getattr(self, id, None)
        if callable(p):
            if hasattr(self, 'set_%s' % id):
                getattr(self, 'set_%s' % id)(value)
        else:
            setattr(self,id,value)
        
    def _delPropValue(self, id):
        """ Overrides the PropertyManager method of the same name.
        
            If the property is callable, it tries to delete it with del_NameOfProperty().
            
            Note: no exception is thrown if we can't delete the property with
            del_NameOfProperty.
            
        """
        if self._property_mapping.has_key(id):
            id = self._property_mapping[id]
        
        p = getattr(self, id)
        
        if callable(p):
            if hasattr(self, 'del_%s' % id):
                getattr(self, 'del_%s' % id)()
                return
                
        delattr(self, id)

    def _delProperty(self, id):
        """ Extends the PropertyManager method of the same name.
        
        """
        PropertyManager._delProperty(self, id)
        if self._property_mapping.has_key(id):
            self._p_changed = 1
            mp = self._property_mapping[id]
            del(self._property_mapping[id])

    def manage_changePropertyMode(self, id, mode='wd'):
        """ Change the mode of the property. Mode is a string consisting
            of one or more of 'w','d','r' (writeable, deletable, readable).
        
        """
        new_properties = []
        if self.hasProperty(id):
            for property_dict in self._properties:
                if property_dict['id'] == id:
                    property_dict['mode'] = mode
                new_properties.append(property_dict)
            self._properties = tuple(new_properties)
        else:
            raise 'AttributeError', 'No such property %s' % id
        
    def manage_addPropertyMapping(self, mapping):
        """ Adds a mapping between one or more properties and an attribute/method.
        
            The property being mapped must exist prior to mapping, as must the
            attribute/method we are mapping to.
            
            Mapping is a dictionary containing {'propertyid': 'attributeid'}.
            
        """
        self._p_changed = 1
        
        for id in mapping:
            if self.hasProperty(id):
                if hasattr(self, mapping[id]):
                    self._property_mapping[id] = mapping[id]
                    # we delete the original attribute, because we are now mapping it,
                    # and we want getattr to work
                    delattr(self, id)
                else:
                    raise 'AttributeError', 'No such attribute or method %s' % mapping[id]
            else:
                raise 'AttributeError', 'No such property %s' % id

    security.declareProtected('Upgrade objects', 'upgrade')
    security.setPermissionDefault('Upgrade objects', ('Manager', 'Owner'))
    def upgrade(self):
        """ Upgrade to the latest version.
            
            UnitTest: TestXWFFileLibrary
        """
        currversion = getattr(self, '_version', 0)
        if currversion == self.version:
            return 'already running latest version (%s)' % currversion

        self._version = self.version
        
        self._property_mapping = getattr(self, '_property_mapping', {})
        self._p_changed = 1
        
        return 'upgraded %s to version %s from version %s' % (self.getId(),
                                                              self._version,
                                                              currversion)
                                                              
    # an example of using value checking -- DOCUMENT ME PROPERLY!
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
