#!/usr/bin/env python3

from _io import BufferedReader
import sys

help_text = """Usage: %s [--decode] [--delim [DELIMINATOR]] [-neh] FILE

Either encodes or decodes the file into or out of binary represented in ASCII.
When FILE is not specified, it defaults to STDIN.

    -d  --decode                    Decodes the text from file.
        --delim DELIMINATOR         When encoding, this inserts a specified 
                                    deliminator between each encoded byte.
    -n  --newline-interval NUM      Prints a newline every NUM encoded bytes.
    -e  --exclude-newlines          Makes it so that it doesn't print new lines
                                    every five bytes and at the end. Overrides
                                    the -n argument.
    -h  --help                      Prints this message.
""" % sys.argv[0].split("/")[-1]

def print_help(code: int):
    sys.stderr.write(help_text)
    exit(code)

# Eat a dick argparse
def parse_args() -> (int, bool, bool, str, str):
    args = sys.argv[1:]

    delim = None
    file = None
    interval = 8

    flags = [False, False, False, False, False]
    delim_last_arg = False
    num_last_arg = False
    for arg in args:
        if arg[:1] == "-":
            if arg == "--help" or arg == "-h":
                print_help(0)
            if delim_last_arg:
                print_help(1)
            elif (arg == "--decode" or arg == "-d") and not flags[0]:
                flags[0] = True
            elif (arg == "--newline-interval" or arg == "-n") and not flags[4]:
                flags[4] = True
                num_last_arg = True
            elif (arg == "--exclude-newlines" or arg == "-e") and not flags[3]:
                flags[3] = True
            elif arg == "--delim" and not flags[1]:
                flags[1] = True
                delim_last_arg = True
            else:
                print_help(1)
            continue
        if delim_last_arg:
            delim_last_arg = False
            delim = arg
        if num_last_arg:
            num_last_arg = False
            try:
                interval = int(arg)
            except ValueError:
                print_help(1)
            if interval < 1:
                print_help(1)
        elif not flags[2]:
            flags[2] = True
            file = arg
        else:
            print_help(1)
    return interval, flags[3], flags[0], delim, file 

def encode(file: BufferedReader, delim: str, exclude_nl: bool, interval: int) -> str:
    text = None
    try:
        text = file.read()
    except KeyboardInterrupt:
        print()
        exit(2)
    ret = ""
    for index, char in enumerate(text):
        if index != 0 and index % interval == 0 and not exclude_nl:
            ret += "\n"
        binary = bin(char)[2:]
        while len(binary) != 8:
            binary = "0" + binary
        if index != len(text) - 1:
            binary += delim
        ret += binary
    return ret

def decode_byte(byte: str) -> str:
    if len(byte) != 8:
        raise IndexError

    num = 0
    for power, bit in enumerate(byte):
        if bit == "0":
            continue
        num += 2 ** (7 - power)
    return num.to_bytes(1, byteorder="big")

def decode(file: BufferedReader) -> bytes:
    binary = None
    try:
        binary = file.read()
    except KeyboardInterrupt:
        print()
        exit(2)

    decoded = b""
    char = ""
    for bit in binary:
        bit = chr(bit)
        if bit == "0" or bit == "1":
            char += bit

        if len(char) == 8:
            decoded += decode_byte(char)
            char = ""
    if char != "":
        while len(char) != 8:
            char += "0"
        decoded += decode_byte(char)
    return decoded

def main():
    interval, exclude_nl, dec, delim, fpath = parse_args()
    
    file = None
    if fpath == None:
        file = sys.stdin.buffer
    else:
        file = open(fpath, "rb")

    if delim == None:
        delim = " "
    
    if dec:
        text = decode(file)
        sys.stdout.buffer.write(text)
    else:
        text = encode(file, delim, exclude_nl, interval)
        if not exclude_nl:
            print(text)
        else:
            print(text, end="")


if __name__ == "__main__":
    main()
