import socket
import threading
import logging
from queue import Queue

# Configure logging
logging.basicConfig(
    filename="scan_results.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# Thread-safe print lock
print_lock = threading.Lock()

# Queue for ports
port_queue = Queue()


def scan_port(host, port):
    """
    Scan a single TCP port.
    """

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        result = sock.connect_ex((host, port))

        with print_lock:
            if result == 0:
                print(f"[OPEN] Port {port}")
                logging.info(f"OPEN - Port {port}")

            elif result == 111:
                print(f"[CLOSED] Port {port}")
                logging.info(f"CLOSED - Port {port}")

            else:
                print(f"[TIMEOUT/FILTERED] Port {port}")
                logging.info(f"TIMEOUT/FILTERED - Port {port}")

        sock.close()

    except socket.gaierror:
        print("[ERROR] Hostname could not be resolved.")

    except socket.timeout:
        print(f"[TIMEOUT] Port {port}")

    except Exception as e:
        print(f"[ERROR] Port {port}: {e}")


def worker(host):
    while not port_queue.empty():
        port = port_queue.get()
        scan_port(host, port)
        port_queue.task_done()


def main():

    print("=" * 50)
    print("TCP PORT SCANNER")
    print("=" * 50)

    host = input("Enter target host/IP: ")

    start_port = int(input("Start Port: "))
    end_port = int(input("End Port: "))

    num_threads = 50

    print(f"\nScanning {host}")
    print(f"Port Range: {start_port}-{end_port}")
    print("-" * 50)

    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    threads = []

    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(host,))
        t.daemon = True
        t.start()
        threads.append(t)

    port_queue.join()

    print("\nScan Completed.")
    print("Results saved to scan_results.log")


if __name__ == "__main__":
    main()