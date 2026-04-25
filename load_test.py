import requests
import time
from concurrent.futures import ThreadPoolExecutor

API_URL = "https://3nntrph2z3.execute-api.ap-southeast-2.amazonaws.com/prod/parcels"
API_KEY = "UNIYaxUThoibZQqp6Lhi3JUsP3gzcdCaAuqjp3r5"

headers = {
    "x-api-key": API_KEY,
    "X-User-Role": "driver",
    "Content-Type": "application/json"
}

def send_request(i):
    data = {
        "sender": f"LoadUser{i}",
        "receiver": f"LoadReceiver{i}",
        "address": "Dubai",
        "email": "20210001364@students.cud.ac.ae"
    }

    for attempt in range(3):
        r = requests.post(API_URL, json=data, headers=headers)
        if r.status_code == 201:
            return 201
        time.sleep(0.3)

    print("Failed request", i, r.status_code, r.text)
    return r.status_code

start = time.time()

with ThreadPoolExecutor(max_workers=20) as executor:
    results = list(executor.map(send_request, range(20)))

end = time.time()

print("Results:", results)
print("Success count:", results.count(201))
print("Total time:", end - start)
print("Average response time:", (end - start) / 20)

