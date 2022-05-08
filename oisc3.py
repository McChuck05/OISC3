#!/usr/bin/env python3
# OISC:3 master program
# Copyright (C) 2022 McChuck
# Released under GNU General Public License
# See LICENSE for more details.
# Many thanks to Lawrence Woodman for inspiration and examples.
# Check out         https://techtinkering.com/articles/subleq-a-one-instruction-set-computer/
# And especially    https://techtinkering.com/2009/05/15/improving-the-standard-subleq-oisc-architecture/
# And maybe watch   https://www.youtube.com/watch?v=FvwcRaE9yxc

import sys
import os
from oisc3_parser import Parser
from oisc3_vm import Oisc3VM
try:
    from getch import getch, getche         # Linux
except ImportError:
    from msvcrt import getch, getche        # Windows


def Write_o3c(o3c_file, mem, neg0):
    count = 0
    maxpc = len(mem)
    neg = False
    if neg0 > 0:
        printneg = mem[neg0:]
        printneg.reverse()
        printmem = mem[:neg0]
        printmem.extend(printneg)
    for pc in range(maxpc):
        if pc == neg0 and pc != 0:
            o3c_file.write("\n% --NEGATIVE--: --NEGATIVE-- \n\n")
            neg = True
        a = printmem[pc]
        o3c_file.write('{} '.format(a))
        count += 1
        if count == 3:
            o3c_file.write("\n")
            count = 0
    o3c_file.write("\n")



def Oisc3(args):
    try:
        o3a_name = args[0]
        o3c_name = None
        if len(args) == 2:
            o3c_name = args[1]
        parser = Parser()
        vm = Oisc3VM()
        mem = []
        with open(o3a_name, "r") as o3a_file:
            raw = o3a_file.read()
            mem, neg0 = parser.parse(raw)
            o3a_file.close()
        if  o3c_name != None:
            with open(o3c_name, "w") as o3c_file:
                Write_o3c(o3c_file, mem, neg0)
                o3c_file.close()
        vm.do_vm(mem, neg0)
    except(ValueError, IndexError):
        print("I just don't know what went wrong!\n")
        o3a_file.close()

def main(args):
    try:
        print()
        if len(args) == 1:
            Oisc3(args)
        elif len(args) == 2:
            if os.path.isfile(args[1]):
                print(args[1], "exists.  Overwrite? ", end="", flush=True)
                answer = getche()
                if answer in ["y", "Y"]:
                    print()
                    print(args[1], "replaced \n\n", flush=True)
                    Oisc3(args)
                else:
                    print()
                    print(args[1], "retained \n\n", flush=True)
                    Oisc3([args[0]])
            else:
                print("creating", args[1], "\n\n", flush=True)
                Oisc3(args)
        else:
            print("\nusage: python subleqp.py infile.sla [outfile.slc]\n")
    except FileNotFoundError:
        print("\n< *Peter_Lorre* >\nYou eediot!  What were you theenking?\nTry it again, but thees time with a valid file name!\n</ *Peter_Lorre* >\n")
        print("\nusage: python oisc3.py infile.o3a [outfile.o3c]\n")


if __name__ == '__main__':
    print("\nOISC:3 starting up.")
    try:
        main(sys.argv[1:])
    except IndexError:
        print("\nusage:  python oisc3.py infile [outfile]")
    finally:
        print("\nOISC:3 shutting down.\n")
