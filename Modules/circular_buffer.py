class Circular_buffer:
    def __init__(self, size:int):
        self.maxlen = size
        self.size = 0
        self.data = [bytes(0) for i in range(size)]
        self.head = 0    
        self.tail = 0       
        self.empty = True

    def put(self, x:bytes) -> int:
        self.data[self.tail] = x
        self.tail += 1
        self.tail %= self.maxlen
        self.size += 1
        return len(x)

    def get(self) -> bytes:
        data = self.data[self.head]
        self.head += 1
        self.head %= self.maxlen
        self.size -= 1
        self.empty = (self.head == self.tail)
        return data
    
    def show_stat(self) -> None:
        print("\n--------- Circular Buffer Statistics --------- \n")
        print("| Maximum Capacity : {0:<10}              | \n".format(self.maxlen))
        print("| Current Size     : {0:<10}              | \n".format(self.size))
        print("---------------------------------------------- \n")
