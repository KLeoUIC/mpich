#!/bin/bash
models=("gpt54" "gpt55"  "claudeopus45" "claudesonnet46")
docs=("free" "content" "lengthNcontent")
# "gpt54" "gpt55"  "claudeopus45" "claudesonnet46"
for doc in "${docs[@]}"; do
    for f in "${models[@]}"; do
        python3 doc/mansrc/maint/extraction-allref.py -m $f -f MPI_T_category_get_cvars MPI_Win_sync MPI_Abi_get_fortran_booleans MPI_Send -d $doc

        cp doc/mansrc/semantics.adoc ~/$doc\_$f.adoc

        git restore doc/mansrc/semantics.adoc
    done
    mv doc/mansrc/maint/$doc\_timing.csv ~/$doc\_timing.csv
done
# sample functions: MPI_Send MPI_T_category_get_cvars MPI_Win_sync MPI_Abi_get_fortran_booleans
# models: gpt5 gpt54 gpt55 claudesonnet46 claudeopus45 gemini35flash