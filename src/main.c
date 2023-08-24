/*
 * Copyright (c) 2016 Intel Corporation
 *
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @file
 * @brief Sample app for CDC ACM class driver
 *
 * Sample app for USB CDC ACM class driver. The received data is echoed back
 * to the serial port.
 */

#include <stdio.h>
#include <string.h>
#include <device.h>
#include <drivers/uart.h>
#include <zephyr.h>
#include <sys/ring_buffer.h>

#include <usb/usb_device.h>
#include <logging/log.h>
LOG_MODULE_REGISTER(cdc_acm_composite, LOG_LEVEL_DBG);

#define RING_BUF_SIZE (64 * 2 * 2 * 2)
// tested size: 256,128
#define DATA_SIZE 128

uint8_t buffer0[RING_BUF_SIZE];
uint8_t buffer1[RING_BUF_SIZE];

struct serial_peer
{
	const struct device *dev;
	struct serial_peer *data;
	struct ring_buf rb;
};

#define DEFINE_SERIAL_PEER(node_id) {                                  \
										.dev = DEVICE_DT_GET(node_id), \
									},
static struct serial_peer peers[] = {
	DT_FOREACH_STATUS_OKAY(zephyr_cdc_acm_uart, DEFINE_SERIAL_PEER)};

BUILD_ASSERT(ARRAY_SIZE(peers) >= 2, "Not enough CDC ACM instances");

static void consume_h2t_data(struct ring_buf *buf, size_t sz)
{
	size_t data_sz = ring_buf_size_get(buf);
	if (data_sz != sz)
	{
		LOG_ERR("data_sz %zu != sz %zu", data_sz, sz);
	}
	// discard data and empty the buf
	size_t rd = ring_buf_get(buf, NULL, sz);
}

/**
 * @brief load data into T2H buffer, user should check the return value to make sure all data is loaded
 *
 * @param buf address if the t2h buffer
 * @param data address of the data
 * @param len data size
 * @return number of bytes wrote into the buffer
 */
size_t load_t2h_buf(struct ring_buf *buf, char *data, size_t len)
{
	size_t wrote = 0;
	// check if buffer is full
	size_t used_space = ring_buf_size_get(buf);
	size_t free_space = ring_buf_space_get(buf);
	LOG_DBG("Load T2H Buffer: buffer used space: %zu", used_space);
	LOG_DBG("Load T2H Buffer: buffer free space: %zu", free_space);

	if (ring_buf_space_get(buf) < len)
	{
		LOG_INF("T2H Buffer: buffer is full, wait for the data being read and try again", len);
		return 0;
	}

	wrote = ring_buf_put(buf, data, len);

	if (wrote != len)
	{
		LOG_ERR("T2H Buffer: Drop %zu bytes in loading data to T2H buffer", len - wrote);
	}

	return wrote;
}

int count = 0;
static void interrupt_handler(const struct device *dev, void *user_data)
{
	struct serial_peer *peer = user_data;
	LOG_DBG("irq called %zu", count++);
	while (uart_irq_update(dev) && uart_irq_is_pending(dev))
	{
		LOG_DBG("dev %p peer %p", dev, peer);

		if (uart_irq_rx_ready(dev))
		{
			uint8_t buf[256];
			size_t read, wrote;
			// note: &peer->data->rb is equvlant to the buffer associated with the current dev (aka. H2T buffer)

			read = uart_fifo_read(dev, buf, sizeof(buf));
			if (read < 0)
			{
				LOG_ERR("Failed to read UART FIFO");
				read = 0;
			};

			LOG_INF("Command received %c%c", buf[0], buf[1]);

			// 'RD' read command, read data from T2H buffer
			if (buf[0] == 'R' && buf[1] == 'D')
			{
				LOG_DBG("IRQ T2H Buffer: buffer used space: %zu", ring_buf_size_get(&peer->rb));
				LOG_DBG("IRQ T2H Buffer: buffer free space： %zu", ring_buf_space_get(&peer->rb));

				while (true)
				{
					if (ring_buf_size_get(&peer->rb) > 255)
					{
						LOG_DBG("IRQ eanble TX, current T2H buffer size	: %zu", ring_buf_size_get(&peer->rb));
						uart_irq_tx_enable(peer->dev);
						break;
					}
					else
					{
						LOG_DBG("IRQ RD sleep... waiting data to be ready in T2H buffer, current buffer size: %zu", ring_buf_size_get(&peer->rb));

						k_sleep(K_MSEC(100));
					}
				}
				// uart_irq_tx_enable(peer->dev);
			}
			else if (buf[0] == 'W' && buf[1] == 'R')
			// 'WR' write command, write data to H2T buffer
			{
				LOG_DBG("H2T Buffer: dev1 %p H2T buffer free space left: %zu", dev, ring_buf_space_get(&peer->data->rb));
				wrote = ring_buf_put(&peer->data->rb, buf, read);

				if (wrote < read)
				{
					LOG_ERR("H2T Buffer: Drop %zu bytes in writing data to H2T buffer", read - wrote);
				}

				LOG_DBG("H2T Buffer: dev1 %p wrote %zu bytes into H2T buffer, free space left: %zu", dev, wrote, ring_buf_space_get(&peer->data->rb));

				// process data in the H2T buffer, otherwise it will be full
				consume_h2t_data(&peer->data->rb, wrote);
			}
			else
			{

				LOG_ERR("Unknown command %c%c", buf[0], buf[1]);
			}
		}

		if (uart_irq_tx_ready(dev))
		{
			uint8_t buf[256];
			memset(buf, 'E', 256);
			size_t wrote, len;

			// get the data out from self.buffer (T2H buffer)
			len = ring_buf_get(&peer->data->rb, buf, sizeof(buf));
			if (!len)
			{
				// no data available, send all 'E(empty)' to host
				uart_fifo_fill(dev, buf, 256);
				LOG_DBG("dev2 %p T2H buffer empty", dev);
				uart_irq_tx_disable(dev);
			}
			else
			{
				wrote = uart_fifo_fill(dev, buf, len);
				LOG_INF("dev2 %p sent len %zu bytes to host", dev, wrote);

				if (wrote < len)
				{
					LOG_ERR("T2H Buffer: Drop %zu bytes in sneding data to host buffer", len - wrote);
				}
				uart_irq_tx_disable(dev);
			}
		}
	}
}

static void uart_line_set(const struct device *dev)
{
	uint32_t baudrate;
	int ret;

	/* They are optional, we use them to test the interrupt endpoint */
	ret = uart_line_ctrl_set(dev, UART_LINE_CTRL_DCD, 1);
	if (ret)
	{
		LOG_DBG("Failed to set DCD, ret code %d", ret);
	}

	ret = uart_line_ctrl_set(dev, UART_LINE_CTRL_DSR, 1);
	if (ret)
	{
		LOG_DBG("Failed to set DSR, ret code %d", ret);
	}

	/* Wait 1 sec for the host to do all settings */
	k_busy_wait(1000000);

	ret = uart_line_ctrl_get(dev, UART_LINE_CTRL_BAUD_RATE, &baudrate);
	if (ret)
	{
		LOG_DBG("Failed to get baudrate, ret code %d", ret);
	}
	else
	{
		LOG_DBG("Baudrate detected: %d", baudrate);
	}
}

/**
 * @brief initalize usb device
 *
 * @return return true if success, otherwise return false
 */
int usb_init()
{
	uint32_t dtr = 0U;
	int ret;

	for (int idx = 0; idx < ARRAY_SIZE(peers); idx++)
	{
		if (!device_is_ready(peers[idx].dev))
		{
			LOG_ERR("CDC ACM device %s is not ready",
					peers[idx].dev->name);
			return;
		}
	}

	ret = usb_enable(NULL);
	if (ret != 0)
	{
		LOG_ERR("Failed to enable USB");
		return;
	}

	LOG_INF("Wait for DTR");

	while (1)
	{
		uart_line_ctrl_get(peers[0].dev, UART_LINE_CTRL_DTR, &dtr);
		if (dtr)
		{
			break;
		}

		k_sleep(K_MSEC(100));
	}

	while (1)
	{
		uart_line_ctrl_get(peers[1].dev, UART_LINE_CTRL_DTR, &dtr);
		if (dtr)
		{
			break;
		}

		k_sleep(K_MSEC(100));
	}

	LOG_INF("DTR set, start test");

	uart_line_set(peers[0].dev);
	uart_line_set(peers[1].dev);

	peers[0].data = &peers[1];
	peers[1].data = &peers[0];

	ring_buf_init(&peers[0].rb, sizeof(buffer0), buffer0);
	ring_buf_init(&peers[1].rb, sizeof(buffer1), buffer1);

	uart_irq_callback_user_data_set(peers[1].dev, interrupt_handler, &peers[0]);
	uart_irq_callback_user_data_set(peers[0].dev, interrupt_handler, &peers[1]);

	/* Enable rx interrupts */
	uart_irq_rx_enable(peers[0].dev);
	uart_irq_rx_enable(peers[1].dev);
}

/**
 * @brief send data to the host, user should check the return value to make sure all data is sent
 *
 * @param data address of the data
 * @param len data size
 * @return return number of bytes sent
 */
int usb_send_data(char *data, size_t len)
{
	int wrote;
	wrote = load_t2h_buf(&peers[1].rb, data, len);
	return wrote;
}


/**
 * @brief example of using usb to send data to the host
 *
 * @return return 0 if success, otherwise return -1
 */
void main(void)
{
	if (!usb_init())
	{
		LOG_ERR("USB init failed");
	}

	// test data
	int data_indx = 0;
	char data[DATA_SIZE];
	memset(data, '1', DATA_SIZE);
	data[8] = '0';

	// loop to send data
	while(true)
	{
		int wrote;
		wrote = usb_send_data(&data, DATA_SIZE);
		if(wrote != DATA_SIZE)
		{
			LOG_ERR("USB send data failed");
		}
		else
		{
			// sned next data
			data_indx++;
			data[8] = data_indx + '0';
		}
	}
}
