class Pipeline:
    def __init__(self,file_name):
        pipe_file_name = file_name.replace(".txt","-pipeline")
        self.pipeline = open(f"{pipe_file_name}.txt",mode = 'w+')
        self.length = None
        self.cc = 0
    def analyse(self,registers,currentCommand,nextCommand,memory):
        self.cc+=1
        self.pipeline.write(f"Clock Cycle: {self.cc}\nExecuting: {currentCommand}\nFetching: {nextCommand}\n")
        for register in registers.keys():
            self.pipeline.write(
                f"Register ${register} value: {registers[register].value}\n")
        self.pipeline.write(f"Memory{memory}\n")
        self.pipeline.write(f"####################################################\n####################################################\n")
        
    def setLength(self,length):
        self.length = length
