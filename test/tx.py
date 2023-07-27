import serial

# test procedure:
# 1. start sender, sender will wait for receiver to send ack signal
# 2. start receiver, receiver will connect to sender and send ack signal
# 3. after sender receives ack signal, sender will start sending data, and wait for reciever to send ack signal
# 4. after receiver receives data, receiver will send ack signal to sender
# 5. repeat step 3 and 4 until total data sent is 1000 bytes
# 6. after total data sent is 1000 bytes, sender will send done signal to receiver
# 7. after receiver receives done signal, receiver will send done signal to sender
# 8. after sender receives done signal, sender will send the total data sent to the receiver as 4 bytes
# 9. after receiver receives the total data sent, receiver will print out the throughput
# 10. close the port

# test parameters:
pkt_sz = 128           # packet size
test_data_sz = 100000 # total data to be sent

# signal
ack = b'ACK'            # ack signal
done = pkt_sz * b'D'
wait = True
total_data_sent = 0

#create a data of pkt_sz bytes
data = pkt_sz * b'a'

# open sender port
sender = serial.Serial('/dev/tty.usbmodem211201', 115200)
print("sender port: " + sender.name) # check which port was really used

# wait for receiver to connect
print("waiting for receiver to connect...")
if sender.read(len(ack)) == ack:
    wait = False
    print("receiver connected")

# send data
while total_data_sent < test_data_sz:
    if wait == False:
        sender.write(data) # write a string with newline
        total_data_sent += len(data)
        print("#", end="", flush=True)
        # print("data sent: " + str(total_data_sent))
        wait = True
    if sender.read(len(ack)) == ack:
        wait = False


# send done signal to receiver
sender.write(done)
print("\n")
if sender.read(pkt_sz) == done:
    print("receiver received done signal")
    # send the total data sent to the receiver as 4 bytes
    sender.write(total_data_sent.to_bytes(4, byteorder='big'))
    print("sent data: " + str(total_data_sent)) 

# close port
sender.close()

