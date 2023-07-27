# nordic_usb_project
# Overivew 
This app demonstrates the use of a USB Communication Device Class (CDC) Abstract Control Model (ACM) driver provided by the Zephyr project. Received data from the serial port is echoed back to the same port provided by this driver.

The throughput test implements a stop-and-wait flow control to manage the data transfer rate between two serial ports.

Tested on nRF5340 DK. 

# Running & testing the throughput
program the board and go to device manager on Windows or do ```ls /dev/``` on Mac/linux to find the serial port. You should see something similar to ```/dev/tty.usbmodem211201```. Replace the serial port with what you found in the rx.py/tx.py in the test folder. The Python script will open the port for you and run the throughput test.

Follow the instructions in the tx.py to learn how the tester works and modify the test parameter to fit your needs.

# Results
## Sender
![image](https://github.com/Dy-Zhang39/nordic_usb_project/assets/85214707/aad37304-ee99-426f-a023-12daf660c7fc)

## Receiver
![image](https://github.com/Dy-Zhang39/nordic_usb_project/assets/85214707/989040d9-06c7-4e68-9d9e-22f6092d71b7)
