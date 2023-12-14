import ctypes
import sys
import subprocess
import paramiko
import subprocess
import socket

# Create an SSH client
client = paramiko.SSHClient()

try:
    # Automatically add the server's host key (this is insecure; see the warning below)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    client.connect(hostname, port, username, password)

    # Execute 'ls' command
    print("Executing 'ls' command:")
    stdin, stdout, stderr = client.exec_command("ls")
    print(stdout.read().decode())

    # Execute 'ps' command
    print("\nExecuting 'ps' command:")
    stdin, stdout, stderr = client.exec_command("ps")
    print(stdout.read().decode())

except Exception as e:
    print(f"Error: {e}")
finally:
    # Close the SSH connection
    client.close()