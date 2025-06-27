import datetime
import http
import http.client
import json
import ssl
import threading
from multiprocessing.dummy import Pool
from termcolor import colored
from threading import BoundedSemaphore

payload_file_path = 'logs\\default_payload-test.txt'
with open(payload_file_path, 'r') as file:
    default_payload = file.read()
    print(f"Loaded payload from {payload_file_path}")
serverhostname = 'xxxx.yyyy.zzz.gov'
#serverport = '4000'
serverport = '9320'
cert_path_file = 'xxxxxx.crt'
key_path_file = 'yyyyyyy.key'
key_pass = None

#with open('xxxx-key', 'r') as file:
#    key_pass = file.read()

timeoutSetting = 30
poolsize = 75
http_context = ssl.create_default_context()
http_context.check_hostname = False
http_context.verify_mode = ssl.CERT_NONE
http_context.load_cert_chain(certfile=cert_path_file, keyfile=key_path_file, password=key_pass)
http_context.minimum_version = ssl.TLSVersion.TLSv1_2
http_context.maximum_version = ssl.TLSVersion.TLSv1_2
headers = {'Content-type': 'application/json'}
json_data = json.dumps({'payload_270': default_payload})

# Create a semaphore to track available threads
thread_semaphore = BoundedSemaphore(poolsize)  # Match your pool size

class ThreadSafeInt:
    """Thread-safe integer class."""
    def __init__(self, value=0):
        self.value = value
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.value += 1
            return self.value

    def decrement(self):
        with self.lock:
            self.value -= 1
            return self.value

    def get(self):
        with self.lock:
            return self.value

active_tasks = ThreadSafeInt(0)  # Add a counter for active tasks

unique_id = ThreadSafeInt(0)

failures = ThreadSafeInt(0)

def send270HTTP(payload = default_payload):
    """Send a 270 transaction to the HTTP server and log the transaction details."""
    timestamp_start = datetime.datetime.today()
    try:
        c = http.client.HTTPSConnection(
                serverhostname + ":" + str(serverport), 
                context=http_context, 
                timeout=timeoutSetting)
        c.connect()
        timestamp_connection_end = datetime.datetime.today()
        delta_connection = (timestamp_connection_end - timestamp_start).total_seconds()
        # Set up request
        headers = {'Content-type': 'application/json', 'Connection': 'keep-alive'}
        payload = payload[:6] + 'J' + str( unique_id.increment() ).zfill(5)[:5] + payload[12:]
        json_data = json.dumps({'payload_270': payload})
        # Send request
        c.request('POST', '/post', json_data, headers)
        response = c.getresponse()

        # Process response
        if isinstance(response, str):
            response_text = response
        else:
            response_text = (response.read().decode()).replace('\r', '').replace('\n', '')
        response_time = datetime.datetime.today()
        delta_response = (response_time - timestamp_connection_end).total_seconds()
        if 'AAA*Y**42*P' in response_text:
            print(f'🕑', end='', flush=True)
            failures.increment()
        elif 'AAA*Y**42*R' in response_text:
            print(f'👹', end='', flush=True)
            failures.increment()
        elif 'AAA*Y**33*R' in response_text:
            print(f'🌩️', end='', flush=True)
            failures.increment()
        elif 'AAA*Y**71*C' in response_text:
            print(f'👻', end='', flush=True)
            failures.increment()
        elif '502 Bad Gateway' in response_text:
            print(f'🤡', end='', flush=True)
            failures.increment()
        elif 'Cannot accept a connection at this time.' in response_text:
            print(f'🍟', end='', flush=True)
            failures.increment()
        elif '270 Error: EDI Fabric Timeout on 270 Parsing' in response_text:
            print(f'🍔', end='', flush=True)
            failures.increment()
        elif 'Health Check Passed' in response_text:
            print(f'😍', end='', flush=True)
        elif 'An error occurred while connecting to the 270 Service' in response_text:
            print(f'😰', end='', flush=True)
            failures.increment()
        elif len(response_text) < 100:
            print(f'💣{response_text}', end='', flush=True)
            failures.increment()
        else:
            print(f'✅', end='')
            if delta_response > 13 and delta_response < 20:
                print(colored(f'L{float(delta_connection):.1f},{float(delta_response):.1f}',"red"), end='', flush=True)
            if delta_response > 20 and delta_response < 30:
                print(colored(f'D{float(delta_connection):.1f},{float(delta_response):.1f}',"red"), end='', flush=True)
            if delta_response > 30 and delta_response < 60:
                print(colored(f'V{float(delta_connection):.1f},{float(delta_response):.1f}',"red"), end='', flush=True)
    
    except (ConnectionResetError):
        print(f'🦄', end='', flush=True)
        failures.increment()
    except (BrokenPipeError):
        print("🛹", end='', flush=True)
        failures.increment()
    except (ConnectionAbortedError):
        print("💀", end='', flush=True)
        failures.increment()
    except TimeoutError:
        print(f'🍄', end='')
        failures.increment()
    except Exception as e:
        print(colored(f'O[{type(e).__name__}: {str(e)}]', "yellow"), end='', flush=True)
        failures.increment()
    finally:
        try:
            c.close()
        except Exception as e:
            print(f'Connection close error: {e}', end='', flush=True)


def send270HTTP_with_tracking(payload=default_payload):
    try:
        active_tasks.increment()
        send270HTTP(payload)
    except Exception as e:
        print(e)
    finally:
        active_tasks.decrement()

wait_time = .12
with Pool(poolsize) as pool:
     threading.Event().wait(5)
     for i in range(1, 99999):
        pool.apply_async(send270HTTP_with_tracking)
        modu = 1000
        if (i % 50 == 0):
            print('', end='', flush=True)
        if (i % modu == 0):
            wait_time = max(.066, wait_time - .005)
            modu = modu + (1/wait_time * 3 * 60) # per second for 3 minutes
            section_time = datetime.datetime.today().strftime('%H:%M:%S')
            print(colored(f"\n{section_time} Wait time:{wait_time:.3f}, {1/wait_time:.1f} per second. send:{i-failures.get()}/{i}", color="cyan"), flush=True)
            print(colored(f"[{active_tasks.get()}/{poolsize}]", "blue"), end='', flush=True)
            failure_rate = (failures.get()/i)
            print(colored(f" Failure Rate: {failure_rate:.1%}", "red"), end='', flush=True)
        threading.Event().wait(wait_time)
threading.Event().wait(30)