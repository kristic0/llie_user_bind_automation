from netmiko import ConnectHandler
from netmiko.exceptions import AuthenticationException
import socket
import getpass

def check_ping(host):
    try:
        socket.create_connection((host, 80), timeout=1)
        return 0
    except (socket.timeout, OSError):
        return 1

def get_vlan(ip_address):
    vlan_mapping = {
        "192.168.88.0": "88",
        "192.168.89.0": "89",
        "192.168.90.0": "90",
        "192.168.91.0": "91",
        "192.168.92.0": "92",
        "192.168.93.0": "93",
        "192.168.94.0": "94",
        "192.168.95.0": "95",
        "10.1.70.0": "2000",
    }

    try:
        # Convert IP to a list of integers
        ip_parts = list(map(int, ip_address.split('.')))

        # Iterate through the mapping
        for base_network, vlan_offset in vlan_mapping.items():
            # Convert base network to a list of integers
            base_parts = list(map(int, base_network.split('.')))

            # Check if the IP address matches the base network
            if ip_parts[:3] == base_parts[:3]:
                return vlan_offset

        # If no match is found
        raise ValueError("No matching VLAN found for the given IP address.")
    except ValueError:
        raise ValueError(f"Invalid IP address format. The parameter was: {ip_address}")


def read_file(file_to_read):
    binding_data = []
    with open(file_to_read, 'r', encoding='utf-8') as file:
        file.readline() #skip line
        for line in file:
            data = line.strip().split('|')
            mac = data[7].strip()
            ip = data[8].strip()
            vlan = ''
            if mac != '' and ip != '':
                vlan = get_vlan(ip)
                binding_data.append([ip, mac, vlan])
    return binding_data


def send_command(ssh_conn, command):
    print("Executing: " + command)
    ssh_conn.send_command_timing(command, )


def send_out_command(ssh_conn, command):
    print("Executing: " + command)
    out = ssh_conn.send_command_timing(command)
    print(out)

def compare_with_switch(ssh_conn):
    command = "display dhcp static user-bind all"
    out = ssh_conn.send_command_timing(command)
    
    bound_users = []

    # Split the output where \n and remove first 7 elements and the last 2 elements
    lines = out.split("\n")[7:-2]
    for line in lines:
        l = line.split()
        bound_users.append([l[0], l[1], l[2]])

    return bound_users
    

def run_script(device, binding_data):
    try:
        print("Trying to connect to the switch!")
        # Connect to the device
        with ConnectHandler(**device) as ssh_conn:
            print(f"Connected to: {device['host']}:")
            
            binding_data_from_switch = compare_with_switch(ssh_conn)
            users_from_switch = {tuple(elem) for elem in binding_data_from_switch}
            users_from_list = {tuple(elem) for elem in binding_data}

            switch_minus_list = users_from_switch - users_from_list
            list_minus_switch = users_from_list - users_from_switch
          
            send_command(ssh_conn, "system-view")
            
            for user in list_minus_switch:
                command = f"user-bind static ip-address {user[0]} mac-address {user[1]} vlan {user[2]}"
                send_command(ssh_conn, command)

            for user in switch_minus_list:
                command = f"undo user-bind static ip-address {user[0]} mac-address {user[1]} vlan {user[2]}"
                send_command(ssh_conn, command)

            send_out_command(ssh_conn, "display dhcp static user-bind all")

    except AuthenticationException:
        print("Authentication failed. Please check your username and password.")
    except socket.timeout:
        print("Connection to the device timed out. Please check the device IP address and connectivity.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    device_info = { # or the appropriate device type
        'device_type': 'huawei',
        'host': "192.168.1.253",
        'username': '',
        'password': '',
        'secret': '',
        'port': 22,  # Change the port if your device uses a different one
    }

    try:
        if check_ping(device_info['host']) == 0:
            username = input("Enter the username: ")
            password = getpass.getpass("Enter your password: ")

            device_info['username'] = username
            device_info['password'] = password
            device_info['secret'] = password

            binding_data = read_file("finance_department.tsv")
            run_script(device_info, binding_data)
    except KeyboardInterrupt:
        print("\nCtrl+C detected. Exiting the script.")
        exit(0)

