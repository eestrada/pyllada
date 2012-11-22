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

class pydae(object):
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

    __defaultunits = {'meter': 1.0, 'decimeter': 0.1, 'centimeter': 0.01, \
            'millimeter': 0.001, 'foot': 0.3048, 'inch': 0.0254 }

    def __init__(self, tool=('pyllada ' + __version__)):
        '''Initialize self.'''
        tmpio = strio(pydae.__template)
        self.newdoc = True
        self.tree = xet.parse(tmpio)
        self.root = self.tree.getroot()
        self.root.attrib['xmlns']='http://www.collada.org/2005/11/COLLADASchema'
        tmpel = self.root.find('asset/contributor/author')
        tmpel.text = str(getpass.getuser())
        tmpel = self.root.find('asset/contributor/authoring_tool')
        tmpel.text = tool


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

    def setUnitScale(self, scaletype = 'meter'):
        '''Sets the unit type to have the Collada document use.
        
        scaletype is a string corresponding to the unit size to use. The available options are: meter, decimeter, centimeter, millimeter, foot, inch. Returns True if the type was set. False otherwise.Calling without any parameters will set the units back to the default of meters.'''
        if isinstance(scaletype, basestring):
            tmpunit = float()
            tmptype = str()
            try:
                tmpunit = float(__defaultunits[scaletype])
                tmptype = str(scaletype)
            except KeyError:
                return False

            self.root.find('asset/unit').attrib = {'name': tmptype, 'meter':tmpunit}
            return True

        return False

    def setUpAxis(self, upaxis='Y_UP'):
        '''Set the up axis of the scene.
        
        Defaults to Y up. The input is a string with a value of: "x", "y", "z", "X_UP", "Y_UP", or "Z_UP". This method is case insensitive. Returns true on successful change. False otherwise.'''

        # Return false if this isn't a string
        if not isinstance(upaxis, basestring):
            return False

        axisdict = {'x':'X_UP', 'y':'Y_UP', 'z':'Z_UP'}
        tmpkey = upaxis.lower[0]
        tmpel = self.root.find('asset/up_axis')
        
        try:
            text = axisdict[tmpkey]
            tmpel.text = text
        except KeyError:
            return False

    def addGeometry(self):
        '''Add to geometry library. Not implemented yet.'''
        return NotImplemented

    def indent(self, elem, level=0, white='  '):
        '''Recursive method to create pleasing indentation in Collada docs.'''
        i = '\n' + level * white
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + '  '
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def write(self, fobj=sys.stdout, encoding='UTF-8'):
        '''Write collada document to the file specified by "fobj".

        fobj can be either a file name or a file like object open for writing. encoding is the encoding of the output (default is UTF-8). Encoding does not generally need to be changed.'''
        now = datetime.isoformat(datetime.now())
        
        if self.newdoc:
            tmpel = self.root.find('asset/created')
            tmpel.text = now
        
        tmpel = self.root.find('asset/modified')
        tmpel.text = now
        self.indent(self.root)
        self.tree.write(fobj, encoding)

# Just include a main script to keep testing simple and easy
if __name__ == '__main__':
    import sys
    
    print('I am testing stuff.')

    testdae = pydae()

#    testdae.test()

#    testdae.write(sys.stdout)

    stest = 'What am I?'

    print(type(stest))

    print(xet)
    print(strio)

    print(testdae)

