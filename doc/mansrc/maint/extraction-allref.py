# KLEO, 6/18/26
# Takes the Latex format of the MPI standard and sorts into all references to each function, printed to text files.
# NOTE: Run from outside the mpi-standard latex folder.
#       This works with the current (MPI-5.0) formating of the MPI Standard as it relies on the Latex tags and chapter 
#       naming conventions. If naming formatting is changed this file will need to be changed. 
# NOTE: Functions that are depreciated with clear replacements are omitted from generation.
#       Including: MPI_Address, MPI_Type_struct, MPI_Errhandler_create, MPI_Type_ub, MPI_Type_hvector, MPI_Type_extent, MPI_Type_lb, MPI_Type_hindexed, MPI_Errhandler_get, MPI_Errhandler_set

import re
import subprocess
from os import path
from os import scandir
from os import getcwd
from os import remove
import time
import argparse

chapterPattern = re.compile("chap-")
subsectionPattern = re.compile("(\\\label\{subsec:)|(\\\label\{sec:)")

# Removes: advice for implimentors, tables, examples, comments, and non-section lables 
excludeStart = re.compile("(begin\{implementors\})|(begin\{table\})|(begin\{example\})")
excludeEnd = re.compile("(end\{implementors\})|(end\{table\})|(end\{example\})")
oneLineExclude = re.compile("(\\\mpitermtitleindex\{)|(\%\%)|(\\\label\{)|(\\\subsection\{)|(\\\section\{)")

def scanChapter(chapPath, funcs, model, doc) -> None:
    with open(chapPath, "r") as chap: 
        subsectionHeader = ""
        subMap = {} # map name of sub/sections onto their content
        funcMap ={} # map name of functions onto their sub/sections
        collecting = False
        omitting = False
        nextLineFunc = False
        for line in chap:
            decl = re.compile('(\s)*function_name\(').match(line)
            sub = subsectionPattern.match(line)
            if decl != None or nextLineFunc: 
                function = re.compile('[\"\']\s*(MPI_[aA-zZ0-9_]*(?<!function)(?<!FN))[\"\']').search(line)
                if function == None:
                    nextLineFunc = True
                else:
                    nextLineFunc = False
                    if (function[1] in funcs) | (funcs == None):
                        funcMap[function[1]] = []
            elif excludeStart.search(line) != None: omitting = True
            elif excludeEnd.search(line) != None: omitting = False
            elif sub != None:
                subsectionHeader = line[sub.end():-2]
                subMap[subsectionHeader] = ""
                collecting = True
            else:
                if collecting and (omitting == False) and oneLineExclude.match(line) == None: subMap[subsectionHeader] += line
        # Associate subsections with functions in chapter
        for func in funcMap:
            temp = re.sub("_", "\_", func)
            funcName = re.compile("[("+temp+")|(\{"+temp+"\})]", re.IGNORECASE)
            for subsection in subMap:
                if funcName.search(subMap[subsection]) != None:
                    funcMap[func].append(subsection)
        generateDescription(funcMap, subMap, model, doc)
        
def generateDescription(funcMap, subMap, model, doc) -> None:
    outPath = path.join(getcwd(), "doc/mansrc/maint/ai_prompt/workingPrompt.txt")
    for func in funcMap:
        with open("doc/mansrc/maint/"+func+"_Extracted.txt", "w+") as out:
            for sec in funcMap[func]:
                out.write(subMap[sec])
        if doc != None:
            start = time.perf_counter()
            subprocess.call("opencode --model 'argo/"+model+"' --format json > 'doc/mansrc/"+doc+"_"+model+"_"+func+".txt' run $(sed 's/FUNCTION/"+func+"/g' "+outPath+")", shell=True)
            end = time.perf_counter()-start
            with open(path.join(getcwd(), "doc/mansrc/maint/docdoc.csv"), "a") as out:
                out.write("\n"+model+","+func+","+str(end))
        else:
            subprocess.call("opencode --model 'argo/"+model+"' run $(sed 's/FUNCTION/"+func+"/g' "+outPath+")", shell=True)
        remove("doc/mansrc/maint/"+func+"_Extracted.txt")

def getMPIX(funcs, model, doc):
    src = path.join(getcwd(), "src/binding/c")
    for entry in scandir(src):
        if re.compile("(.*)_api.txt").match(entry.name): 
            with open(path.join(src, entry)) as sect:
                for line in sect:
                    func = re.compile("(MPIX_.*):").match(line)
                    if func and ((func[1] in funcs)|(funcs==None)): 
                        mpixPrompt = path.join(getcwd(), "doc/mansrc/maint/ai_prompt/mpixPrompt.txt")
                        if doc != None:
                            start = time.perf_counter()
                            subprocess.call("opencode --model 'argo/"+model+"' --format json > 'doc/mansrc/"+doc+"_"+model+"_"+func+".txt' run $(sed 's/FUNCTION/"+func[1]+"/g' "+mpixPrompt+")", shell=True)
                            end = time.perf_counter()-start
                            with open(path.join(getcwd(), "doc/mansrc/maint/docdoc.csv"), "a") as out:
                                out.write("\n"+doc+","+model+","+func+","+str(end))
                        else:
                            subprocess.call("opencode --model 'argo/"+model+"' run $(sed 's/FUNCTION/"+func[1]+"/g' "+mpixPrompt+")", shell=True)

def main():
    parser = argparse.ArgumentParser(prog='Argo semantic description generator', description='-m Model name\n-f function names\n-d Name for documentation')
    parser.add_argument('-m', default='claudeopus45', type=str)
    parser.add_argument('-f', nargs='*', type=str)
    parser.add_argument('-d', type=str)
    argv = parser.parse_args()
    model = argv.m
    funcs = set()
    for elm in argv.f: funcs.add(elm)

    # Scan whole latex folder for chapters, get un-rendered version and scan
    rootPath = path.join(getcwd(), "doc/mansrc/maint/mpi-standard")
    for entry in scandir(rootPath):
        if chapterPattern.match(entry.name) != None:
            for file in scandir(rootPath+"/"+entry.name):
                namePattern = re.compile("("+entry.name[5:]+"(-2)*.tex)|(prof.tex)|(mpit.tex)")
                if namePattern.match(file.name):
                    chapterPath = path.join(rootPath, entry.name+"/"+file.name)
                    scanChapter(chapterPath, funcs, model, argv.d)
    # getMPIX(funcs, model, argv.d)
                
if __name__ == "__main__":
    main()