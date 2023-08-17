


#  receiver class version
import serial
import time

class Sender:
    def __init__(self, port, baudrate, pkt_sz=255, num_pkts=1):
        self.port = port                                            # port name, check which port was really used
        self.baudrate = baudrate                                    # baudrate, check which baudrate was really used
        self.sender = serial.Serial(port, baudrate)                 # open sender port
        self.ack = b'ACK'                                           # ack signal
        self.done = b'DONE'                                         # done signal   
        self.wait = True                                            # wait for receiver to send ack signal
        self.total_data_sent = 0                                    # total data sent
        self.pkt_sz = pkt_sz                                        # packet size
        self.num_pkts = num_pkts                                    # total pkts to be sent
        self.data = pkt_sz * b'a'                                   #create a data of pkt_sz bytes

    def connect(self):
        print("sender port: " + self.sender.port) # check which port was really used
        print("waiting for receiver to connect...")
        if self.sender.read(len(self.ack)) == self.ack:
            self.wait = False
            print("receiver connected")

    def send_data(self, data, num_pkts):
        count = 0
        while count < num_pkts:
            if self.wait == False:
                self.sender.write(data) # write a string with newline
                self.total_data_sent += len(data)
                count += 1
                print("#", end="", flush=True)
                # print("data sent: " + str(total_data_sent))
                self.wait = True
            if self.sender.read(len(self.ack)) == self.ack:
                self.wait = False

    def send_done_signal(self, pkt_sz):
        done_signal = pkt_sz * b'D'
        self.sender.write(done_signal)
        print("\n")
        if self.sender.read(pkt_sz) == done_signal:
            print("receiver received done signal")
            # send the total data sent
            self.sender.write(self.total_data_sent.to_bytes(4, byteorder='big'))
            print("total data sent: " + str(self.total_data_sent))

    def send_rd_signal(self):
        rd_signal = b'RD'
        self.sender.write(rd_signal)

    def send_WR_signal(self):
        data = b'WR0101010101010101010101010101010101001'
        data = data.ljust(256, b'0')
        print(data)
        self.sender.write(data)

    def close_port(self):
        self.sender.close()

class Receiver:
    def __init__(self, port, baudrate, pkt_sz=255):
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
        # print("receiving data...")
        start = time.time()
        while True:
            data = self.receiver.read(self.pkt_sz)
            if data == self.done:
                self.receiver.write(self.done)
                break
            else:
                # print progress bar
                # print("#", end="", flush=True)
                # print(data)
                if(len(data)!= self.pkt_sz):
                    print("data dropped: " + (self.pkt_sz - str(len(data))) + " bytes")
                self.total_data_received += len(data)
                self.receiver.write(self.ack) # write a string with newline

        end = time.time()
        self.delta_time = end - start
        print("\ntime taken: " + str(self.delta_time) + " seconds")

    def receive_data_rd(self):
        # print("receiving data...")
        data = self.receiver.read(self.pkt_sz)
        self.total_data_received += len(data)
        # print(data)

    def receive_total_data_sent(self):
        # receive the last 4 bytes containing the total data sent
        total_data_sent = self.receiver.read(4)
        print("total data sent: " + str(int.from_bytes(total_data_sent, byteorder='big')) + " bytes")
        print("received data: " + str(self.total_data_received) + " bytes")
        throughput = (self.total_data_received) * 8/ self.delta_time
        print("throughput: " + str(2*throughput/1000) + " kbps")

    def close_port(self):
        self.receiver.close()

# # create receiver object and open port
# receiver = Receiver('/dev/tty.usbmodem211203', 115200)

# # wait for sender to connect
# receiver.connect()

# # receive data
# receiver.receive_data()

# # receive total data sent from sender
# receiver.receive_total_data_sent()

# # close the port
# receiver.close_port()


receiver = Receiver('/dev/tty.usbmodem211203', 115200)
sender = Sender('/dev/tty.usbmodem211201', 115200)

# total_pkt_rd = 0
# start = time.time()
# while(total_pkt_rd < 20):
#     sender.send_rd_signal()
#     receiver.receive_data_rd()
#     total_pkt_rd += 1


# end = time.time()
# delta_time = end - start

# throughput = receiver.total_data_received * 8/ delta_time
# print("total data sent: " + str(receiver.total_data_received) + " bytes")
# print("throughput: " + str(throughput/1000) + " kbps")



def test_rx():
    total_pkt_rd = 0
    start = time.time()
    while(total_pkt_rd < 2000):
        sender.send_rd_signal()
        receiver.receive_data_rd()
        total_pkt_rd += 1


    end = time.time()
    delta_time = end - start

    throughput = receiver.total_data_received * 8/ delta_time
    print("total data received: " + str(receiver.total_data_received) + " bytes")
    print("throughput: " + str(throughput/1000) + " kbps")


# sender.send_WR_signal()

test_rx()
# test_tx()


sender.close_port()
receiver.close_port()