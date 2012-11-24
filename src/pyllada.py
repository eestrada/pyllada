from __future__ import division, print_function, unicode_literals
import sys
import getpass
from datetime import datetime

def __killme(module):
    message = '''\n\nSomething went terribly wrong with importing modules. \
This script needs at least python version 2.6 in order to work properly. \
Please be sure you have at least version 2.6 installed.\n\n'''
    sys.exit(message)


# Some checks to make older versions of python compatible with Py3k
if sys.version_info[0] < 3:
    # Make open() act like Py3k
    import codecs
    open = codecs.open
    
    try:
        bytes # If this works we are already forward compatible with Py3k
    except NameError:
        bytes = str

    # In Py3k, strings are Unicode text
    str = unicode

    try:
        import xml.etree.cElementTree as xet
    except ImportError:
        import xml.etree.ElementTree as xet

    try:
        from cStringIO import StringIO as strio
    except ImportError:
        from StringIO import StringIO as strio
else:
    from io import StringIO as strio
    import xml.etree.ElementTree as xet


__version__ = '0.1'

class daedoc(object):
    __template ='''<?xml version='1.0'?>
    <COLLADA version='1.4.1'>
        <asset>
            <contributor>
                <author></author>
                <authoring_tool></authoring_tool>
                <comments></comments>
                <copyright></copyright>
            </contributor>
            <created></created>
            <modified></modified>
            <unit meter='1.0' name='meter'/>
            <up_axis>Y_UP</up_axis>
        </asset>
        <library_cameras></library_cameras>
        <library_lights></library_lights>
        <library_materials></library_materials>
        <library_effects></library_effects>
        <library_geometries></library_geometries>
        <library_visual_scenes></library_visual_scenes>
        <scene></scene>
    </COLLADA>
    '''

    __defaultunits = {'kilometer': 1000.0, 'meter': 1.0, 'decimeter': 0.1, \
    'centimeter': 0.01,'millimeter': 0.001, 'mile': 1609.34, 'yard': 0.9144, \
    'foot': 0.3048, 'inch': 0.0254 }

    def __init__(self, tool='', fileobj = None):
        '''Initialize self.'''
        
        self.newdoc = not fileobj
        tmpio = strio()
        tmpattr = '____daedoc_pseudo_attr'

        if not self.newdoc:
            tmpio = open(str(fileobj), buffering=0, encoding='UTF-8')
            tmpstr = tmpio.read()
            tmpstr = tmpstr.replace('xmlns=', tmpattr+'=', 1)
            tmpio = strio(tmpstr)
        else:
            tmpio = strio(daedoc.__template)
        
        self.tree = xet.parse(tmpio)
        self.root = self.tree.getroot()

        if self.root.attrib.has_key(tmpattr):
            self.root.attrib['xmlns'] = self.root.attrib[tmpattr]
            self.root.attrib.pop(tmpattr)
        else:
            self.root.attrib['xmlns']='http://www.collada.org/2005/11/COLLADASchema'
        
        tmpel = self.root.find('asset/contributor/author')
        tmpel.text = str(getpass.getuser())
        tmpel = self.root.find('asset/contributor/authoring_tool')
        tmpel.text = 'pyllada ' + __version__ + ' | ' + tool


    def __str__(self):
        '''Return string representation of self.'''
        tmpstr = strio();
        self.write(tmpstr)
        return tmpstr.getvalue()

    def __sizeof__(self):
        '''Return size of self. This roughly corresponds to the size of the Collada XML tree.'''
        return sys.getsizeof(self.tree)
    
    def getUnitScale(self):
        '''Returns the scale of the collada file.

        More specifically this method returns a tuple containing the unit scale name as a string and unit scale (in relation to meters) as a float. The default scale is ('meter', 1.0)'''
        unit = self.root.find('asset/unit')
        usfloat = float(unit.attrib['meter'])
        usname = str(unit.attrib['name'])
        return tuple(usname, usfloat)

    def setUnitScale(self, scaletype = 'meter', scaleval = None):
        '''Set the unit type and scale that the Collada document will use.
        
        If called with both scaletype and scaleval, this method will set the scene units to the name of "scaletype" cast as a string, and the meter scale to "scaleval" cast to a float. This allows you to set any unit type with any scaling value, even made up units of measurement (e.g. name="spam-and-eggs" meter="12345.6789").
        
        If called with only scaletype, then scaletype is a string corresponding to the unit size to use and the scalevalue will be filled automatically if "scaletype" is a known type. The value of "scaletype" should be a string or something that can be cast to a string. The available options are: "kilometer", "meter", "decimeter", "centimeter", "millimeter", "mile", "yard", "foot", and "inch".
        
        Calling without any parameters will set scene unit scale back to the default of meters.

        Returns True if the type was set. False otherwise.'''

        tmpel = self.root.find('asset/unit')
        if(scaleval != None):
            tmpel.attrib = {'name': str(scaletype), 'meter':str(float(scaleval))}
        else:
            tmpunit = str()
            tmptype = str(scaletype).lower()
            try:
                tmpunit = str(daedoc.__defaultunits[tmptype])
            except KeyError:
                return False
            tmpel.attrib = {'name': tmptype, 'meter':tmpunit}

        return True

    def setUpAxis(self, upaxis='Y_UP'):
        '''Set the up axis of the scene.
        
        Defaults to Y up. The input is a string with a value of: "x", "y", "z", "X_UP", "Y_UP", or "Z_UP". This method is case insensitive. Returns True on successful change. False otherwise.'''

        axisdict = {'x':'X_UP', 'y':'Y_UP', 'z':'Z_UP'}
        tmpkey = str(upaxis).lower()[0]
        tmpel = self.root.find('asset/up_axis')
        
        try:
            text = axisdict[tmpkey]
            tmpel.text = text
        except KeyError:
            return False

        return True

    def addGeometry(self):
        '''Add to geometry library. Not implemented yet.'''
        return NotImplemented

    def _indent(self, elem, white='\t\t', level=0):
        '''Recursive method to create pleasing indentation in Collada docs.
        
        Called by default when writing file to disk or generating a string representation of the document.'''

        i = '\n' + level * white
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + '  '
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level = level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def _flatten(self, elem):
        '''Recursive method to remove unnecessary white space from the document.
        
        This can make documents slightly smaller on disk with the downside that human readability is reduced. However, the document will still be parsable by machine.
        
        The savings in disk spaced gained by flattening the document are usually very minimal, so using this method is discouraged.'''

        if isinstance(elem.text, basestring):
            elem.text = elem.text.strip()
        if isinstance(elem.tail, basestring):
            elem.tail = elem.tail.strip()
        for elem in elem:
            self._flatten(elem)
    

    def write(self, fileobj=sys.stdout, encoding='UTF-8', indent=True):
        '''Write collada document to the file specified by "fileobj".

        fileobj can be either a file name or a file like object open for writing. encoding is the encoding of the output (default is UTF-8). Encoding does not generally need to be changed.'''
        
        now = datetime.isoformat(datetime.now())
        if self.newdoc:
            tmpel = self.root.find('asset/created')
            tmpel.text = now
        tmpel = self.root.find('asset/modified')
        tmpel.text = now
        
        if indent:
            self._indent(self.root)
        else:
            self._flatten(self.root)

        self.tree.write(fileobj, encoding)

# Just include a main script to keep testing simple and easy
if __name__ == '__main__':
    import sys
    
    print('I am testing stuff.')

    testdae = daedoc(fileobj = '/tmp/test.dae')

#    testdae.test()

    testdae.setUnitScale('Mile')

#    print(help(daedoc.setUnitScale))

    testdae.write('/tmp/testflat.dae', indent=False)
    testdae.write('/tmp/testindent.dae', indent=True)
    
    print(testdae.newdoc)
