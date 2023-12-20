from netmiko import ConnectHandler
import socket

def get_vlan(ip_address):
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
    ssh_conn.send_command_timing(command)


def run_script(device, binding_data):
    try:
        # Connect to the device
        with ConnectHandler(**device) as ssh_conn:
            print(f"Executing command on {device['host']}:")
            send_command(ssh_conn, "system-view")
            for user in binding_data:
                command = f"undo user-bind static ip-address {user[0]} mac-address {user[1]} vlan {user[2]}"
                send_command(ssh_conn, command)

    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    hostname = '192.168.1.253' 
    port = 22

    device_info = {
        'device_type': 'huawei',  # or the appropriate device type
        'host': hostname,
        'username': 'admin',
        'password': 'Linglong123',
        'secret': 'Linglong123',
        'port': 22,  # Change the port if your device uses a different one
    }
    binding_data = read_file("finance_department.tsv")
    # print(binding_data)
    run_script(device_info, binding_data)

