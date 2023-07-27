import serial
import time

# signal
done = "1"
done = done.encode('utf-8')

# open receiver port
receiver = serial.Serial('/dev/tty.usbmodem211203', 115200)
print("receiver port: " + receiver.name) # check which port was really used
receiver.write(done) # let sender know that receiver is connected
print("receiver connected")

total_data_received = 0
# receive data
print("receiving data...")

start = time.time()
while True:
    data = receiver.read(1)
    # print("data received: " + str(total_data_received))
    total_data_received += 1
    receiver.write(done) # write a string with newline
    if data == done:
        break

end = time.time()
delta_time = end - start
print("time taken: " + str(delta_time))


# send done signal to sender
receiver.write(done)

# receive the last 4 bytes containing the total data sent
total_data_sent = receiver.read(4)
print("total data sent: " + str(int.from_bytes(total_data_sent, byteorder='big')))
print("received data: " + str(total_data_received - 1)) # minus 1 because of the last done signal
throughput = (total_data_received - 1) * 8/ delta_time
print("throughput: " + str(throughput) + " bits/second")
# close port
receiver.close()
