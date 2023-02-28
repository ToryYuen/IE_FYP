import socket
import struct
import time
import threading


FILE_NAME = "TestFile/result.txt"
FILE_SIZE = 0

#
# Multicast Socket
#
# GROUP = '224.1.1.1'
# PORT = 5008
# TTL = 2
#
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind(('', PORT))
#
# mreq = struct.pack("4sl", socket.inet_aton(GROUP), socket.INADDR_ANY)
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


#
# Receiver TCP Server
#
RECEIVER_HOST = socket.gethostbyname(socket.gethostname())
RECEIVER_PORT = 5567
ADDR = (RECEIVER_HOST, RECEIVER_PORT)
BUFFER_SIZE = 1032


def handle_client(conn, addr):
    print(f"\n[NEW CONNECTION] {addr} connected.")

    packet_received = 0
    total_packet_num = 0

    start_timer = 0.0
    connected = True
    with open(FILE_NAME, 'wb') as f:
        while connected:

            data = conn.recv(BUFFER_SIZE)
            packet_received += 1

            if packet_received == 1:
                header = data[:8]
                (seq_num, total_packet_num) = struct.unpack('!II', header)
                start_timer = time.time()
                print(f"[{addr}] Expected Total packets: {total_packet_num}")

            file_data = data[8:]
            f.write(file_data)

            if packet_received == total_packet_num:
                connected = False

    print(f"[{addr}] Received packets: {packet_received}")
    total_time = time.time() - start_timer
    print(f"[{addr}] Total time: {total_time}")
    conn.close()


def main():
    print("[STARTING] Receiver server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Receiver is listening on {RECEIVER_HOST}:{RECEIVER_PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] in Receiver {threading.activeCount() - 1}")


if __name__ == "__main__":
    main()
