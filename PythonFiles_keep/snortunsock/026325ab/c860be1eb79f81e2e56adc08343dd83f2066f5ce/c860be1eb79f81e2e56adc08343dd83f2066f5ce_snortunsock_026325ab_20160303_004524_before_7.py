from snort_socket import snort_listener

# snort_listener.start_recv()

for i in snort_listener.start_recv():
    print(i)
