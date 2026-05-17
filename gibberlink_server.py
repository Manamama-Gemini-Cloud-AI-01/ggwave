import subprocess
import time
import re
import os

LOG_FILE = "rx_logs.txt"

def transmit(message):
    print(f"Transmitting: {message}")
    # Run the transmitter
    process = subprocess.Popen(['./bin/ggwave-cli', '-p0'], stdin=subprocess.PIPE, text=True)
    process.communicate(input=message)

def run_gibberlink_server():
    print("Gibberlink Server Active: Waiting for ping...")
    # Clear the log file first
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()
        
    # Open the log file
    with open(LOG_FILE, "r") as f:
        f.seek(0, 2) # Go to end
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            
            # The exact "click" logic from the Gibberlink repo
            match = re.search(r"Received sound data successfully: '([^']+)'", line)
            if match:
                msg = match.group(1).strip().lower()
                print(f"Heard: {msg}")
                
                # The "Protocol" Logic (Ping -> Pong)
                if "ping" in msg:
                    try:
                        num = int(msg.split()[-1])
                        response = f"pong {num + 1}"
                        print(f"Server replied: {response}")
                        transmit(response)
                    except Exception as e:
                        print(f"Error parsing ping: {e}")

if __name__ == "__main__":
    run_gibberlink_server()
