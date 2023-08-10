# import serial
# import time

# # test parameters:
# pkt_sz = 512 # packet size, need to match the sender packet size


# # signal
# ack = b'ACK' # ack signal

# # done signal
# done = pkt_sz * b'D'


# total_data_received = 0

# # open receiver port
# receiver = serial.Serial('/dev/tty.usbmodem211203', 115200)
# print("receiver port: " + receiver.name) # check which port was really used
# receiver.write(ack) # let sender know that receiver is connected
# print("receiver connected")

# # receive data
# print("receiving data...")

# start = time.time()
# while True:
#     data = receiver.read(pkt_sz)
#     if data == done:
#         receiver.write(done)
#         break
#     else:
#         # print("data received: " + str(total_data_received))
#         # print progress bar
#         print("#", end="", flush=True)
#         if(len(data)!= pkt_sz):
#             print("data dropped: " + (pkt_sz - str(len(data))) + " bytes")
#         total_data_received += len(data)
#         receiver.write(ack) # write a string with newline

# end = time.time()
# delta_time = end - start
# print("\ntime taken: " + str(delta_time) + " seconds")



# # receive the last 4 bytes containing the total data sent
# total_data_sent = receiver.read(4)
# print("total data sent: " + str(int.from_bytes(total_data_sent, byteorder='big')) + " bytes")
# print("received data: " + str(total_data_received) + " bytes")
# throughput = (total_data_received) * 8/ delta_time
# print("throughput: " + str(2*throughput/1000) + " kbps")
# # close port
# receiver.close()


#  receiver class version
import serial
import time

class Receiver:
    def __init__(self, port, baudrate, pkt_sz=512):
        self.port = port                                # port
        self.baudrate = baudrate                        # baudrate
        self.receiver = serial.Serial(port, baudrate)   # receiver serial port
        self.ack = b'ACK'                               # ack signal
        self.done = pkt_sz * b'D'                       # done signal
        self.total_data_received = 0                    # total data received
        self.pkt_sz = pkt_sz                            # packet size
        self.delta_time = 0                             # time taken to receive all data

    def connect(self):
        print("receiver port: " + self.receiver.name) # check which port was really used
        self.receiver.write(self.ack) # let sender know that receiver is connected
        print("receiver connected")

    def receive_data(self):
        print("receiving data...")
        start = time.time()
        while True:
            data = self.receiver.read(self.pkt_sz)
            if data == self.done:
                self.receiver.write(self.done)
                break
            else:
                # print progress bar
                print("#", end="", flush=True)
                if(len(data)!= self.pkt_sz):
                    print("data dropped: " + (self.pkt_sz - str(len(data))) + " bytes")
                self.total_data_received += len(data)
                self.receiver.write(self.ack) # write a string with newline

        end = time.time()
        self.delta_time = end - start
        print("\ntime taken: " + str(self.delta_time) + " seconds")

    def receive_total_data_sent(self):
        # receive the last 4 bytes containing the total data sent
        total_data_sent = self.receiver.read(4)
        print("total data sent: " + str(int.from_bytes(total_data_sent, byteorder='big')) + " bytes")
        print("received data: " + str(self.total_data_received) + " bytes")
        throughput = (self.total_data_received) * 8/ self.delta_time
        print("throughput: " + str(2*throughput/1000) + " kbps")

    def close_port(self):
        self.receiver.close()

# create receiver object and open port
receiver = Receiver('/dev/tty.usbmodem211203', 115200)

# wait for sender to connect
receiver.connect()

# receive data
receiver.receive_data()

# receive total data sent from sender
receiver.receive_total_data_sent()

# close the port
receiver.close_port()
