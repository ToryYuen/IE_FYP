import socket
import os
import struct
import time
# Self-defined Modules
from Modules import circular_buffer as cb, Streamer

#
# Circular Buffer
#
CIRCULAR_BUFFER_SIZE = 131072

#
# Streamer
#
FILE_NAME = "TestFile/test.txt"
TX_RATE = 10240000   # 10MBps
BUFFER_SIZE = 1024

#
# Multicast Socket
#
# GROUP = '224.1.1.1'
# PORT = 5007
# TTL = 2


#
# TCP
#
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (HOST, PORT)


def fill_cBuffer(f, cBuffer, streamer):
    for i in range(cBuffer.maxlen):
        data = bytearray()

        # Read data from the file
        data.extend(f.read(BUFFER_SIZE))
        if data:

            # Each packet = sequence no. + no. of total packets + data[Buffer Size]
            header = struct.pack('!II', streamer.packet_sent + i, streamer.packets_required)

            cBuffer.put(header + bytearray(data))

        else:
            break


def main():
    with open(FILE_NAME, 'rb') as f:

        # 1. Initialize Circular buffer
        cBuffer = cb.Circular_buffer(CIRCULAR_BUFFER_SIZE)
        cBuffer.show_stat()

        # 2. Initialize streamer
        FILE_SIZE = os.path.getsize(FILE_NAME)
        streamer = Streamer.Sender(TX_RATE, FILE_SIZE, BUFFER_SIZE)

        # 3. Initialize Socket
        # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL) # Reuse addr and port
        sendSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sendSock.connect(ADDR)
        print(f"[CONNECTED] sender connected to relay at {HOST}:{PORT}")

        # 4. Fill the Circular Buffer
        fill_cBuffer(f, cBuffer, streamer)

        print("Expected Time : {0}s".format(streamer.time_required))

        # 5. Start Transmission
        compensation_start_timer = time.time()
        for i in range(streamer.packets_required):

            data = cBuffer.get()

            sendSock.sendall(data)

            streamer.packet_sent += 1

            if cBuffer.empty == True and streamer.packet_sent != streamer.packets_required:
                print("cBuffer empty at: " + str(i))
                fill_cBuffer(f, cBuffer, streamer)

            # (Expected time used according to the sequence number) - (current time used)
            sleep_time = streamer.time_per_packet * (i + 1) - (time.time() - compensation_start_timer)

            if sleep_time > 0:
                time.sleep(sleep_time)

        compensation_end_timer = time.time()

        if compensation_end_timer - compensation_start_timer > streamer.time_required:
            time.sleep(compensation_end_timer - compensation_start_timer > streamer.time_required)

        streamer.show_txStat()
        print("Total Time Used: " + str(compensation_end_timer - compensation_start_timer))


if __name__ == "__main__":
    main()
