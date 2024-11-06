import requests
from bs4 import BeautifulSoup
import argparse
from urllib.parse import urlparse, parse_qs, urljoin
from pprint import pprint

# Hàm để trích xuất toàn bộ thẻ form từ một trang web
def extract_forms(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find_all('form')

# Hàm để trích xuất thẻ input có kiểu text hoặc password
def extract_text_and_password_inputs(forms):
    inputs = []
    for form in forms:
        for input_tag in form.find_all('input'):
            input_type = input_tag.attrs.get('type', 'text')
            if input_type in ['text', 'password']:
                inputs.append(input_tag)
    return inputs

# Hàm để trích xuất chi tiết form
def get_form_details(form):
    details = {}
    action = form.attrs.get('action')
    if action:
        action = action.lower()
    else:
        action = ''
    method = form.attrs.get('method', 'get').lower()
    inputs = []
    for input_tag in form.find_all('input'):
        input_name = input_tag.attrs.get('name')
        input_type = input_tag.attrs.get('type', 'text')
        inputs.append({'name': input_name, 'type': input_type})
    details['action'] = action
    details['method'] = method
    details['inputs'] = inputs
    return details

# Hàm để gửi payload SQL Injection
def submit_form(form_details, url, payload):
    target_url = urljoin(url, form_details['action'])
    data = {input_tag['name']: payload for input_tag in form_details['inputs'] if input_tag['type'] == 'text' or input_tag['type'] == 'password'}
    if form_details['method'] == 'post':
        return requests.post(target_url, data=data)
    else:
        return requests.get(target_url, params=data)

# Hàm để đọc các payload từ tệp
def read_payloads(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Hàm để kiểm tra lỗ hổng SQL Injection với phương thức GET
def GET_method(url):
    forms = extract_forms(url)
    print(f"[+] Đã tìm thấy {len(forms)} form trên {url}.")
    sql_payloads = read_payloads('payload.txt')  # Đọc payload từ tệp payload.txt
    original_response = requests.get(url).content.decode().lower()
    
    for form in forms:
        form_details = get_form_details(form)
        for payload in sql_payloads:
            response = submit_form(form_details, url, payload)
            response_content = response.content.decode().lower()
            if "error" in response_content or "syntax" in response_content or response_content != original_response:
                print(f"[-] {url} có thể bị lỗ hổng SQL Injection với payload: {payload} bằng phương thức GET")
            elif response_content != original_response:
                print(f"[+] Nghi ngờ rằng form này hoặc thẻ input này có thể chứa thông tin nhạy cảm.")
                pprint(form_details)
                
    print(f"[+] Kết thúc kiểm tra lỗ hổng SQL Injection trên {url} bằng phương thức GET")

# Hàm để kiểm tra lỗ hổng SQL Injection với phương thức POST
def POST_method(url):
    forms = extract_forms(url)
    print(f"[+] Đã tìm thấy {len(forms)} form trên {url}.")
    sql_payloads = read_payloads('payload.txt')  # Đọc payload từ tệp payload.txt
    original_response = requests.get(url).content.decode().lower()
    
    for form in forms:
        form_details = get_form_details(form)
        for payload in sql_payloads:
            form_details['method'] = 'post'  # Đặt phương thức thành POST
            response = submit_form(form_details, url, payload)
            response_content = response.content.decode().lower()
            if "error" in response_content or "syntax" in response_content or response_content != original_response:
                print(f"[-] {url} có thể bị lỗ hổng SQL Injection với payload: {payload} bằng phương thức POST")
            elif response_content != original_response:
                print(f"[+] Nghi ngờ rằng form này hoặc thẻ input này có thể chứa thông tin nhạy cảm.")
                pprint(form_details)
                
    print(f"[+] Kết thúc kiểm tra lỗ hổng SQL Injection trên {url} bằng phương thức POST")

# Hàm để trích xuất và in ra các tham số từ URL
def extract_params(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href = True)
    params = set()

    for link in links:
        href = link['href']
        if '?' in href:
            parsed_url = urlparse(href)
            query_params = parse_qs(parsed_url.query)
            for param in query_params:
                params.add(param)
    
    return params

# Hàm chính để thiết lập CLI
def main():
    parser = argparse.ArgumentParser(description="Công cụ quét lỗ hổng SQL Injection đơn giản")
    parser.add_argument("-u", "--url", required=True, help="URL của trang web cần quét")
    args = parser.parse_args()
    url = args.url
    
    # In ra các tham số từ URL
    params = extract_params(url)
    print("Các tham số từ URL:")
    pprint(params)
    
    method = input("Bạn chọn phương thức nào? Get(G) hay Post(P): ").strip().lower()
    if method == 'g':
        GET_method(url)
    elif method == 'p':
        POST_method(url)
    else:
        print("Phương thức không hợp lệ, vui lòng chọn G (Get) hoặc P (Post).")

if __name__ == "__main__":
    main()
