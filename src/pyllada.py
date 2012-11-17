try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

try:
    from StringIO import cStringIO as strio
except ImportError:
    from StringIO import StringIO as strio
    

class pydae:
    __daedict = dict()
    __daedict["xmlns"] = "http://www.collada.org/2005/11/COLLADASchema"
    __daedict["version"] = "1.4.1"

    __liblist = list()
    __liblist.append("library_cameras")
    __liblist.append("library_lights")
    __liblist.append("library_materials")
    __liblist.append("library_effects")
    __liblist.append("library_geometries")
    __liblist.append("library_visual_scenes")
    
    def __init__(self):
        self.tree = ET.ElementTree(ET.Element("COLLADA", pydae.__daedict))

    def __str__(self):
        tmpstr = strio();
        self.tree.write(tmpstr, "US-ASCII")
        return tmpstr.getvalue()

    def write(self, fp, encoding="US-ASCII"):
        self.tree.write(fp, encoding)
        

# Just include a main script to keep testing simple and easy
if __name__ == '__main__':
    import sys, os
    print("I am testing stuff.")

    testdae = pydae()

#    testdae.write(sys.stdout)

    print (testdae)

