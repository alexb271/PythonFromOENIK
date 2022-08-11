# PythonFromOENIK
Convert and run OE-NIK pseudocode

This is a small script that creates executable python code from what
was the official pseudocode used at OE-NIK on the Programming I. subject.

I've written this script so that I could practice writing algorhythms
in the same pseudocode that would be required on tests and exams while
being able to run and test the code that I'm practicing.

The script converts syntax and symbols specifically used in the OE-NIK
pseudocode to python and leaves everything else not recognized as
OE-NIK pseudocode unchanged. Therefore actual python can be freely
mixed with pseudocode.

To run OE-NIK pseudocode simply pass it as an argument while running
the script, such as:

python3 pyfromnik.py kivalasztas.txt

Use the -p flag to aslo print the converted python code before
execution. Use the -pn flag to only print the converted python
code without executing it.

I've included a few example pseudocode files in this repository.
Keep in mind that these example files have LF line endings.
