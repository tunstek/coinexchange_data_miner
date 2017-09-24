import re, os


def split(arr, size):
     arrs = []
     while len(arr) > size:
         pice = arr[:size]
         arrs.append(pice)
         arr   = arr[size:]
     arrs.append(arr)
     return arrs


def findOccurences(s, ch):
    res = []
    for tup in enumerate(s, start=0):
        if tup[1] == ch:
            res.append(tup[0])
    return res


def addSpacePaddingEitherSide(s,chArr):
    newStr = ""
    for char in s:
        spaceAdded = False
        for ch in chArr:
            if char==ch:
                newStr = newStr + " " + char + " "
                spaceAdded = True
        if not spaceAdded:
            newStr = newStr + char
    return newStr

def parseToValidJson(s):

    #replace whitespace with a single space
    s = ' '.join(s.split())

    #replace all single quotes with double quotes
    s = s.replace("'",'"')

    #Space everything properly
    s = addSpacePaddingEitherSide(s,['{','}','[',']'])

    #add missing '"' where necessary
    arr = s.split()
    newArr = []
    for word in arr:
        if re.match("^[A-Za-z]*$", word):
            word = '"' + word + '"'
        elif word[-1] == ':':
            word = '"' + word[:-1] + '"' + word[-1]
        newArr.append(word)
    s = ' '.join(newArr)


    #remove trailing ',' if present
    lstCommaIndex = s.rfind(",")
    substr = s[lstCommaIndex:]
    if "{" not in substr or "}" not in substr:
        s = s[:lstCommaIndex] + s[lstCommaIndex+1:]

    return s



def mkdir(dirName):
    # OS File handling
    dirname=os.path.dirname
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), dirName)

    #Create the directory
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
