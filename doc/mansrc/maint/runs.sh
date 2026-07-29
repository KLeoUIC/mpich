#!/bin/bash
python3 doc/mansrc/maint/extraction-allref.py -m gpt54 -f MPI_Send MPI_T_category_get_cvars MPI_Win_sync MPI_Abi_get_fortran_booleans -d compNimp

cp doc/mansrc/semantics.adoc ~/compNimp_gpt54.adoc

# sample functions: MPI_Send MPI_T_category_get_cvars MPI_Win_sync MPI_Abi_get_fortran_booleans
# models: gpt5 gpt54 gpt55 claudesonnet46 claudeopus45 gemini35flash