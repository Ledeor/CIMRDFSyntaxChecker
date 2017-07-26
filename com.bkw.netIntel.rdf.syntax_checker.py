import datetime
import sys
import os
import re
from collections import deque

filepath = ""

OT_RDF = "<RDF:"
CT_RDF = "</RDF:"

OT_CIM = "<CIM:"
CT_CIM1 = "</CIM:"
CT_CIM2 = "/>"


# Nesting iterators (open tag: +1, close tag: -1)
itrRDF = 0
itrCIMClass = 0
itrCIMAttrib = 0

# Blocks count (open tag: +1)
countRDFBlocks = 0
countCIMClasses = 0  # i.e. 1st level blocks
countCIMAttribs = 0  # i.e. 2nd level++ nested blocks

countNestedAttribs = 0

lClasses = []
seen = set()

def cimAttributeContext(openTAG, iLine):
    global itrCIMAttrib
    global countCIMAttribs
    global countNestedAttribs
    global sampleNestedLine
    if openTAG:
        itrCIMAttrib = itrCIMAttrib + 1
        countCIMAttribs = countCIMAttribs + 1
        if itrCIMAttrib > 1:
            countNestedAttribs = countNestedAttribs + 1
            print (">>> Nested CIM attribute context in line " + str(iLine))
            return -1
    else:
        itrCIMAttrib = itrCIMAttrib - 1

    return 0

def cimContext(openTAG, iLine):
    global itrCIMClass
    global countCIMClasses
    if openTAG:
        if itrCIMClass == 0:
            countCIMClasses = countCIMClasses + 1
            itrCIMClass = itrCIMClass + 1
        else:
            if cimAttributeContext(True, iLine) == -1:
                return -1
    else:
        if itrCIMAttrib > 0:
            cimAttributeContext(False, iLine)
        else:
            itrCIMClass = itrCIMClass - 1
            if itrCIMClass < 0:
                print (">>> Close CIM tag without open tag in line " + str(iLine))
                itrCIMClass = 0

    return 0

def rdfContext(openTAG, iLine):
    global itrRDF
    global countRDFBlocks
    if openTAG:
        countRDFBlocks = countRDFBlocks + 1
        itrRDF = itrRDF + 1
        if itrRDF > 1:
            print (">>> Nested RDF context in line " + str(iLine))
    else:
        itrRDF = itrRDF - 1
        if itrRDF < 0:
            print (">>> Close RDF tag without open tag in line " + str(iLine))
            itrRDF = 0

def main():
    sys.stdout.write(datetime.datetime.now().strftime("%I:%M%p") + " Trying to open " + filepath + "...")
    sys.stdout.flush()
    try:
        f = open(filepath, 'rt')
    except:
        print ("failed" + '\n' + datetime.datetime.now().strftime("%I:%M%p") + " Cannot open file: " + filepath)
        return

    print ("ok" + " (" + str(os.stat(filepath).st_size >> 10) + " KB)")

    print (datetime.datetime.now().strftime("%I:%M%p") + " Start parsing...")
    curLine = ""
    i = 0
    preContextList = deque(maxlen=15)
    for line in f:
        i = i + 1

        curLine = str(line).upper()
        preContextList.append(str(line))
        if OT_RDF in curLine:
            rdfContext(True, i)

        if CT_RDF in curLine:
            rdfContext(False, i)

        if OT_CIM in curLine:
            if cimContext(True, i) == -1:
                print (">>> Error in line " + str(i) + ": ")
                print (str(''.join(preContextList)))
                f.close()
                print (datetime.datetime.now().strftime("%I:%M%p") + "...Program stopped!")
                sys.exit(1)

        if CT_CIM1 in curLine or CT_CIM2 in curLine:
            cimContext(False, i)

    print (datetime.datetime.now().strftime("%I:%M%p") + " ...parsing finished.")

    f.close()

    print ("")
    print (">File has " + str(i) + " lines.")
    print (">RDF blocks: " + str(countRDFBlocks))
    print (">CIM classes: " + str(countCIMClasses) + " (i.e. 1st level CIM blocks)")
    print (">CIM attributes: " + str(countCIMAttribs) + " (i.e. 2nd level++ nested CIM blocks)")
    if countNestedAttribs > 0 :
        print (">>>Nested attributes: " + str(countNestedAttribs))
    print ("")



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print ("Missing path as first argument.")
        sys.exit(1)
    else:
        filepath = sys.argv[1]
    print (datetime.datetime.now().strftime("%I:%M%p") + " Starting...")
    main()
    print (datetime.datetime.now().strftime("%I:%M%p") + " ...done.")
