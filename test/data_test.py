


#  receiver class version
import serial
import time

class Sender:
    def __init__(self, port, baudrate, pkt_sz=64, num_pkts=1):
        self.port = port                                            # port name, check which port was really used
        self.baudrate = baudrate                                    # baudrate, check which baudrate was really used
        self.sender = serial.Serial(port, baudrate)                 # open sender port
        self.rd = b'RD'                                           # ack signal
        self.wr = b'WR'                                         # done signal   
        self.total_data_sent = 0                                    # total data sent
        self.pkt_sz = pkt_sz                                        # packet size
        self.num_pkts = num_pkts                                    # total pkts to be sent
        self.data =  b'test'                                   #create a data of pkt_sz bytes

    def connect(self):
        print("sender port: " + self.sender.port) # check which port was really used


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
        data = data.ljust(64, b'0')
        print(data)
        self.sender.write(data)
        self.total_data_sent += len(data)

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

    def receive_data(self) -> bytes:
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
        return data
        # print(data)

    def receive_total_data_sent(self):
        # receive the last 4 bytes containing the total data sent
        total_data_sent = self.receiver.read(4)
        print("total data sent: " + str(int.from_bytes(total_data_sent, byteorder='big')) + " bytes")
        print("received data: " + str(self.total_data_received) + " bytes")
        throughput = (self.total_data_received) * 8/ self.delta_time
        print("throughput: " + str(2*throughput/1000) + " kbps")

    def save_to_file(self, data, pkt_num=0):
        with open('data.txt', 'a') as f:
            f.write(str(pkt_num) + ": ")
            f.write(data.decode('utf-8'))
            f.write('\n')

    def close_port(self):
        self.receiver.close()



receiver = Receiver('/dev/tty.usbmodem211203', 115200)
sender = Sender('/dev/tty.usbmodem211201', 115200)
time.sleep(2)


def test_rx():
    total_pkt_rd = 0
    start = time.time()
    while(total_pkt_rd < 100000):
        sender.send_rd_signal()
        data = receiver.receive_data_rd()
        receiver.save_to_file(data, total_pkt_rd)
        total_pkt_rd += 1


    end = time.time()
    delta_time = end - start

    throughput = receiver.total_data_received * 8/ delta_time
    print("total data received: " + str(receiver.total_data_received) + " bytes")
    print("throughput: " + str(throughput/1000) + " kbps")


def test_tx():
    total_pkt_wr = 0
    start = time.time()
    while(total_pkt_wr < 4000):
        sender.send_WR_signal()
        time.sleep(0.2)  # wait is needed to prevent receiver from dropping data, sender ideal packet szie is 64 bytes
        total_pkt_wr += 1

    end = time.time()
    delta_time = end - start

    throughput = sender.total_data_sent * 8/ delta_time
    print("total data sent: " + str(sender.total_data_sent) + " bytes")
    print("throughput: " + str(throughput/1000) + " kbps")


def test_rx():
    total_pkt_rd = 0
    start = time.time()
    while(total_pkt_rd < 1000):
        sender.send_rd_signal()
        data = receiver.receive_data_rd()
        receiver.save_to_file(data, total_pkt_rd)
        total_pkt_rd += 1


    end = time.time()
    delta_time = end - start

    throughput = receiver.total_data_received * 8/ delta_time
    print("total data received: " + str(receiver.total_data_received) + " bytes")
    print("throughput: " + str(throughput/1000) + " kbps")


def test_tx():
    total_pkt_wr = 0
    start = time.time()
    while(total_pkt_wr < 30):
        sender.send_WR_signal()
        time.sleep(0.2)  # wait is needed to prevent receiver from dropping data, sender ideal packet szie is 64 bytes
        total_pkt_wr += 1
    
    # time.sleep(1)
    # sender.send_WR_signal()


    end = time.time()
    delta_time = end - start

    throughput = sender.total_data_sent * 8/ delta_time
    print("total data sent: " + str(sender.total_data_sent) + " bytes")
    print("throughput: " + str(throughput/1000) + " kbps")


test_rx()
# test_tx()


sender.close_port()
receiver.close_port()