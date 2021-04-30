class Register:
    def __init__(self,m_type,value = None):
        self.m_type = m_type  #type
        self.value = value  #value
        self.binVal = None  #address


    def update(self,value):
        self.value = value

    def toBin(self,num):
        num = int(num)
        num = str(bin(num)[2:])
        while(len(num)<5):
            num = "0" + num
        return num
    