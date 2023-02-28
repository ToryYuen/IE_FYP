import math


class Sender():
    def __init__(self, transmission_rate:int, file_size:int, buf_size:int) -> None:
        self.transmission_rate = transmission_rate
        self.file_size = file_size
        self.buf_size = buf_size

        self.packet_sent = 0
        self.packets_required = math.ceil(file_size / buf_size)
        self.packets_per_second = math.floor(transmission_rate / buf_size)
        self.time_per_packet = 1 / self.packets_per_second
        self.time_required = file_size / transmission_rate

    def show_txStat(self) -> None:
        print("\n---------------- Transmission Statistics ----------------- \n")
        print("| Transmission Rate  : {0:<15} (Bytes Per Second)| \n".format(self.transmission_rate))
        print("| File Size          : {0:<15}            (Bytes)| \n".format(self.file_size))
        print("| Payload Size       : {0:<15}            (Bytes)| \n".format(self.buf_size))
        print("| Required Packet    : {0:<15}                   | \n".format(self.packets_required))
        print("| Packet Sent        : {0:<15}                   | \n".format(self.packet_sent))
        print("| Packets Per Second : {0:<15}                   | \n".format(self.packets_per_second))
        print("| Time Per Packet    : {0:<15}                   | \n".format(self.time_per_packet))
        print("| Time Required      : {0:<15}                (s)| \n".format(self.time_required))
        print("---------------------------------------------------------- \n")
        
