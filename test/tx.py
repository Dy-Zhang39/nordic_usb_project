import serial


done = "1"
done = done.encode('utf-8')
wait = True


# open sender port
sender = serial.Serial('/dev/tty.usbmodem211201', 115200)
print("sender port: " + sender.name) # check which port was really used

total_data_sent = 0
print("waiting for receiver to connect...")
if sender.read(1) == done:
    wait = False
    print("receiver connected")

while total_data_sent < 100000:
    if wait == False:
        sender.write(b'2') # write a string with newline
        total_data_sent += 1
        # print("data sent: " + str(total_data_sent))
        wait = True
    if sender.read(1) == done:
        wait = False


sender.write(done) # write a string with newline

# send the total data sent to the receiver as 4 bytes
sender.write(total_data_sent.to_bytes(4, byteorder='big'))
print("sent data: " + str(total_data_sent)) 

# close port
sender.close()

