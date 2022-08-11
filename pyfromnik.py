#!/usr/local/bin/python3
#v1.0

def Translate():
    import re
    import sys

    #IF Branching Translation
    def IfBranch(code,i,command,tabCount):

        if command == "if":
            code[i] = re.sub("ha ", "if ", code[i])
            code[i] = re.sub(" akkor"," :", code[i])
            code[i] = tabCount*tab + code[i]
            return tabCount + 1

        elif command == "elif":
            code[i] = re.sub(r"k(u|ü)l(o|ö)nben ha", "elif", code[i])
            code[i] = re.sub("akkor",":", code[i])
            code[i] = (tabCount-1)*tab + code[i]
            return tabCount

        elif command == "else":
            code[i] = (tabCount-1)*tab + re.sub(r"k(u|ü)l(o|ö)nben","else:",code[i])
            return tabCount

        elif command == "close":
                    code[i] = ""
                    return tabCount - 1

    #FOR Loop Translation
    def ForLoop(code,i,command,tabCount,loopVarLst):

        if command == "open":

            #Getting for loop start and end values
            start = re.search(r"=[^\n]*-t(ő|o)l",code[i]).group()
            for j in range(len(start)):
                if start[j] == '-' and start[j+1] == 't':
                    break
            start = start[1:j]
            del j


            end = re.search(r"t(o|ő)l[^\n]*-ig",code[i]).group()
            for j in range(len(end)):
                if end[j] == '-' and end[j+1] == 'i':
                    break
            end = end[3:j]
            del j

            #find loop variable name
            loopVarName = re.search(r"ciklus \w*",code[i]).group()
            loopVarName = loopVarName[6:].lstrip()
            loopVarLst.append(loopVarName)

            #Writing code for automatic detection of ascending/descending indexing
            code[i] = (tabCount*tab+ "___ = ({0})-({1})\n".format(end,start) + tabCount*tab +
            "if ___ >= 0:\n" + (tabCount+1)*tab + "___ = 1\n" + tabCount*tab + "else:\n" +
            (tabCount+1)*tab + "___ = -1\n")

            #Writing the beginning of the for loop
            code[i] = code[i] +tabCount*tab + "for {0} in range({1},{2},{3}):\n".format(
                      loopVarName,start,end+"+"+"___","___")

            return tabCount + 1

        elif command == "close":
            tabCount -= 1
            varName = loopVarLst[len(loopVarLst)-1]
            code[i] = tabCount*tab+ "del {0}\n".format(varName)
            del loopVarLst[len(loopVarLst)-1]
            if len(loopVarLst) == 0:
                code[i] = code[i] + tabCount*tab + "___ = 0; del ___\n"
            return tabCount

    #WHILE Loop Translation
    def WhileLoop(code,i,command,tabCount):

        if command == "open":
            code[i] = re.sub(r"ciklus am(i|í)g",tabCount*tab+"while",code[i])[:-1]+":\n"
            return tabCount + 1

        elif command == "close":
            code[i] = ""
            return tabCount - 1

    #DO-WHILE Loop Translation
    def DoWhileLoop(code,i,command,tabCount):

        if command == "open":
            code[i] = tabCount*tab + "while True:\n"
            return tabCount + 1

        elif command == "close":
            code[i] = code[i].rstrip()
            condition = code[i][re.search(r"am(i|í)g ",code[i]).end():]
            code[i] = tabCount*tab + "if not (" + condition + "):\n" + (tabCount+1)*tab + "break\n"
            return tabCount - 1

    #Function Declaration
    def FuncDef(code,i,command,tabCount):

        if command == "open":
            code[i] = re.sub(r"^\w* ","def ",code[i]).rstrip()+":\n"
            return tabCount + 1

        elif command == "close":
            code[i] = ""
            return tabCount - 1

    #Array Construction Translation
    def ArrayInit(code,i):

        varName = re.search(r"[\s]*[\w]*[\s]*<",code[i]).group()[:-1].lstrip().rstrip()

        code[i] = code[i].lower()
        varType = re.search(r"l(e|é)trehoz\([ \w]*\)",code[i]).group()
        #print(varType[9:])
        if "egesz" in varType or "egész" in varType:
            var = 0
        elif "logikai" in varType:
            var = False
        elif "t" in varType[9:]:
            var = 0

        size = re.search(r"\[[^\n]*\]",code[i]).group()[1:-1]

        code[i] = tabCount*tab + varName + "=[" + str(var) + "]*(" + str(size)+")\n"

    def InfiniteInArray(code,i):
        arrayName = re.search(r"\w*\[", code[i]).group()[:-1]
        if re.search(r"-\s*∞",code[i]):
            infinite = "[-9999999]"
        else:
            infinite = "[9999999]"
        code[i] = (tabCount*tab + "try:\n" + (tabCount+1)*tab + re.sub(r"∞","9999999",code[i])
        + tabCount*tab + "except IndexError:\n" + (tabCount+1)*tab + arrayName + " = " + arrayName +
        " + " + infinite + "\n")

    #The SWAP operator
    def Swap(code,i):
        firstVar = re.search(r"[\w \[\]\-+]*[ ]*\<",code[i]).group()[:-1].rstrip()
        secondVar = re.search(r">[ ]*[\w \[\]\-+]*",code[i]).group()[1:].lstrip()
        code[i] = (tabCount*tab + "___ = " + firstVar + "; " + firstVar +" = " + secondVar +
        "; " + secondVar + " = ___ ; del ___\n")

    ################
    ####  MAIN  ####
    ################

    #Program variables
    tab = "    "
    tabCount = 0
    loopVarLst = []
    lastLoop = []
    printOutput = False
    executeCode = True

    usageString = ("Usage: {0} [-pn] inputfile\n".format(sys.argv[0])+
    "       -p   Print translated python code\n"+
    "       -pn  No execute - print code only\n\n")

    #Initialization
    if len(sys.argv) < 2:
        sys.exit(usageString + "Error: No input file.")
    if len(sys.argv) > 3:
        sys.exit(usageString + "Error: Too many arguments given.")
    if len(sys.argv) > 2:
        filename = sys.argv[2]
        if sys.argv[1] == '-p' or sys.argv[1] == "-P":
            printOutput = True
        elif sys.argv[1] == "-pn" or sys.argv[1] == "-PN":
            printOutput = True
            executeCode = False
        else:
            sys.exit(usageString + "Error: Unrecognized flag '{0}' in command".format(sys.argv[1]))
    else:
        filename = sys.argv[1]

    #Opening the file
    try:
        file = open(filename,"r")
    except:
         sys.exit("Error opening file: {0}".format(filename))
    code = file.readlines()
    file.close

    #Remove leading whitespaces
    for i in range(len(code)):
        code[i] = code[i].lstrip()

    #Removing empty strings that remain after
    #stripping \n from lines that were a single \n character
    i = 0
    ln = len(code)
    while i < ln:
        if code[i] == "":
            del code[i]
            ln -= 1
        else:
            i += 1

    #Simple replacements
    for i in range(len(code)):
        if code[i][0] == "#":
            pass
        else:
            code[i] = re.sub("vissza","return",code[i])
            code[i] = re.sub("\^","and",code[i])
            code[i] = re.sub(" v "," or ",code[i])
            code[i] = re.sub("\¬","not ",code[i])
            code[i] = re.sub(" mod "," % ", code[i])
            code[i] = re.sub(r"(I|i)gaz", "True", code[i])
            code[i] = re.sub(r"(H|h)amis", "False", code[i])
            code[i] = re.sub("=/=", "!=", code[i])

            # Replacing = sign with ==
            if "=" in code[i]:
                tmplst = list(code[i])
                j = 0
                ln = len(tmplst)
                while j < ln:
                    if tmplst[j] == "=" and tmplst[j-1] != "<" and tmplst[j-1] != ">" and tmplst[j-1] != "!":
                        tmplst.insert(j,"=")
                        ln += 1
                        j += 1
                    j += 1
                code[i] = "".join(tmplst)

            # Replacing <- with =
            if not ("letrehoz" in code[i].lower() or "létrehoz" in code[i].lower() or "<->" in code[i]):
                code[i] = re.sub("<-","=",code[i])

            #Compensate array indexing
            cpos = 0
            while (re.search(r"\w*\[[ \w+\-\*\/%]*\]",code[i][cpos:]) and
            not re.search(r"l(e|é)trehoz",code[i].lower()) ):
                part = re.search(r"\w*\[[ \w+\-\*\/%]*\]",code[i][cpos:])
                temp = part.group()
                code[i] = code[i][:cpos+part.start()] + temp[:-1] + "-1]" + code[i][cpos+part.end():]
                cpos = cpos + part.end()


    #The Main Translator
    for i in range(len(code)):
        try:
            if code[i][0] == "#":
                code[i] = tabCount*tab + code[i]

            elif "emenet:" in code[i] or "imenet:" in code[i]:
                code[i] = "#"+code[i]

            elif "∞" in code[i]:
                if "[" in code[i] and "]" in code[i]:
                    InfiniteInArray(code,i)
                else:
                    code[i] = tabCount*tab + re.sub("∞","9999999",code[i])

            elif (("letrehoz" in code[i].lower() or "létrehoz" in code[i].lower())
            and "<-" in code[i]):
                ArrayInit(code,i)

            elif ( ("függvény" in code[i] or "fuggveny" in code[i]) and
            "vége" not in code[i] and "vege" not in code[i] ):
                tabCount = FuncDef(code,i,"open",tabCount)

            elif "függvény vége" in code[i] or "fuggveny vege" in code[i]:
                tabCount= FuncDef(code,i,"close",tabCount)

            elif re.match("^ha ", code[i]):
                tabCount = IfBranch(code,i,"if",tabCount)

            elif re.match(r"k(u|ü)l(o|ö)nben ha", code[i]):
                tabCount = IfBranch(code,i,"elif",tabCount)

            elif re.match(r"k(u|ü)l(o|ö)nben", code[i]):
                tabCount = IfBranch(code,i,"else", tabCount)

            elif "elágazás vége" in code[i] or "elagazas vege" in code[i]:
                tabCount = IfBranch(code,i,"close",tabCount)

            elif code[i].rstrip() == "ciklus":
                tabCount = DoWhileLoop(code,i,"open",tabCount)

            elif ("amig" in code[i] or "amíg" in code[i]) and "ciklus" not in code[i]:
                tabCount = DoWhileLoop(code,i,"close",tabCount)

            elif ( ("ciklus amig" in code[i] or "ciklus amíg" in code[i])
            and "vége" not in code[i] and "vege" not in code[i] ):
                tabCount = WhileLoop(code,i,"open",tabCount)
                lastLoop.append("while")

            elif "ciklus" in code[i] and "vége" not in code[i] and "vege" not in code[i]:
                tabCount = ForLoop(code,i,"open",tabCount,loopVarLst)
                lastLoop.append("for")

            elif "ciklus vége" in code[i] or "ciklus vege" in code[i]:
                if lastLoop[len(lastLoop)-1] == "for":
                    tabCount = ForLoop(code,i,"close",tabCount,loopVarLst)
                    del lastLoop[len(lastLoop)-1]
                elif lastLoop[len(lastLoop)-1] == "while":
                    tabCount = WhileLoop(code,i,"close",tabCount)
                    del lastLoop[len(lastLoop)-1]

            elif re.search(r"[\w\[\]]*[ ]*\<-\>[ ]*[\w\[\]]*",code[i]):
                Swap(code,i)

            else:
                code[i] = tabCount*tab + code[i]
        except:
            sys.exit("Error while translating pseudocode to python code.\n")

    #Compiling the code into a single string
    onestr = "".join(code)

    #Printing output
    if printOutput:
        linenr = 2
        print("1 ",end="")
        for i in range(len(onestr)):
            if i == len(onestr)-1:
                print("\n")
            elif onestr[i] == "\n":
                print("{0}{1} ".format(onestr[i], linenr),end="")
                linenr += 1
            else:
                print(onestr[i],end="")

    #Sending result based on whether code was set to execute
    if executeCode:
        return onestr
    else:
        return "pass"

#Executing code
exec("del Translate;" + Translate())
