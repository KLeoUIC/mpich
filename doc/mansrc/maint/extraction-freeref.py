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
import time
import argparse

def gatherFromApi() -> set:
    funcMap = set()
    bindingDir = path.join(getcwd(), "src/binding/c")
    for entry in scandir(bindingDir):
        if re.compile(".*(_api\.txt)$").match(entry.name): 
            search = open(path.join(bindingDir, entry.name))
            for line in search:
                m = re.compile("(MPIX*_[aA-zZ0-9_]*)\:").search(line)
                if m and (m[1] not in funcMap):
                    funcMap.add(m[1])
            search.close()
    return funcMap
        
def generateDescription(func, model, doc) -> None:
    outPath = path.join(getcwd(), "doc/mansrc/maint/ai_prompt/workingPromptFreeRef.txt")
    if doc != None:
        start = time.perf_counter()
        subprocess.call("opencode --model 'argo/"+model+"' --format json > 'doc/mansrc/"+doc+"_"+model+"_"+func+".txt' run $(sed 's/FUNCTION/"+func+"/g' "+outPath+")", shell=True)
        end = time.perf_counter()-start
        with open(path.join(getcwd(), "doc/mansrc/maint/"+doc+"timing_.csv"), "a") as out:
            out.write("\n"+model+","+func+","+str(end))
    else:
        subprocess.call("opencode --model 'argo/"+model+"' run $(sed 's/FUNCTION/"+func+"/g' "+outPath+")", shell=True)

def main():
    parser = argparse.ArgumentParser(prog='Argo semantic description generator', description='-m Model name\n-f function names\n-d Name for documentation')
    parser.add_argument('-m', default='claudeopus45', type=str)
    parser.add_argument('-f', nargs='*', type=str)
    parser.add_argument('-d', type=str)
    argv = parser.parse_args()

    if argv.f == [] or argv.f == None: funcs = gatherFromApi()
    else: # user provided function list
        funcs = set()
        for elm in argv.f: funcs.add(elm)

    for func in funcs:
        generateDescription(func, argv.m, argv.d)
                
if __name__ == "__main__":
    main()