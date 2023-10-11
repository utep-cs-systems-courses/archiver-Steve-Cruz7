#! /usr/bin/env python3

import sys #enables command line arguments
import os  #used for some file related stuff

"""
Changes to make: Program will not write new file itself, only output archived
version or unarchived version
Shell will be used to redirect that output so no need to make  an output file
"""
class BufferedFdReader:
    def __init__(self, fd, bufLen = 1024*16):
        self.fd = fd
        self.buf = b""
        self.index = 0
        self.bufLen = bufLen
    def readByte(self):
        if self.index >= len(self.buf):
            self.buf = os.read(self.fd, self.bufLen)
            self.index = 0
        if len(self.buf) == 0:
            return None
        else:
            retval = self.buf[self.index]
            self.index += 1
            return retval
    def close(self):
        os.close(self.fd)
        
class BufferedFdWriter:
    def __init__(self, fd, bufLen = 1024*16):
        self.fd = fd
        self.buf = bytearray(bufLen)
        self.index = 0
    def writeByte(self, bVal):
        self.buf[self.index] = bVal
        self.index += 1
        if self.index >= len(self.buf):
            self.flush()
    def flush(self):
        startIndex, endIndex = 0, self.index
        while startIndex < endIndex:
            nWritten = os.write(self.fd, self.buf[startIndex:endIndex])
            if nWritten == 0:
                os.write(2,f"buf.BufferedFdWriter(fd={self.fd}): flush failed\n".encode())
                sys.exit(1)
            startIndex += nWritten
        self.index = 0
    def close(self):
        self.flush()
        os.close(self.fd)

def bufferedCopy(byteReader, byteWriter):
    while (bv := byteReader.readByte()) is not None:
        byteWriter.writeByte(bv)
    byteWriter.flush()





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
    if (size == 0):
        return size
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
    buffWtr = BufferedFdWriter(1)
    for target in files:
        
        #opening file to read with file descriptor
        fd = os.open(target, os.O_RDONLY)
        #creating instances of buffered reader and writer
        buffRdr = BufferedFdReader(fd)

        
        #writing size of filename
        fileNameSize = EbitConversion(len(target)).encode()
        for byte in fileNameSize:
            buffWtr.writeByte(byte)
        
        #converting file name to a byte array and writing it to fd
        fileName = target.encode()
        for byte in fileName:
            buffWtr.writeByte(byte)

        #Finding size of file, representing in binary and writing it to fd
        targetFileSize = EbitConversion(os.path.getsize(target)).encode()
        for byte in targetFileSize:
            buffWtr.writeByte(byte)

        #create buffered reader to moderate reading, same for writing
        
        #Now that fileNameSize, fileName, and targetFileSize are written into buffer, we can just copy over file contents with Copy
        bufferedCopy(buffRdr, buffWtr)  

        #Repeat the process for the rest of the files
   # print("Flushing buffered writer to fd 1")
    buffWtr.flush()    
        
#this would be my deframer
#Moving onto extracting section
elif (command == "x"):
    for target in files:
        
        fd = os.open(target, os.O_RDONLY)
        while(True):
            nameSize = convertBack(os.read(fd, 8).decode())
            if(nameSize == 0): #this is checking to see if os.read reaches EoF
                break
            fileName = os.read(fd, nameSize).decode()
            #Not going to use buffered reader here because I know file name can only be up to 256 bytes max, and the 8 before I know are there

            #fd for target file
            fileName = os.open(fileName, os.O_WRONLY)
            

            fileSize = convertBack(os.read(fd, 8).decode())

            bytesRead = 0
            buffRdr = BufferedFdReader(fd)          #reading from target file
            buffWtr = BufferedFdWriter(fileName)    #writing to "new" file
            while (bytesRead < fileSize ):
                byte = buffRdr.readByte()
                buffWtr.writeByte(byte)
                bytesRead += 1
            buffWtr.flush()                 
    exit()


        
        
