import network
import socket
import machine
import time

# Configure Wi-Fi
SSID = "Archismans23fe"
PASSWORD = "archisman2004"

# Configure Relay
RELAY_PIN = 2
relay = machine.Pin(RELAY_PIN, machine.Pin.OUT)

# Set relay to default state (ON)
relay.value(1)  # Assume active-low relay; set HIGH to keep it ON initially

# Flag to track the state of the system
last_trigger = None  # Tracks the last trigger received
permanent_stop = False  # Flag to indicate if the relay should be stopped permanently

def connect_to_wifi():
    """
    Connects to Wi-Fi.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        pass
    print("Connected! IP address:", wlan.ifconfig()[0])

def handle_trigger(request):
    """
    Handles triggers based on the received HTTP request.
    """
    global last_trigger, permanent_stop

    if "TRIGGER1" in request:
        print("TRIGGER1 received! Turning ON the relay.")
        relay.value(0)  # Turn ON the relay (LOW for active-low relay)
        last_trigger = "TRIGGER1"
        permanent_stop = False  # Reset permanent stop if TRIGGER1 is received

    elif "TRIGGER2" in request:
        print("TRIGGER2 received! Turning OFF the relay.")
        relay.value(1)  # Turn OFF the relay (HIGH for active-low relay)
        last_trigger = "TRIGGER2"

        # First wait for 10 seconds
        print("Waiting 10 seconds for another TRIGGER2...")
        time.sleep(10)  # Wait for 10 seconds

        if last_trigger != "TRIGGER2":
            print("No additional TRIGGER2 received in 10 seconds. Turning ON the relay again.")
            relay.value(0)  # Turn ON the relay (LOW for active-low relay)
        else:
            # Enter 30-second waiting period
            print("Another TRIGGER2 received! Waiting 30 seconds...")
            time.sleep(30)  # Wait for 30 seconds

            if last_trigger != "TRIGGER2":
                print("No additional TRIGGER2 received in 30 seconds. Turning ON the relay again.")
                relay.value(0)  # Turn ON the relay (LOW for active-low relay)
            else:
                # Stop the relay permanently
                print("Another TRIGGER2 received within 30 seconds. Stopping relay permanently.")
                permanent_stop = True
                relay.value(1)  # Keep relay OFF (HIGH for active-low relay)
    else:
        print("Unknown request. Relay state unchanged.")

def start_server():
    """
    Starts the HTTP server to listen for incoming requests.
    Controls the relay based on received trigger messages.
    """
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    server = socket.socket()
    server.bind(addr)
    server.listen(1)
    print("Server listening on", addr)

    while True:
        conn, client_addr = server.accept()
        print("Connection from", client_addr)
        request = conn.recv(1024).decode("utf-8")
        print("Request received:", request)
        
        if not permanent_stop:  # Check if the relay is permanently stopped
            handle_trigger(request)
        else:
            print("Relay permanently stopped. Ignoring all triggers.")

        # Send an HTTP response
        response = "HTTP/1.1 200 OK\nContent-Type: text/plain\n\nAcknowledged"
        conn.send(response.encode("utf-8"))
        conn.close()

# Main script
connect_to_wifi()
start_server()