from common import *

def main(path, folder, fileName):
    global outputText, nestingIncrement, nesting
    inputFile = structureFile(fileName, path, folder) #Transcribes game file to more parseable format
    specialSection, negative, negativeNesting, printSection, base_chance, option, random_list, randomNesting = False, False, False, False, False, False, False, False
    value1, value2, modifier, command, value = "", "", "", "", ""
    outputText = []
    for line in inputFile:
        nesting, nestingIncrement = nestingCheck(line, nesting) #Determines how deeply nested the current line is
        if nesting <= 1:
            continue #Nothing relevant is nested this low
        if nesting == 2:
            if folder != "events":
                if nestingIncrement == 1: #At these values the name is encountered
                    name = statementLookup(line, lookup, getValues(line)[0]+"_title", 0) #Finds just the name identifier
                    output(name, 2)
            elif "title" in line:
                name = statementLookup(line, lookup, getValues(line)[1], 0) #Finds just the title identifier
                output(name, 2)
                if specialSection == "province_event":
                    output("Province event", -1)
                    specialSection = False
            if "is_triggered_only" in line:
                output("Cannot fire randomly", -1)
                continue
            elif "province_event" in line:  #This should be printed after the name of the event
                specialSection = "province_event"
            elif "fire_only_once" in line:  #One of the few instances of relevant info that isn't a title on this nesting level
                output("Can only fire once", -1)
            elif nestingIncrement == -1: #End of relevant section
                printSection = False
            continue #Nothing more to do this iteration
        else:
            negative, line, negativeNesting = negationCheck(negative, line, negativeNesting)
        if folder == "decisions":
            if any(x in line for x in ["potential", "allow", "effect"]):
                printSection = True #Only these sections are relevant
        elif folder == "missions":
            if any(x in line for x in ["allow", "success", "abort", "effect"]):
                if not "abort_effect" in line:
                    printSection = True #Only these sections are relevant
        elif folder == "events":
            if any(x in line for x in ["trigger", "mean_time_to_happen", "option", "immediate"]):
                printSection = True #Only these sections are relevant
                if "option" in line:
                    option = True
                    continue #This is handled by the "name" attribute instead
            elif "ai_chance" in line:
                base_chance = True #Tells the parser to look for the base chance
            elif "factor" in line:
                if base_chance:
                    line = statementLookup(line, statements, "factor_base", getValues(line)[1])
                    base_chance = False
                    output(line, 0)
                else:
                    line = statementLookup(line, statements, "factor", getValues(line)[1])
                    output(line, 1)
                continue #Nothing more to do here
            elif option and "name" in line:
                line = "Option: "+valueLookup(getValues(line)[1], "name")[0]+":" #Shows clearly that it is an option
                output(line, 1)
                option = False
                continue #Nothing more to do here
        if not printSection:
            continue #Nothing more to do this iteration
        if command == "num_of_owned_provinces_with": #The line itself needs to be ignored, but the value needs to be extracted
            if "value" in line:
                value = getValues(line)[1]
                if negative:
                    output(statementLookup(line, statements, "num_of_owned_provinces_with_false", value), 1)
                    negative = False
                else:
                    output(statementLookup(line, statements, "num_of_owned_provinces_with", value), 1)
                command = ""
            continue
        if command == "define_advisor":
            if "type" in line:
                value = lookup[getValues(line)[1]]
                output(statementLookup(line, statements, command, value), 1)
                command = ""
            continue
        if command == "add_unit_construction":
            if "type" in line:
                value = lookup[getValues(line)[1].upper()]
                output(statementLookup(line, statements, command, value), 1)
                command = ""
            continue
        command, value = getValues(line)
        if command == "random_list": #Random lists are a bit special
            random_list = True
            output(statementLookup(line, statements, "random_list", ""), False)
            randomNesting = nesting - 1 #Tells the Parser when to stop parsing as a random_list
            continue
        elif command in ["num_of_owned_provinces_with", "define_advisor", "add_unit_construction"]:
            continue #This is handled next iteration
        if randomNesting == nesting:
            random_list = False
        #These commands span multiple lines, so they need special handling
        if '"%s"' % command in exceptions["specialCommands"]:
            specialSection = True
            specialType = command
            continue #Nothing more to do this iteration
        elif specialSection and nestingIncrement != -1:
            #Assign the correct values
            if '"%s"' % command in exceptions["value1"]:
                value1 = valueLookup(value, specialType)[0]
                if command == "name":
                    modifier = value
                if specialType == "trading_part":
                    value1 =str(round(100*float(value1), 1)).rstrip("0").rstrip(".")
            elif '"%s"' % command in exceptions["value2"]:
                value2 = valueLookup(value, specialType)[0]
                if command == "which":
                    match = re.match(r"\s*which\s*=\s*([\w\"]*)\s*value\s*=\s*(\d+)\s*",line)
                    if match:
                        value2 = match.group(1)
                        value1 = match.group(2)
                if command == "duration":
                    if value2 == "-1":
                        value2 = "the rest of the campaign"
                    elif int(value2) <= 365: #Convert to months
                        value2 = str(round(int(value2)/365*12))
                        value2 += " months"
                    else: #Convert to years
                        value2 = str(round(int(value2)/365, 2))
                        value2 = value2.rstrip("0").rstrip(".")
                        value2 += " years"
            elif specialType == "religion_years" and command != "":
                value1 = valueLookup(command, specialType)[0]
                value2 = value
            continue #Nothing more to do this iteration
        if not specialSection:
            line, negative = formatLine(command, value, negative, random_list) #Looks up the command and value, and formats the string
            if line != "":
                output(line, negative)
        elif nestingIncrement == -1:
            specialSection = False
            #Outputs commands that span multiple lines
            if negative:
                specialType += "_false"
            if value2 != "":
                if '"%s"' % specialType in exceptions["invertedSpecials"]:
                    line = special[specialType] % (value2, value1)
                elif specialType in special:
                    line = special[specialType] % (value1, value2)
            elif specialType in statements:
                line = statements[specialType] % value1
            output(line, negative+1)
            if modifier != "":
                getModifier(modifier) #Looks up the effects of the actual modifier
                modifier = ""
            value1 = ""
            value2 = ""
    with open("output/%s" % fileName, "w", encoding="utf-8") as outputFile:
        outputFile.write("".join(outputText))
 
def negationCheck(negative, line, negativeNesting):
    #Negation via NOT
    if "NOT" in line:
        negative = 1
        negativeNesting = nesting-1
        line = line.lstrip("NOT =")
    elif negativeNesting == nesting:
        negative = False
    return negative, line, negativeNesting
 
def formatLine(command, value, negative, random_list):
    if command == "{":
        return "", negative
    if "}" in command: #For some reason this occasionally won't get caught
        command = command.strip()
        if command == "}" or command == "{":
            return "", negative
    try:
        # [myzael] adding special exception for coloanial range. Dirty, but works and I have no creativity atm.
        if(command == "range"):
            try:
                float(value)
                command += "_modifier"
            except ValueError:
                command += "_trigger"

        if "%%" in statements[command]: #Percentage values should be multiplied
            value = str(round(100*float(value), 1)).rstrip("0").rstrip(".")
    except KeyError:
        pass

    #Local negation
    if value == "no":
        localNegation = True
    else:
        localNegation = False
 
    value, valueType = valueLookup(value, command)
 
    #Special exceptions
    if valueType == "country":
        if '"%s"' % command in exceptions["countryCommands"]:
            command += "_country"
    elif value == "capital":
        value = "the capital"

    #Buildings
    try:
        if negative:
            return special["building_false"] % (value, lookup["building_"+command]), negative
        else:
            return special["building"] % (value, lookup["building_"+command]), negative
    except KeyError:
        pass

    #Negation
    if negative and not localNegation or not negative and localNegation:
        if value != "":
            command += "_false" #Unique lookup string for false version
        elif "any_" in command:
            command += "_false"
            negative = False #Contents of a "none of the following" scope don't need to be negated
   
    #Fallback code in case the lookups fail
    if value != "":
        line = "%s = %s" % (command, value)
    else:
        line = command
 
    #Lookup of human-readable string
    if len(command) == 3 and re.match("[A-Z]{3}", command) and command != "AND" and command != "DIP" and command != "MIL" and command != "ADM":
        line = statementLookup(line, countries, command, value)
        return statementLookup(line, lookup, command, value)+":", negative
    elif command != "" and value == "":
        line = statementLookup(line, lookup, command, value)+":"
        try:
            command = str(int(command))
            if not random_list:
                line = statementLookup(line, provinces, "PROV"+command, value)+":"
            else:
                line = statementLookup(line, statements, "random_list_chance", command)
        except ValueError:
            pass

    line = statementLookup(line, statements, command, value)
    return line, negative

# [myzael] this method does not fulfill the contract temporarily, because of merging of events and lookup dicts.
# But it does not matter for now, as the only time the second element of the returned tuple is checked, it is neither
# "other" nor "events". Should that ever no longer be the case, the dicts and this method must be changed accordingly.
def valueLookup(value, command):
    if value == "":
        return value, "other"

    #Assign province
    if '"%s"' % command in exceptions["provinceCommands"]: #List of statements that check provinces
        if "PROV"+value in provinces:
            return provinces["PROV"+value], "province"
        # else:
        #     print("Could not look up province with value: %s for command: %s" % (value,command))
    #Root
    if value.lower() == "root":
        return "our country", "country"
    if value.lower() == "from":
        return "our country", "country"

    #Assign country. 3 capitalized letters in a row is a country tag
    if len(value) == 3 and re.match("[A-Z]{3}", value):
        if value in countries:
            return countries[value], "country"
        elif value in lookup:
            return lookup[value], "country"
        else:
            print("Could not look up country with value %s" % value)

    if value != "" and re.match("[a-zA-Z]", value): #Try to match a value with text to localisation
        if value in lookup:
            if folder == "events":
                return lookup[value], "event"
            else:
                return lookup[value], "other"
        elif "building_"+value in lookup:
            return lookup["building_"+value], "other"
        elif value+"_title" in lookup:
            return lookup[value+"_title"], "other"
        else:
            return value, "other"
    return value, "other"
 
#Lookup of human-readable string
def statementLookup(line, check, command, value):
    #if command in check:
    try:
        return check[command] % value
    except TypeError:
        return check[command]
    except (KeyError, ValueError):
        return line
 
#Looks up the actual effects of modifiers
def getModifier(modifier):
    modifierFound = False
    #Rare enough that going line by line is efficient enough
    for line in eventModifiers:
        if not modifierFound:
            if modifier in line:
                modifierFound = True
                if "}" in line:
                    output("No effects", 0)
                    break
            continue
        elif not "icon" in line:
            if "}" in line:
                break #End of modifier found
            command, value = getValues(line)
            line = formatLine(command, value, 0, False)[0]
            if re.match("[0-9]", line):
                line = "+" + line
            if line != "":
                output(line, 0)

def output(line, negative): #Outputs line to a temp variable. Written to output file when input file is parsed
    global outputText
    indent = "*"*(nesting-nestingIncrement-negative-2)
    if indent != "":
        line = "%s %s\n" % (indent, line)
    elif negative == 2:
        line = "=== %s ===\n" %line
    else:
        line = "'''%s'''\n" %line
    if specificFile != "no":
        print(line)
    outputText.append(line)

modFilePattern = re.compile(r"replace_path\s*=\s*\"(.*)\"")
def getReplacedFolders(modDirPath, modName):
    replacedFolders = []
    if not (modDirPath and modName):
        return replacedFolders
    with open('%s/%s.mod' % (modDirPath, modName)) as modFile:
        for line in modFile.readlines():
            match = re.search(modFilePattern, line)
            if match:
                replacedFolders.append(match.group(1))
    return replacedFolders

def getFilesToSkip(files):
    return [s.strip() + ".txt" for s in files.split(";")]


if __name__ == "__main__":
    import cProfile, pstats
    pr = cProfile.Profile()
    pr.enable()

    from common import * #Various functions shared with the countryParser
    import time #Used for timing the parser
    start = time.clock()
    import re #Needed for various string handling
    import os #Used to grab the list of files
    settings = readStatements("settings")
    path = settings["path"].replace("\\", "/")
    modDirPath = settings["modDirPath"].replace("\\", "/")
    modName = settings["modName"]
    replacedFolders = getReplacedFolders(modDirPath,modName)
    filesToSkip = getFilesToSkip(settings["filesToSkip"])
    folder = settings["folder"]
    specificFile = settings["file"]
    if folder == "decisions":
        nesting, nestingIncrement = 0, 0
    elif folder == "missions" or folder == "events":
        nesting, nestingIncrement = 1, 0 #One less level of irrelevant nesting

    #Dictionaries of known statements
    special = readStatements("statements/special")
    statements = readStatements("statements/statements")
    exceptions = readStatements("statements/exceptions")

    def getModPath():
        return "%s/%s" % (modDirPath, modName)

    def useMod():
        return modDirPath and modName

    def getPath():
        if modName and modDirPath:
            return getModPath()
        else:
            return path

    def notProvNameOrCountry(name):
        return not name.startswith("prov_names") and not name.startswith("countries")

    def isEnglishLocalization(name):
        return name.endswith("_l_english.yml")

    def acceptName(name):
        return notProvNameOrCountry(name) and isEnglishLocalization(name)


    try:
        #Dictionaries of relevant values
        provinces = readDefinitions("%s/localisation/prov_names_l_english.yml" % getPath())
        countries = readDefinitions("%s/localisation/countries_l_english.yml" % getPath())

        lookup = {}
        for fileName in [f for f in os.listdir("%s/localisation" % path) if acceptName(f)]:
            lookup.update(readDefinitions("%s/localisation/%s" % (path,fileName)))
        if useMod():
            for fileName in [f for f in os.listdir("%s/localisation" % getModPath()) if acceptName(f)]:
                lookup.update(readDefinitions("%s/localisation/%s" % (getModPath(),fileName)))


        eventModifiers = []
        for fileName in os.listdir("%s/common/event_modifiers" % path):
            with open("%s/common/event_modifiers/%s" % (path,fileName)) as f:
                for line in f.readlines():
                    if "#" in line:
                        line = line.split("#")[0]
                    if not re.match(r"\s+", line) and line != "":
                        eventModifiers.append(line)
        if useMod():
            for fileName in os.listdir("%s/common/event_modifiers" % getModPath()):
                with open("%s/common/event_modifiers/%s" % (getModPath(),fileName)) as f:
                    for line in f.readlines():
                        if "#" in line:
                            line = line.split("#")[0]
                        if not re.match(r"\s+", line) and line != "":
                            eventModifiers.append(line)


        if specificFile == "no":
            for fileName in os.listdir("%s/%s" % (path, folder)):
                if fileName not in filesToSkip and folder not in replacedFolders:
                    print("Parsing file %s/%s/%s" % (path, folder, fileName))
                    main(path, folder, fileName)
            if useMod():
                for fileName in os.listdir("%s/%s" % (getModPath(), folder)):
                    if fileName not in filesToSkip:
                        print("Parsing file %s/%s/%s" % (getModPath(), folder, fileName))
                        main(getModPath(), folder, fileName)
        else:
            fileName = specificFile+".txt"
            main(getPath(), folder, fileName)
    except FileNotFoundError as ex:
        print("File not found %s: Make sure you've set the file path in settings.txt" % ex.args)
    elapsed = time.clock() - start
    print("Parsing the files took %.3f seconds" %elapsed)
    pr.disable()
    sortby = 'tottime'
    ps = pstats.Stats(pr).sort_stats(sortby)
    ps.print_stats()
