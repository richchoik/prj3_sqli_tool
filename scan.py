import requests
import time
from bs4 import BeautifulSoup
import tunqli


wordlist = [
    "success", "successful", "completed", "submitted", "thank you",
    "your submission", "has been received", "confirmation", "congratulations",
    "done", "finished", "saved", "accepted", "approved", "validated", "verified",
    "successful", "succeeded", "passed", "sent", "message received", "we received",
    "thank", "wellcome", "hi", "hello", "200", "xin chào", "chào mừng", "bắt đầu", "thành công"
]

s = requests.Session()

def scan_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return ["[✔]\tThis URL is verified", "1"]
        else:
            return ["[✖]\tThis URL cannot be verified", "0"]
    except requests.RequestException:
        return ["[✖]\tThis URL cannot be verified", "0"]


def get_forms(url):
    soup = BeautifulSoup(s.get(url).content, "html.parser")
    return soup.find_all("form")

#Trích xuất chi tiết form
def form_details(form):
    detailOfForm = {}
    action = form.attrs.get("action")
    method = form.attrs.get("method", "get")
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({
            "type": input_type,
            "name": input_name,
            "value": input_value
        })
    detailOfForm['action'] = action
    detailOfForm['method'] = method
    detailOfForm['inputs'] = inputs
    return detailOfForm

#in đẹp
def print_pretty_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    pretty_html = soup.prettify()
    print(pretty_html)

#quét
def scan_vulnerability(url, mode='Custom'):
    all_forms = get_forms(url)
    for i in range(len(all_forms)):
        Form = all_forms[i]
        formDetail = form_details(Form)
        method = formDetail['method'].lower()
        print(f"FORM {i + 1}:\t{method}")

        for input_tag in formDetail["inputs"]:
            print(f" -{input_tag['name']}")

        #Mode Time-based
        if mode == 'Time Based':
            with open('timeBasedPayload.txt', 'r') as filepayload:
                cntline = 0
                for line in filepayload:
                    cntline += 1
                    line = line.rstrip('\n')
                    for input_tag in formDetail["inputs"]:
                        data = {input_tag['name']: input_tag["value"] + line}
                    try:
                        if method == "post":
                            res = requests.post(url, data=data, timeout=6)
                        elif method == "get":
                            res = requests.get(url, params=data, timeout=6)
                        timeres = res.elapsed.total_seconds()
                        if timeres > 5:
                            print(f'\r', end='', flush=True)
                            print(f"executed with payload: {line}\ttime to response: {timeres}")
                    except requests.exceptions.Timeout:
                        print(f'\r', end='', flush=True)
                        print(f"maybe execute with payload: {line}\t time out: 6")
                    print(f'\rLOADING [{cntline}/98]', end='', flush=True)
                print(f'\rDONE')

        #Mode normal
        if mode == 'Normal':
            with open('normalPayload.txt', 'r') as filepayload:
                cntline = 0
                for line in filepayload:
                    cntcase = 0
                    cntline += 1
                    line = line.rstrip('\n')
                    data = {}  # Khởi tạo lại data cho mỗi payload
                    print(f'\rLOADING [{cntline}/155]', end='', flush=True)
                    for input_tag in formDetail["inputs"]:
                        data[input_tag['name']] = input_tag["value"] + line  # Cập nhật data thay vì ghi đè
                        #print(data)
                        print()
                    if method == "post":
                        res = requests.post(url, data=data)
                        #print(f"Payload: {data}")
                        #print(f"Response Status Code: {res.status_code}")
                        #print_pretty_html(res.content)
                        #print()
                    elif method == "get":
                        res = requests.get(url, params=data)
                        #print(f"Payload: {data}")
                        #print(f"Response Status Code: {res.status_code}")
                        #print_pretty_html(res.content)
                        #print()
                    if 200 <= res.status_code < 300:
                        cntcase += 1
                    for word in wordlist:
                        if word in res.text.lower():
                            cntcase += 1
                            break
                    if cntcase >= 2:
                        print(f'\r', end='', flush=True)
                        print(f"executed with payload: {line}\tresponse code: {res.status_code}")
                        break
                    elif cntcase == 1:
                        print(f'\r', end='', flush=True)
                        print(f"may be execute with payload: {line}\tresponse code: {res.status_code}")
                        break
                print()
                print(f'\rDONE')
            with open('banner.txt', 'r') as file:
                content = file.read()
            print(content)

        #Mode custom
        if mode == 'Custom':
            header = []
            print('CUSTOM')
            while True:
                userinput = input("input tag: ")
                if userinput == "":
                    break
                header.append(userinput)
            with open('normalPayload.txt', 'r') as filepayload:
                cntline = 0
                for line in filepayload:
                    cntcase = 0
                    cntline += 1
                    line = line.rstrip('\n')
                    for h in header:
                        data = {h: line}
                    res = requests.post(url, data=data, allow_redirects=False)
                    if 300 <= res.status_code < 400:
                        cntcase += 1
                    for word in wordlist:
                        if word in res.text.lower():
                            cntcase += 1
                            break
                    if cntcase >= 2:
                        print(f'\r', end='', flush=True)
                        print(f"executed with payload: {line}\tresponse code:  {res.status_code}")
                    elif cntcase == 1:
                        print(f'\r', end='', flush=True)
                        print(f"may be execute with payload: {line}\tresponse code:  {res.status_code}")
                    print(f'\rLOADING [{cntline}/154]', end='', flush=True)

            with open('timeBasedPayLoad.txt', 'r') as filepayload:
                cntline = 0
                for line in filepayload:
                    cntline += 1
                    line = line.rstrip('\n')
                    for h in header:
                        data = {h: line}
                    try:
                        res = requests.post(url, data=data, timeout=6)
                        timeres = res.elapsed.total_seconds()
                        if timeres > 5:
                            print(f'\r', end='', flush=True)
                            print(f"executed with payload: {line}\ttime to response: {timeres}")
                    except requests.exceptions.Timeout:
                        print(f'\r', end='', flush=True)
                        print(f"maybe execute with payload: {line}\t time out: 6")
                    print(f'\rLOADING [{cntline}/98]', end='', flush=True)
            print(f'\rDONE')