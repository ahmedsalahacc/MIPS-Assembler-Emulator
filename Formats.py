class Parent:
    def convertToBvalue(self, intValue, fill_size):
        return bin(int(intValue))[2:].zfill(fill_size)

class RFormat(Parent):
    def __init__(self,destinationFile,executionOutput):
        """
        destinationFile File with binary code
        """
        self.destinationFile = destinationFile
        self.executionOutput = executionOutput
        self.ops = {
            'and': "100100",
            'or' : "100101",
            "add": '100000',
            "sub": '100010',
            'sll': "000000",
            'srl': "000010",
            'sra': "000011",
            'slt': "101010",
            'nor': "100111"
        }
        self.binary_format = {
            "funct": "000000",
            "shamt": "00000"
        }
    #Assmebler execution function
    def assemble(self,command_arr,registers):
        #binary format
        #add $d, $s, $t => 0000 00ss ssst tttt dddd d000 0010 0000
        reg_t = command_arr[3]
        reg_s = command_arr[2]
        reg_d = command_arr[1]
        cmd   = command_arr[0]
        reg_h = None
        if cmd not in ['srl','sra','sll']:
            self.destinationFile.write(f"{self.binary_format['funct']}{registers[reg_s].binVal}{registers[reg_t].binVal}{registers[reg_d].binVal}{self.binary_format['shamt']}{self.ops[cmd]}\n")
        else:
            #sll $d, $t, h => 0000 0000000 t tttt dddd dhhh hh00 0000
            reg_h = reg_t
            reg_t_1 = reg_s
            self.destinationFile.write(
                f"00000000000{registers[reg_t_1].binVal}{registers[reg_d].binVal}{self.convertToBvalue(int(reg_h),5)}{self.ops[cmd]}\n")
        #line execution
        if cmd == "and":
            registers[reg_d].value = (registers[reg_s].value & registers[reg_t].value)
            self.executionOutput.write(f"{self.convertToBvalue(registers[reg_s].value,32)} {cmd} {self.convertToBvalue(registers[reg_t].value,32)}  = {self.convertToBvalue(registers[reg_d].value,32)}\n")
        elif cmd == "or":
            registers[reg_d].value = (registers[reg_s].value | registers[reg_t].value)
            self.executionOutput.write(f"{self.convertToBvalue(registers[reg_s].value,32)} {cmd} {self.convertToBvalue(registers[reg_t].value,32)}  = {self.convertToBvalue(registers[reg_d].value,32)}\n")
        elif cmd == "add":
            registers[reg_d].value = registers[reg_s].value + registers[reg_t].value
        elif cmd == "sub":
            registers[reg_d].value = registers[reg_s].value - registers[reg_t].value
        elif cmd == "slt":
            registers[reg_d].value = registers[reg_s].value < registers[reg_t].value
        elif (cmd == 'sll'):
            registers[reg_d].value = (self.convertToBvalue(registers[reg_s].value,5).lstrip("0") + "0"*int(reg_h)).zfill(32)
            self.executionOutput.write(
                f"{self.convertToBvalue(registers[reg_s].value,32)} {cmd} {reg_h}  = {registers[reg_d].value}\n")
            registers[reg_d].value = int(registers[reg_d].value, 2)
        elif (cmd == 'srl'):
            registers[reg_d].value = (self.convertToBvalue(registers[reg_s].value,5)[:-int(reg_h)]).zfill(32)
            self.executionOutput.write(f"{self.convertToBvalue(registers[reg_s].value,32)} {cmd} {reg_h}  = {registers[reg_d].value}\n")
            registers[reg_d].value = int(registers[reg_d].value,2)
        elif (cmd == 'sra'):
            rsbval = self.convertToBvalue(registers[reg_s].value,5)
            registers[reg_d].value = rsbval.zfill(32)[0]*(int(reg_h)) + (rsbval[:-int(reg_h)]).zfill(32-int(reg_h))
            self.executionOutput.write(
                f"{self.convertToBvalue(registers[reg_s].value,32)} {cmd} {reg_h}  = {registers[reg_d].value}\n")
            registers[reg_d].value = int(registers[reg_d].value, 2)
        elif (cmd == 'nor'):
            registers[reg_d].value = bin((registers[reg_s].value | registers[reg_t].value) ^ 0b11111111111111111111111111111111)[2:]
            self.executionOutput.write(f"{self.convertToBvalue(registers[reg_s].value,32)} {cmd} {self.convertToBvalue(registers[reg_t].value,32)}  = {registers[reg_d].value}\n")
            registers[reg_d].value = int(registers[reg_d].value, 2)
            #registers[reg_d].value = self.convertToBvalue(((registers[reg_s].value|registers[reg_t].value) ^ 31), 5)
        if cmd not in ['srl','sra','sll','nor','and','or']:
            self.executionOutput.write(f"{registers[reg_s].value} {cmd} {registers[reg_t].value}  = {registers[reg_d].value}\n")
            #self.executionOutput.write(f"{self.convertToBvalue(registers[reg_s].value,32)} {cmd} {self.convertToBvalue(registers[reg_t].value,32)}  = {self.convertToBvalue(registers[reg_d].value,32)}\n")

class JFormat(Parent):
    def __init__(self, destinationFile, executionOutput):
        """
        destinationFile: File with binary code
        """
        self.destinationFile = destinationFile
        self.executionOutput = executionOutput
        self.op = "000010"

    def assemble(self,target_idx):
        self.destinationFile.write(f"{self.op}{self.convertToBvalue(target_idx,26)} \n")

class IFormat(Parent):
    def __init__(self,destinationFile,executionOutput):
        """
        destination : destination file to write
        """
        self.destinationFile = destinationFile
        self.executionOutput = executionOutput
        self.ops = {
            'beq': "000100",
            'bne': "000101",
            'addi': "001000",
            'andi': "001100",
            'ori': "001101",
            'slti': "001010",
            'lui': "001111",
            'lw': "100011",
            'sw': "101011" 
        }

    #for beq and bne commands
    def compareCompStatement(self,command,registers):
        #beq $s, $t, offset
        #0001 00ss ssst tttt iiii iiii iiii iiii
        if command[0] =='beq' or command[0] =='bne':
            return float(registers[command[1]].value) == float(registers[command[2]].value)
        else:
            raise ValueError("No comparison operator with this name")

    #writing assembly bin command
    def writeAssemblyComp(self,command,registers,offset):
        self.destinationFile.write(f"{self.ops[command[0]]}{registers[command[1]].binVal}{registers[command[2]].binVal}{self.convertToBvalue(offset,16)}\n")

    def assemble(self,command_arr,registers,memory):
        #binary format
        cmd   = command_arr[0]
        if cmd not in ['lui','lw','sw']:
            imm = command_arr[3]
            reg_s = command_arr[2]
            reg_t = command_arr[1]
            self.destinationFile.write(f"{self.ops[cmd]}{registers[reg_s].binVal}{registers[reg_t].binVal}{self.convertToBvalue(imm,16)}\n")
            # COMMAND EXECUTION
            if cmd == 'addi':
                registers[reg_t].value = registers[reg_s].value + int(imm)
                self.executionOutput.write(f"{registers[reg_s].value} {cmd} {imm} = {registers[reg_t].value}\n")
            elif cmd == 'andi':
                registers[reg_t].value = self.convertToBvalue(registers[reg_s].value & int(imm), 32)
                self.executionOutput.write( f"{self.convertToBvalue(registers[reg_s].value,32)} {cmd} {self.convertToBvalue(imm,32)} = {self.convertToBvalue(registers[reg_t].value,32)}\n")
            elif cmd == 'ori':
                #self.convertToBvalue(registers[reg_s], 32)[:16] + self.convertToBvalue(registers[reg_s] | int(imm), 16)[16:]
                registers[reg_t].value = self.convertToBvalue(registers[reg_s].value, 32)[:16] + self.convertToBvalue(registers[reg_s].value | int(imm), 16)
                registers[reg_t].value = int(registers[reg_t].value,2)
                self.executionOutput.write(f"{self.convertToBvalue(registers[reg_s].value,32)} {cmd} {self.convertToBvalue(imm,32)} = {self.convertToBvalue(registers[reg_t].value,32)}\n")
            elif cmd == 'slti':
                registers[reg_t].value="0"*31 + str(int(registers[reg_s].value< int(imm)))
                self.executionOutput.write(
                    f"{registers[reg_s].value} {cmd} {imm} = {registers[reg_t].value}\n")
                registers[reg_t].value = int(registers[reg_t].value, 2)
        elif cmd == 'lui':
            reg_t = command_arr[1]
            imm = command_arr[2]
            self.destinationFile.write(f"{self.ops[cmd]}00000{registers[reg_t].binVal}{self.convertToBvalue(imm,16)}\n")
            #command execution
            registers[reg_t].value = registers[reg_t].value + int(imm)*(2**16)
            self.executionOutput.write(f"reg_t {cmd} {imm}= {registers[reg_t].value}\n")
        elif cmd in ['sw','lw']:
            reg_t = command_arr[1]
            mix = self._parseToExtract(command_arr[2])
            offset = mix[0]
            reg_b = mix[1]
            if cmd == 'lw':
                registers[reg_t].value = memory[registers[reg_b].value + int(offset)]
                self.destinationFile.write(f"100011{registers[reg_b].binVal}{registers[reg_t].binVal}{self.convertToBvalue(offset,16)}\n")
            else:
                memory[registers[reg_b].value + int(offset)] = registers[reg_t].value
                self.destinationFile.write(f"101011{registers[reg_b].binVal}{registers[reg_t].binVal}{self.convertToBvalue(offset,16)}\n")

    def _parseToExtract(self,word):
        return word.replace('(', ' ').replace(')', ' ').split()
                    