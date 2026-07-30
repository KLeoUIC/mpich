# KLEO, 7/28/26
# Takes the source code and generates a description for each function.

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
    if doc == "freefilewiki":
        prompt = "Read through sections pretaining to "+func+" in 'src' and "+func+" section in 'doc/mansrc/funcnotes.txt'. If more context is needed look to 'doc/wiki'. Convert it to a concise documentation style semantic description for "+func+"."
    elif doc == "freeall":
        prompt = "Read through sections pretaining to "+func+" in 'src', "+func+" section in 'doc/mansrc/funcnotes.txt', and 'doc/mansrc/maint/mpi-standard'. If more context is needed look to 'doc/wiki'. Convert it to a concise documentation style semantic description for "+func+"."
    else:
        prompt = "Read through sections pretaining to "+func+" in 'src' and convert it to a concise documentation style semantic description for "+func+"."
    prompt += " The following is a list of traits of complex functions;\n- uses more than one communicator\n- involves more than one process\n- is more than a parameter checker and wrapper for the underlying MPID function\n- has threading/concurrency behavior\n- is collective\n- is nonlocal" \
    "If "+func+" has 0-2 traits get a <=6 sentence description, 3-4 traits a <=8 sentence description, and 5-6 traits a <=10 sentence description. During any of the following description do not; explain the parameters or their ranges, give the function signature, explain MPI_SUCESS return, extrapolate or interpret resources to complete checklist items, nor use run-on sentences.\nWrite a short summary sentence. On a new line write the following checklist items as one paragraph while continuing to follow the above rules and sentence limits. Only include list items if they are stated in the reference file if not exclude them silently." \
    "- when the function returns\n- wildcard, MPI constants, or values that cause errors\n- thread/concurrency\n- overtaking/non-overtaking\n- collective behavior\n- advice to users for building their own programs, do not use opinionated language such as 'prefer' or 'should' instead use 'may' or 'are recommended'\nOutput description to 'doc/mansrc/semantics.adoc' in Asciidoc format, with first usage of "+func+" bolded, parameters monospaced, bracketed by '//tag::"+func+"[]' and '//end::"+func+"[]'"

    if doc != None:
        start = time.perf_counter()
        subprocess.call("opencode --model 'argo/"+model+"' --format json > 'doc/mansrc/"+doc+"_"+model+"_"+func+".txt' run \""+prompt+"\"", shell=True)
        end = time.perf_counter()-start
        with open(path.join(getcwd(), "doc/mansrc/maint/"+doc+"_timing.csv"), "a") as out:
            out.write("\n"+doc+","+model+","+func+","+str(end))
    else: subprocess.call("opencode --model 'argo/"+model+"' run \""+prompt+"\"", shell=True)

def main():
    parser = argparse.ArgumentParser(prog='Argo semantic description generator', description='-u Argonne username\n-m Model name\n-f function names')
    parser.add_argument('-m', default='claudeopus45', type=str)
    parser.add_argument('-f', nargs='*', type=str)
    parser.add_argument('-d', type=str)
    argv = parser.parse_args()

    if argv.f == [] or argv.f == None: funcs = gatherFromApi()
    else: # user provided function list
        funcs = {}
        for elm in argv.f: funcs[elm] = set()

    for func in funcs:
        generateDescription(func, argv.m, argv.d)
    
                
if __name__ == "__main__":
    main()