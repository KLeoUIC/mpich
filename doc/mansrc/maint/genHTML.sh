#!/bin/bash

cd doc/mansrc/binding

for f in *.adoc; do asciidoctor $f; done