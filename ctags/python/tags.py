#!/usr/bin/python3

# author Aria Poutanen
#

import sys
import subprocess
import linecache

types = ["prototype", "function", "class", "macro", "member", "method", "field", "constant", "package", "label", "namespace", "define", "type", "enumerator", "subroutine", "struct", "typedef", "enum", "union", "variable"]

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print("tags.py <filename> <outputfile*>")
    exit()

filename = sys.argv[1]
if (filename == '--language=C'):
   filename = sys.argv[2]

sys.stderr.write(f"Tokenizing {filename}\n")

if len(sys.argv) >= 4:
    sys.stdout = open(sys.argv[2], 'w')

output = subprocess.run(['ctags', "--language-force=C", '-x', '--c-kinds=+p', filename], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
arr = []

for line in output:

    line = line.split()

    if len(line) < 5:
        # end of ctags output
        break

    name = line[0]
    token_type = line[1]
    line_num = line[2]
    file_name = line[3]
    decl = " ".join(line[4:])

    # check types
    if token_type not in types:
        sys.stderr.write(f"illegal type {token_type} in {name}")
        exit (1)

    # each line is now of the formal [function name, type, line number, file, declaration]
    # inspect declaration to see if it is truncated or not

    stack = []
    eol = False;
    parens = False;
    for char in decl:
        if char == '(':
            parens = True;
            stack.append(char)
        elif char == ')':
            if len(stack) > 0:
                stack.pop()
            else:
                print("Unmatched braces in function declaration")
                exit(1)
        elif char == ';':
            eol = True;

    if ((token_type == 'function') or (token_type == 'prototype')) and ((len(stack) > 0) or (not parens and not eol)):
        # need to search in file for full function decl
        lines = []
        with open(file_name, encoding='ISO-8859-1') as f:
            lines = f.readlines()
        loop = True
        i = 0
        while(loop):
            if i > 100000:
                # we don't want infinite recursion
                break
            next_line = lines[int(line_num)+i]
            for char in next_line:
                if (char == ';') or (char == '{'):
                    loop = False
                    break
                else:
                    decl = decl + char
            i = i+1

        # replace tabs and whitespace
        decl = decl.replace('\t','')
        decl = " ".join(decl.split())

    print_decl = "";

    if token_type == "variable" or token_type == "macro":
        # normally we would consider macros, but we are only looking at functions or prototypes for this case
        # note to update this for script reuse
        print_decl = name;
    else:
       #print_decl = decl[decl.find(name):]
        print_decl = decl

    arr.append(f"DECL|{name}|{token_type}|{print_decl}")

print('\n'.join(sorted(arr)))
