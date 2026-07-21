# Description generation
For all of the following description generations the `maint` folder will need to be placed in `doc/mansrc` and commands called from the top `mpich` directory.

MPI and MPIX semantic descriptions
-
Generates descriptions of MPI and MPIX functions for an audiance of users unfamiliar with details of MPI or for quick reference by more expirienced users. 

To generate whole new set of semantic descriptions follow all steps. There is an already generated set of definitions, to use those skip to step 5.

1) Install Opencode with model Claude Opus 4.5 through Argo API. On setup details for Opencode: 
https://anl.app.box.com/notes/1871610644419?s=hxc72dkm0a8mlmo7ownfl4ixwx6iu3ko

2) Place MPI Standard Repo Latex in mpich/doc/mansrc/maint named `mpi-standard`

    Note: Preprocessing for the models rely on Latex structural tags and cannot work with raw text as is. 

3) Insure `doc/mansrc/semantics.adoc` is empty of all tagged definitions.

4) Run `python3 doc/mansrc/maint/extraction.py` and `python3 doc/mansrc/maint/mpixExtraction.py`

5) Build as normal with `./autogen.sh --with-doc`

    Finished pages in Asciidoc format will be generated into `doc/mansrc/c`

Cvar descriptions
-
Generates descriptions of MPIR_CVAR variables for an audiance of users expirienced with MPI.

To generate a whole new set of Cvar descriptions follow all steps. There is an already generated set of descriptions in `doc/wiki/cvar.md`

1) Install Opencode with model Claude Opus 4.5 through Argo API. On setup details for Opencode: 
https://anl.app.box.com/notes/1871610644419?s=hxc72dkm0a8mlmo7ownfl4ixwx6iu3ko
