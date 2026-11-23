int uart_send(int); int crc(int); int odd(void); int other_uart(void); int start_val(void);
int main(void){ return uart_send(1)+crc(2)+odd()+other_uart()+start_val(); }
