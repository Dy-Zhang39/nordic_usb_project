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

int once;

// static void consume_h2t_data(struct ring_buf *buf)
// {
// 	uint8_t temp_buf[256];
// 	size_t len;
// 			// get the data out from self.buffer (T2H buffer)
// 	len = ring_buf_get(buf, temp_buf, sizeof(temp_buf));
// 	if (!len)
// 	{
// 		LOG_DBG("dev1 %p H2T buffer empty", buf);
// 	}
// 	else
// 	{
// 		LOG_INF("dev1 %p H2T buffer loaded %zu bytes", buf, len);
// 			// print the tmep_buf
// 		for(int i = 0; i < 20; i++)
// 		{
// 			LOG_INF("%c", temp_buf[i]);
// 		}
// 	}


// }
int count  = 1;
static void interrupt_handler(const struct device *dev, void *user_data)
{
	struct serial_peer *peer = user_data;
	LOG_INF("irq called %zu", count++);
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


			LOG_INF("read %zu bytes %c%c", read, buf[0], buf[1]);


			// read command, read data from T2H buffer
			if (buf[0] == 'R' && buf[1] == 'D')
			{
				// load data into peer's(T2H) buffer
				char data[256] = "010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010";
				int len = strlen(data);
				wrote = ring_buf_put(&peer->rb, data, len);

				if (wrote < len)
				{
					LOG_ERR("Drop %zu bytes in loading data to T2H buffer", len - wrote);
				}

				LOG_INF("T2H load: dev2 %p T2H T2H buffer loaded %zu bytes", peer->dev, wrote);

				if (wrote)
				{
					// tell peer to send out the data
					uart_irq_tx_enable(peer->dev);
				}
			}
			else if (buf[0] == 'W' && buf[1] == 'R')
			// write command, route data to H2T buffer
			{
				LOG_INF("dev1 %p H2T buffer free space: %zu", dev, ring_buf_space_get(&peer->data->rb));
				wrote = ring_buf_put(&peer->data->rb, buf, read);

				if (wrote < read)
				{
					LOG_ERR("Drop %zu bytes in writing data to H2T buffer", read - wrote);
				}

				LOG_INF("dev1 %p wrote %zu bytes into H2T buffer",
						dev, wrote);

				LOG_INF("dev1 %p H2T buffer free space: %zu", dev, ring_buf_space_get(&peer->data->rb));

				int rd = ring_buf_get(&peer->data->rb, NULL, wrote);

				LOG_INF("dev1 %p H2T buffer freed: %zu", dev, rd);

				LOG_INF("dev1 %p H2T buffer free space: %zu", dev, ring_buf_space_get(&peer->data->rb));

				

				
				// // if H2T buffer not full
				// if(ring_buf_space_get(&peer->data->rb) < 256)
				// {
				// 	LOG_ERR("H2T buffer is full");
				// }
				// else
				// {
				// 	LOG_INF("dev1 %p H2T buffer free space: %zu", dev, ring_buf_space_get(&peer->data->rb));
				// 	// write data to self.buffer (H2T buffer)
				// 	wrote = ring_buf_put(&peer->data->rb, buf, read);
				// 	if (wrote < read)
				// 	{
				// 		LOG_ERR("Drop %zu bytes when writing to H2T buffer", read - wrote);
				// 	}

				// 	LOG_INF("dev1 %p wrote %zu bytes into H2T buffer",
				// 			dev, wrote);

				// 	LOG_INF("dev1 %p H2T buffer free space: %zu", dev, ring_buf_space_get(&peer->data->rb));

				// 	// ohter program to consume the data
				// 	char temp_buf[256];
				// 	read = ring_buf_get(&peer->data->rb, temp_buf, wrote);
				// 	if (!read)
				// 	{
				// 		LOG_ERR("Failed to read from the H2T buffer");
				// 	}
				// 	else
				// 	{
				// 		// print buf
				// 		for(int i = 0; i < 10; i++)
				// 		{
				// 			LOG_INF("%c", temp_buf[i]);
				// 		}
				// 		LOG_INF("dev1 %p H2T buffer cleaned %zu bytes, free buffer space: %zu", dev, read, ring_buf_space_get(&peer->data->rb));
				// 	}
				// 	// consume_h2t_data(&peer->data->rb);
				// }
				// // write data to self.buffer (H2T buffer)
				
				// // check if buffer is full

				// // other program to read the data out
			
			}
			else
			{

				LOG_ERR("Unknown command %c%c", buf[0], buf[1]);

			}

			// wrote = ring_buf_put(rb, buf, read);
			// if (wrote < read)
			// {
			// 	LOG_ERR("Drop %zu bytes", read - wrote);
			// }

			// LOG_DBG("dev %p -> dev %p send %zu bytes",
			// 		dev, peer->dev, wrote);
			// if (wrote)
			// {
			// 	uart_irq_tx_enable(peer->dev);
			// }
		}

		if (uart_irq_tx_ready(dev))
		{
			uint8_t buf[256];
			size_t wrote, len;
			// get the data out from self.buffer (T2H buffer)
			len = ring_buf_get(&peer->data->rb, buf, sizeof(buf));
			if (!len)
			{
				LOG_DBG("dev2 %p T2H buffer empty", dev);
				uart_irq_tx_disable(dev);
			}
			else
			{
				wrote = uart_fifo_fill(dev, buf, len);

				if(wrote != 255)
				{
					LOG_ERR("dev2 %p sent len %zu bytes to host, potential data lost", dev, wrote);
				}
				else
				{
					LOG_INF("dev2 %p sent len %zu bytes to host", dev, wrote);
				}
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

void main(void)
{
	once = 1;
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
