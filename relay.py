import socket
import struct
import time
import threading
# Self-defined Modules
from Modules import circular_buffer as cb

#
# Circular Buffer
# -!!!- If too large not sure why affect the accuracy of time.time()
RELAY_CIRCULAR_BUFFER_SIZE = 131072

#
# TCP
#
RELAY_HOST = socket.gethostbyname(socket.gethostname())
RELAY_PORT = 5566
BUFFER_SIZE = 1032

#
#  Out-going
#
outgoingMap = {}


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    relay_cirBuffer = cb.Circular_buffer(RELAY_CIRCULAR_BUFFER_SIZE)

    packet_received = 0
    total_packet_num = 0
    packets_transmitted = 0
    avg_time = 0.0

    receive_start_timer = 0.0
    transmit_start_timer = 0.0

    # Receiver socket
    receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver.connect((RELAY_HOST, 5567))
    print(f"\n[CONNECTED] Relay connected to Receiver at {RELAY_HOST}:{5567}")

    connected = True
    while connected:
        data = conn.recv(BUFFER_SIZE)

        # Put the packet into buffer
        relay_cirBuffer.put(data)
        packet_received += 1

        # First packet arrived
        if packet_received == 1:
            header = data[:8]
            (seq_num, total_packet_num) = struct.unpack('!II', header)
            receive_start_timer = time.time()

        # Average time base on the
        avg_time = (time.time() - receive_start_timer) / packet_received

        # If buffer is not empty, transmit and sleep
        if relay_cirBuffer.size > 0:

            data = relay_cirBuffer.get()

            # Start transmission timer
            if packets_transmitted == 0:
                transmit_start_timer = time.time()
            receiver.sendall(data)

            packets_transmitted += 1

            # (Expected time used) - (current time used)
            sleep_time = avg_time * packets_transmitted - (time.time() - transmit_start_timer)
            if sleep_time > 0:
                time.sleep(sleep_time)

        if packets_transmitted == total_packet_num:
            connected = False

    total_time = time.time() - transmit_start_timer
    print(f"[END CONNECTION] Transmitted all {packets_transmitted} packets, {addr} disconnected.")
    print(f"Average Time Per Packet: {avg_time}s")
    print(f"Total Transmission Time: {total_time}s")
    conn.close()


def main():
    print("[STARTING] Relay Server is starting...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((RELAY_HOST, RELAY_PORT))
    sock.listen(5)
    print(f"[LISTENING] Relay is listening on {RELAY_HOST}:{RELAY_PORT}")

    while True:
        conn, addr = sock.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


if __name__ == "__main__":
    main()
