import re
from Formats import RFormat, JFormat,IFormat
from register import Register
from Pipeline import Pipeline
from random import randint
import math

class Interpreter:
    
    def __init__(self):
        self.registers = {}   # Array of Register objects of size 32
        self.memory = [0]*100 # Memory
        self._initializeMemory() #filling memory with random numbers from 0 to 100
        self.compiled = None  # assembled File | to be initialized 
        self.executionOutput = None # file that will the carry executed file
        self.pipeline = None
        self.RForm = None     # to be initialized 
        self.JForm = None     # to be initiated 
        self.IForm = None     # to be initiated 

    def run(self,processFilename):
        
        self._adjust_registers()
        self._set_dummy_values()
        processFile = open(processFilename,mode = 'r')
        otpt_name = processFilename.replace(".txt","-output")
        self.executionOutput = open(f"{otpt_name}.txt",mode = 'w+')
        self.executionOutput.write("OUTPUT FILE\n")
        bin_name = processFilename.replace(".txt","-binary")
        self.compiled = open(f"{bin_name}.txt",mode = 'w+')
        self.compiled.write("BINARY FILE\n")
        self.RForm = RFormat(self.compiled,self.executionOutput)
        self.JForm = JFormat(self.compiled,self.executionOutput)
        self.IForm = IFormat(self.compiled,self.executionOutput)
        self.pipeline = Pipeline(processFilename)
        #looping over each command in the file
        mips = []
        for line in processFile:
            mips.append(self._parse(line))
        lengthOfCmds = len(mips)
        self.pipeline.setLength(lengthOfCmds)
        self.assemble(mips,processFile)
        print("All commands executed Successfully\nexecutionOutput file contains all the output values' emulation\nBinary file contains all the binary execution values")

        #Parsing file
    def _parse(self,line):
        return re.split('; |$ |, |\* |\s',line.replace('$', ''))

    #adjusting registers pt-1
    def _adjust_registers(self):
        # Register $zero
        self._set_regs("zero",0)
        # at $at
        self._set_regs("at",1)
        # $v
        self._set_regs('v0',2)
        self._set_regs('v1',3)
        # $a
        self._set_regs('a0', 4)
        self._set_regs('a1', 5)
        self._set_regs('a2', 6)
        self._set_regs('a3', 7)
        # $t
        self._set_regs('t0', 8)
        self._set_regs('t1', 9)
        self._set_regs('t2', 10)
        self._set_regs('t3', 11)
        self._set_regs('t4', 12)
        self._set_regs('t5', 13)
        self._set_regs('t6', 14)
        self._set_regs('t7', 15)
        # $s
        self._set_regs('s0', 16)
        self._set_regs('s1', 17)
        self._set_regs('s2', 18)
        self._set_regs('s3', 19)
        self._set_regs('s4', 20)
        self._set_regs('s5', 21)
        self._set_regs('s6', 22)
        self._set_regs('s7', 23)
        # $t
        self._set_regs('t8', 24)
        self._set_regs('t9', 25)
        # $k
        self._set_regs('k0', 26)
        self._set_regs('k1', 27)
        #$gp
        self.registers["gp"] = Register("gp")
        self.registers["gp"].binVal = self.registers["gp"].toBin(28)
        #$sp
        self.registers["sp"] = Register("sp")
        self.registers["sp"].binVal = self.registers["sp"].toBin(29)
        #$fp
        self.registers["fp"] = Register("fp")
        self.registers["fp"].binVal = self.registers["fp"].toBin(30)
        #$fp
        self.registers["ra"] = Register("ra")
        self.registers["ra"].binVal = self.registers["ra"].toBin(31)

    # adjusting registers pt-2
    def _set_regs(self,typeOfReg,i):
        self.registers[typeOfReg] = Register(typeOfReg)
        self.registers[typeOfReg].binVal = self.registers[typeOfReg].toBin(i)

    # setting values to 0
    def _set_dummy_values(self):
        for reg in self.registers.keys():
            self.registers[reg].value = 0

    #assembling file commands
    def assemble(self, mips,processFile):
        #labeling and storing index
        labels = {}
        for command in mips:
             if ':' in command[0]:
                label = command[0].replace(':', '')
                #adding label to dict
                labels[label] = mips.index(command)
                label_line = mips[mips.index(command)]
        print(labels)
        #Executing each command
        print(mips)
        for command in mips:
            if ':' not in command[0]:
                if command[0] in self.RForm.ops.keys():
                    self.RForm.assemble(command, self.registers)
                elif 'j' in command:
                    self._jump(mips,command,1,labels,processFile)
                    break
                elif command[0] in ['beq','bne']:
                    delta = (labels[command[3]] - mips.index(command))  #offset in bne command
                    if delta<0 :
                        delta = (labels[command[3]] - mips.index(command))-1
                    else:
                        delta = (labels[command[3]] - mips.index(command))-1
                    self.IForm.writeAssemblyComp(command,self.registers,delta)
                    decision = self.IForm.compareCompStatement(command,self.registers)
                    if command[0] == 'beq':
                        if decision:
                            self._jump(mips,command,3,labels,processFile)
                            break
                        else:
                            continue
                    elif command[0] == 'bne':
                        if not decision:
                            self._jump(mips,command,3,labels,processFile)
                            break
                        else:
                            continue
                elif command[0] in self.IForm.ops.keys():
                    self.IForm.assemble(command, self.registers, self.memory)
            else:
                if len(command)>1:
                    if command[1] in self.RForm.ops.keys():
                        self.RForm.assemble(command[1:], self.registers)
                    elif command[1] in self.IForm.ops.keys():
                        self.IForm.assemble( command[1:], self.registers, self.memory)
                    elif 'j' in command:
                        # getting index of the label (label line index-1)
                        self._jump(mips, command, 2, labels, processFile)
                        break
            cnt_idx = mips.index(command)
            if (cnt_idx <(self.pipeline.length-1)):
                self.pipeline.analyse(self.registers, command, mips[cnt_idx+1],self.memory)
            else:
                self.pipeline.analyse(self.registers, command, None,self.memory)
    
    #jump command
    def _jump(self,mips,command,cmd_start_idx,labels,processFile):
        target_label_idx = labels[command[cmd_start_idx]]   #getting index of the label (label line index-1)
        self.pipeline.setLength(len(mips[(target_label_idx):]))
        self.JForm.assemble(target_label_idx)
        self.assemble(mips[(target_label_idx):],processFile)

    # setting memory with random numbers
    def _initializeMemory(self):
        size = len(self.memory)
        for i in range(size):
            self.memory[i] = 0
            #self.memory[i] = randint(0,100)
