# KLEO, 7/9/26
# Gets 

import re
import subprocess
from os import path
from os import scandir
from os import getcwd
import random

cvarsMap = {}

def scanForCvar(folder:str):
    for entry in scandir(folder):
        if entry.is_dir(): scanForCvar(path.join(folder, entry.name))
        if re.compile(".*(\.c|\.h|\.txt)$").match(entry.name): 
            search = open(path.join(folder, entry.name))
            for line in search:
                m = re.compile("(MPIR_CVAR(_*[A-Z0-9])*)").search(line)
                n = re.compile("(MPIR_CVAR(_*[A-Z0-9])*)\(").search(line)
                if m and (not n):
                    if m[1] in cvarsMap: cvarsMap[m[1]].add(folder+"/"+entry.name)
                    else:
                        cvarsMap[m[1]] = set()
                        cvarsMap[m[1]].add(folder+"/"+entry.name)
            search.close()

def main():
    srcPath = path.join(getcwd(), "src")
    scanForCvar(srcPath)
    sample = random.sample(list(cvarsMap), 5)
    for entry in sample:
        readyString = "opencode --model 'argo/gpt55' run 'Read only through the following files"
        for file in cvarsMap[entry]: readyString += ", "+file
        readyString += " with focus on "+entry+". Use the reading to deterine if "+entry+" is an alternate name for another CVAR, if it is add 'Alternate name: "+entry+"' above the other CVARs function list, do not change anything else. If it is not an alternate name use the reading to inform a description of when "+entry+" is used, including if it relies on values of other CVARs or modes being active. What "+entry+" enables/sets -do not mention individual valid values here. After that then a list of valid values and what they enable or represent. Output, with existing formatting used on MPIR_CVAR_EXAMPLE, to 'doc/wiki/cvar.md', do not change remove MPIR_CVAR_EXAMPLE.'" 
        subprocess.call(readyString, shell = True)
                
if __name__ == "__main__":
    main()