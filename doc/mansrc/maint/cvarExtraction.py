# KLEO, 7/9/26
# Gets 

import re
import subprocess
from os import path
from os import scandir
from os import getcwd
from os import remove
import time

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
                        print(m[1])
            search.close()

def main():
    srcPath = path.join(getcwd(), "src")
    scanForCvar(srcPath)
    for entry in cvarsMap:
        readyString = "opencode --model 'argo/claudeopus45' run 'Read only through the following files"
        for file in cvarsMap[entry]: readyString += ", "+file
        readyString += " with focus on "+entry+". Use the reading to inform a description of when "+entry+" is used and what "+entry+" enables/sets. After that a list of valid values and what they enable. Output, with existing formatting used on MPIR_CVAR_EXAMPLE, to 'doc/wiki/cvar.md', reread and remove redundant information.'" 
        subprocess.call(readyString, shell = True)
                
if __name__ == "__main__":
    main()