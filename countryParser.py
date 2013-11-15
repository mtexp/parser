from common import *

def main(fileName):
    global outputDict
    inputFile = structureFile(path, "history/countries/", fileName) #Transcribes game file to more parseable format
    outputDict = {}
    for line in inputFile:
        #Determines how deeply nested the current line is
        nesting, nestingIncrement = nestingCheck(line, nesting, nestingIncrement)
        if nesting > 0:
            continue
        command, value = getValues(line)
        if not '"%s"' % command in countryCommands:
            continue
        value = valueLookup(value)
        output(command, value)
    outputText = "| [[File:%s.png|100px|border]] '''[[%s]]''' || '''%s'''" % (countries[fileName[:3]], countries[fileName[:3]], fileName[:3])
    for token in countryCommands:
        try:
            outputText += " || " + outputDict[token.strip('"')]
        except KeyError:
            outputText += " || "
    #for trigger in ideas.values():
    #    if "tag = %s" % fileName[:3] in trigger:
    #        outputText += " || Unique"
    #        break
    #if not "Unique" in outputText:
    #    outputText += " || "
    try:
        return outputText +"\n|-\n"
    except UnboundLocalError:
        return ""

def valueLookup(value):
    try:
        return provinces["PROV"+value]
    except KeyError:
        try:
            int(value)
            print("Could not look up province with value %s" % value)
        except ValueError:
            pass
    try:
        return lookup[value]
    except KeyError:
        pass
    return value

def output(command, value): #Outputs line to a temp variable. Written to output file when input file is parsed
    global outputDict
    outputDict[command] = value

if __name__ == "__main__":
    import cProfile, pstats
    pr = cProfile.Profile()
    pr.enable()

    import time #Used for timing the parser
    start = time.clock()
    import os #Used to grab the list of files
    settings = readStatements("settings")
    path = settings["path"].replace("\\", "/")
    modPath = settings["mod"].replace("\\", "/")

    #Dictionaries of known statements
    countryStatements = readStatements("statements/countryStatements")
    countryCommands = countryStatements["commands"].split()
    nesting, nestingIncrement = 0, 0
    finalOutput = ""
    #ideas = {}
    #unformattedIdeas = structureFile(path, "common/ideas", "00_country_ideas.txt")
    #triggerFound = False
    #for line in unformattedIdeas:
    #    nestingCheck(line)
    #    if triggerFound:
    #        if nesting == 1:
    #            triggerFound = False
    #        else:
    #            ideas[token].append(line)
    #    if nesting == 1 and nestingIncrement == 1:
    #        token = getValues(line)[0]
    #        ideas[token] = []
    #    elif "trigger" in line:
    #        triggerFound = True

    try:
        #Dictionaries of relevant values
        provinces = readDefinitions(path, "prov_names")
        countries = readDefinitions(path, "countries")
        countries.update(readDefinitions(path, "text"))
        countries.update(readDefinitions(path, "eu4"))
        lookup = readDefinitions(path, "eu4")
        lookup.update(readDefinitions(path, "text"))
        lookup.update(readDefinitions(path, "opinions"))
        lookup.update(readDefinitions(path, "powers_and_ideas"))
        lookup.update(readDefinitions(path, "decisions"))
        lookup.update(readDefinitions(path, "modifers"))
        lookup.update(readDefinitions(path, "muslim_dlc"))
        lookup.update(readDefinitions(path, "Purple_Phoenix"))
        lookup.update(readDefinitions(path, "core"))
        lookup.update(readDefinitions(path, "missions"))
        lookup.update(readDefinitions(path, "diplomacy"))
        for fileName in os.listdir("%s/history/countries" % path):
            print("Parsing file %s" % fileName)
            finalOutput += main(fileName)
        with open("output/countryOutput.txt", "w", encoding="utf-8") as outputFile:
            outputFile.write(finalOutput)
    except FileNotFoundError:
        print("File not found error: Make sure you've set the file path in settings.txt")
    elapsed = time.clock() - start
    print("Parsing the files took %.3f seconds" %elapsed)
    pr.disable()
    sortby = 'tottime'
    ps = pstats.Stats(pr).sort_stats(sortby)
    ps.print_stats()