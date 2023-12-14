import ctypes
import sys
import subprocess
import paramiko
import subprocess
import socket

class Net():
    vlan_mapping = {
        "192.168.88.0": 88,
        "192.168.89.0": 89,
        "192.168.90.0": 90,
        "192.168.91.0": 91,
        "192.168.92.0": 92,
        "192.168.93.0": 93,
        "192.168.94.0": 94,
        "192.168.95.0": 95,
        "10.1.70.0": 2000,
    }

    def check_ping(self, host):
        try:
            socket.create_connection((host, 80), timeout=1)
            return 0
        except (socket.timeout, OSError):
            return 1

    def get_vlan(self, ip_address):
        try:
            # Convert IP to a list of integers
            ip_parts = list(map(int, ip_address.split('.')))

            # Iterate through the mapping
            for base_network, vlan_offset in self.vlan_mapping.items():
                # Convert base network to a list of integers
                base_parts = list(map(int, base_network.split('.')))

                # Check if the IP address matches the base network
                if ip_parts[:3] == base_parts[:3]:
                    return vlan_offset

            # If no match is found
            raise ValueError("No matching VLAN found for the given IP address.")
        except ValueError:
            raise ValueError(f"Invalid IP address format. The parameter was: {ip_address}")


if __name__ == "__main__":
    hostname = '192.168.1.253' 
    port = 22
    binding_data = []
    net = Net()

    with open('finance_department.tsv', 'r', encoding='utf-8') as file:
        file.readline() #skip line
        for line in file:
            data = line.strip().split('|')
            mac = data[7].strip()
            ip = data[8].strip()
            vlan = ''
            if mac != '' and ip != '':
                vlan = net.get_vlan(ip)
                binding_data.append([mac, ip, vlan])

    # print(binding_data)
    # for user in binding_data:
    #     print(f"user-bind static ip-address {user[1]} mac-address {user[0]} vlan {user[2]}")

    # input("Press Enter to exit...")

    if net.check_ping(hostname) == 0:
        client = paramiko.SSHClient()
        # Automatically add the server's host key (WARNING: this is insecure in production)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            username = input("Username: ")
            password = input("Password: ")

            client.connect(hostname, port, username, password, timeout=10, allow_agent=False)
            channel = client.invoke_shell(width=1000, height=1000)

            # Start of commands
            channel.send("system-view" + '\n')

            for user in binding_data:
                channel.send(f"user-bind static ip-address {user[1]} mac-address {user[0]} vlan {user[2]}" + "\n")

            channel.send("\x1a")
            channel.send("save" + '\n')
            channel.send("y" + '\n')
            channel.send('\n')
            channel.send("quit")
            # End of commands
            channel.close()

            while not channel.exit_status_ready():
                # Read and print the output
                if channel.recv_ready():
                    output = channel.recv(4096).decode()
                    print(output, end='')
            
        finally:
            if not channel.closed:
                channel.close()
    else:
        print("The host might be down, if not, check your connection!")

    ### display dhcp static user-bind all ###