#! /usr/bin/env python3

import sys #enables command line arguments
import os  #used for some file related stuff

"""
Changes to make: Program will not write new file itself, only output archived
version or unarchived version
Shell will be used to redirect that output so no need to make  an output file
"""
def EbitConversion(size):
    binary = ""
    divisor = 128
    while (divisor > 0):
        if (size - divisor > -1):
            size = size - divisor
            binary += "1"
        else:
            binary += "0"
        divisor = divisor//2
    return binary

def convertBack(size):
    total = 0
    convert = 128
    for character in size:
        if (character == "1"):
            total += convert
        convert = convert//2
    return total
        
        
#setting up files
if len(sys.argv) < 2:
    print("Corrext usage: mytar.py c/x < target file> <target file>")
    exit()

command = sys.argv[1]
sys.argv.pop(0)
sys.argv.pop(0)
files = []
for arg in sys.argv:
    files.append(arg)

#checking if files exist
for target in files:
    if not os.path.exists(target):
        print("Target File: %s does not exist! Exiting...", target)
        exit()
    

#this if statement would be my framer
#create will be writing to file descriptor 1
if (command == "c"):
    for target in files:
        
        #opening file to read
        fd = os.open(target, os.O_RDONLY)
        
        #writing size of filename
        size = EbitConversion(len(target))
        os.write(1, size.encode())
        
        #converting file name to a byte array and writing it to fd
        os.write(1, target.encode())

        #Finding size of file, representing in binary and writing it to fd
        targetFileSize = os.path.getsize(target)
        os.write(1, EbitConversion(targetFileSize).encode())
        
        #writing targetFile in byte array form to fd
        #make loop to go through file and read in segments of bites
        targetInBytes = os.read(fd, targetFileSize)
        os.write(1, targetInBytes)  

        #Repeat the process for the rest of the files

        
#this would be my deframer
#Moving onto extracting section

elif (command == "x"):
    for target in files:
        fd = os.open(target, os.O_RDONLY)
        nameSize = convertBack(os.read(fd, 8))
        fileName = os.read(fd, nameSize)

        fileSize = convertBack(os.read(fd, 8))
        fileContents = os.read(fd, fileSize)
        os.write(1, fileName)
        os.write(1, fileContents)
                               
    exit()


        
        
