import serial
import time

# test parameters:
pkt_sz = 128 # packet size, need to match the sender packet size
test_data_sz = 100000 # total data to be sent

# signal
ack = b'ACK' # ack signal

# done signal
done = pkt_sz * b'D'


total_data_received = 0

# open receiver port
receiver = serial.Serial('/dev/tty.usbmodem211203', 115200)
print("receiver port: " + receiver.name) # check which port was really used
receiver.write(ack) # let sender know that receiver is connected
print("receiver connected")

# receive data
print("receiving data...")

start = time.time()
while True:
    data = receiver.read(pkt_sz)
    if data == done:
        receiver.write(done)
        break
    else:
        # print("data received: " + str(total_data_received))
        # print progress bar
        print("#", end="", flush=True)
        total_data_received += len(data)
        receiver.write(ack) # write a string with newline

end = time.time()
delta_time = end - start
print("\ntime taken: " + str(delta_time))



# receive the last 4 bytes containing the total data sent
total_data_sent = receiver.read(4)
print("total data sent: " + str(int.from_bytes(total_data_sent, byteorder='big')))
print("received data: " + str(total_data_received - 1)) # minus 1 because of the last ack signal
throughput = (total_data_received - 1) * 8/ delta_time
print("throughput: " + str(throughput) + " bits/second")
# close port
receiver.close()
