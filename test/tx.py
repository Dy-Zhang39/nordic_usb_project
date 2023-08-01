# import serial

# # test procedure:
# # 1. start sender, sender will wait for receiver to send ack signal
# # 2. start receiver, receiver will connect to sender and send ack signal
# # 3. after sender receives ack signal, sender will start sending data, and wait for reciever to send ack signal
# # 4. after receiver receives data, receiver will send ack signal to sender
# # 5. repeat step 3 and 4 until total data sent is 1000 bytes
# # 6. after total data sent is 1000 bytes, sender will send done signal to receiver
# # 7. after receiver receives done signal, receiver will send done signal to sender
# # 8. after sender receives done signal, sender will send the total data sent to the receiver as 4 bytes
# # 9. after receiver receives the total data sent, receiver will print out the throughput
# # 10. close the port

# # test parameters:
# pkt_sz = 512       # packet size
# num_pkts = 2000 # total data to be sent
# count = 0               # number of packets sent

# # signal
# ack = b'ACK'            # ack signal
# done = pkt_sz * b'D'
# wait = True
# total_data_sent = 0

# #create a data of pkt_sz bytes
# data = pkt_sz * b'a'

# # open sender port
# sender = serial.Serial('/dev/tty.usbmodem211201', 115200)
# print("sender port: " + sender.name) # check which port was really used

# # wait for receiver to connect
# print("waiting for receiver to connect...")
# if sender.read(len(ack)) == ack:
#     wait = False
#     print("receiver connected")

# # send data
# while count < num_pkts:
#     if wait == False:
#         sender.write(data) # write a string with newline
#         total_data_sent += len(data)
#         count += 1
#         print("#", end="", flush=True)
#         # print("data sent: " + str(total_data_sent))
#         wait = True
#     if sender.read(len(ack)) == ack:
#         wait = False


# # send done signal to receiver
# sender.write(done)
# print("\n")
# if sender.read(pkt_sz) == done:
#     print("receiver received done signal")
#     # send the total data sent to the receiver as 4 bytes
#     sender.write(total_data_sent.to_bytes(4, byteorder='big'))
#     print("sent data: " + str(total_data_sent) + " bytes")

# # close port
# sender.close()



## Class version

import serial

class Sender:
    def __init__(self, port, baudrate, pkt_sz=512, num_pkts=2000):
        self.port = port
        self.baudrate = baudrate
        self.sender = serial.Serial(port, baudrate)
        self.ack = b'ACK'
        self.done = b'DONE'
        self.wait = True
        self.total_data_sent = 0
        self.pkt_sz = pkt_sz
        self.num_pkts = num_pkts
        self.data = pkt_sz * b'a' #create a data of pkt_sz bytes

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

    def close_port(self):
        self.sender.close()

# create sender object and open port
sender = Sender('/dev/tty.usbmodem211201', 115200)

# wait for receiver to connect
sender.connect()

# send data
sender.send_data(sender.data, sender.num_pkts)

# send done signal to receiver
sender.send_done_signal(sender.pkt_sz)

# close the port
sender.close_port()
