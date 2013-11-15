import re

linePattern = re.compile("(=[\s]*[\w\.]*) ([\w\.]*[\s]*=)")
#Splits the file at every bracket to ensure proper parsing
def structureFile(path, folder, name):
    functionOutput = []
    encode = findEncode(path, folder, name)
    with open('%s/%s/%s' % (path, folder, name), encoding=encode) as file:
        for line in file:
            if "#" in line:
                line = line.split("#")[0]
            if line == "":
                continue
            line = line.replace("{", "{\n").replace("}", "\n}").strip() #Splits line at brackets
            if line == "":
                continue
            if "=" in line:
                count = line.count("=")
                if count > 1:
                    for values in range(count):
                        line = linePattern.sub("\g<1>\n\g<2>", line) #Splits lines with more than one statement in two
            if "\n" in line:
                parts = line.split("\n")
                for p in parts:
                    functionOutput.append(p)
            else:
                functionOutput.append(line)
    return functionOutput

#Tries both cp1252 (ANSI) and UTF-8 encoding for reading files
def findEncode(path, folder, name):
    functionOutput = ''

    encodes = [ 'utf-8', 'cp1252' ]
    for e in encodes:
        try:
            fh = open('%s/%s/%s' % (path, folder, name), 'r', encoding=e)
            fh.readlines()
            fh.seek(0)
        except UnicodeDecodeError:
            print('error on %s, trying another encoding' % e)
        else:
            print('encoding was %s' % e)
            functionOutput = e
            return functionOutput

#Reads in a statement file as a dictionary
def readStatements(localisationName):
    localisation = {}
    with open('%s.txt' % localisationName) as effectsFile:
        for line in effectsFile.readlines():
            if not ":" in line: #Not a statement string
                continue
            StatementName, formatString = line.split(':', 1)
            localisation[StatementName.strip()] = formatString.strip()

    return localisation

#Reads in a definition file as a dictionary
def readDefinitions(path, name):
    definitions = {}
    with open(path+"/localisation/%s_l_english.yml" % name, encoding="utf-8") as definitionsFile:
        lines = definitionsFile.readlines()
        lineNumber = 1
        for line in lines[1:]:
            if not ":" in line:
                continue
            try:
                identifier, value = line.split(':', 1)
                definitions[identifier.strip()] = value.strip('" \n')
            except ValueError:
                print ("%d -> %s" % (lineNumber, line))
            lineNumber += 1

    return definitions

#Determines the current level of nesting
def nestingCheck(line, nesting, nestingIncrement):
    nestingIncrement = 0
    #Thanks to file restructuring, it is impossible for there to be multiple brackets on a line
    if "{" in line:
        nesting += 1
        nestingIncrement = 1
    elif "}" in line:
        nesting -= 1
        nestingIncrement = -1
    return nesting, nestingIncrement


def getValues(line):
    line = line.split("=")
    line[0] = line[0].strip()
    try: #Checks if the command has a value
        line[1] = line[1].strip().strip('{}"')
        return line[0], line[1]
    except IndexError:
        return line[0], ""