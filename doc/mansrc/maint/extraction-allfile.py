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

def gatherFromApi() -> dict:
    funcMap = {}
    bindingDir = path.join(getcwd(), "src/binding/c")
    for entry in scandir(bindingDir):
        if re.compile(".*(_api\.txt)$").match(entry.name): 
            search = open(path.join(bindingDir, entry.name))
            for line in search:
                m = re.compile("(MPIX*_[aA-zZ0-9_]*)\:").search(line)
                if m and (m[1] not in funcMap):
                    funcMap[m[1]] = set()
            search.close()
    return funcMap

def scanForFunc(folder:str, funcs:dict):
    for entry in scandir(path.join(getcwd(), folder)):
        if entry.is_dir(): scanForFunc(path.join(folder, entry.name), funcs)
        if re.compile(".*(\.c|\.h)$").match(entry.name): 
            search = open(path.join(folder, entry.name))
            for line in search:
                m = re.compile("(MPIX*_[aA-zZ0-9_]*)\(").search(line)
                if m and m[1] in funcs:
                    funcs[m[1]].add(path.join(folder, entry.name))
            search.close()

def generateDescription(funcs, model, doc) -> None:
    for func in funcs:
        if funcs[func] != None and len(funcs[func]) != 0:
            prompt = "Read through all of "
            for source in funcs[func]:
                prompt += source + ", "
            prompt = prompt + "and convert it to a concise documentation style semantic description for "+func+". The following is a list of traits of complex functions;\n- uses more than one communicator\n- involves more than one process\n- is more than a parameter checker and wrapper for the underlying MPID function\n- has threading/concurrency behavior\n- is collective\n- is nonlocal" \
            "If "+func+" has 0-2 traits get a <=6 sentence description, 3-4 traits a <=8 sentence description, and 5-6 traits a <=10 sentence description. During any of the following description do not; explain the parameters or their ranges, give the function signature, explain MPI_SUCESS return, extrapolate or interpret resources to complete checklist items, nor use run-on sentences.\nWrite a short summary sentence. On a new line write the following checklist items as one paragraph while continuing to follow the above rules and sentence limits. Only include list items if they are stated in the reference file if not exclude them silently." \
            "- when the function returns\n- wildcard, MPI constants, or values that cause errors\n- thread/concurrency\n- overtaking/non-overtaking\n- collective behavior\n- advice to users for building their own programs, do not use opinionated language such as 'prefer' or 'should' instead use 'may' or 'are recommended'\nOutput description to 'doc/mansrc/semantics.adoc' in Asciidoc format, with first usage of FUNCTION bolded, parameters monospaced, bracketed by '//tag::"+func+"[]' and '//end::"+func+"[]'"

            if doc != None:
                start = time.perf_counter()
                subprocess.call("opencode --model 'argo/"+model+"' --format json > 'doc/mansrc/"+doc+"_"+model+"_"+func+".txt' run \""+prompt+"\"", shell=True)
                end = time.perf_counter()-start
                with open(path.join(getcwd(), "doc/mansrc/maint/docdoc.csv"), "a") as out:
                    out.write("\n"+doc+","+model+","+func+","+str(end))
            else: subprocess.call("opencode --model 'argo/"+model+"' run \""+prompt+"\"", shell=True)

def main():
    parser = argparse.ArgumentParser(prog='Argo semantic description generator', description='-u Argonne username\n-m Model name\n-f function names')
    parser.add_argument('-m', default='claudeopus45', type=str)
    parser.add_argument('-f', nargs='*', type=str)
    parser.add_argument('-d', type=str)
    argv = parser.parse_args()
    model = argv.m

    if argv.f == [] or argv.f == None: funcs = gatherFromApi()
    else: # user provided function list
        funcs = {}
        for elm in argv.f: funcs[elm] = set()

    scanForFunc("src", funcs)
    generateDescription(funcs, model, argv.d)
    
                
if __name__ == "__main__":
    main()