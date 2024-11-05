import requests
from bs4 import BeautifulSoup
import argparse
from urllib.parse import urljoin

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

def is_suspected_password(response_content):
    """Kiểm tra nếu nội dung phản hồi có thể chứa thông tin nhạy cảm như mật khẩu"""
    keywords = ["password", "admin", "login", "username"]
    for keyword in keywords:
        if keyword in response_content.lower():
            return True
    return False

def scan_sql_injection(url):
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
                print(f"[-] {url} có thể bị lỗ hổng SQL Injection với payload: {payload} bằng phương thức {form_details['method'].upper()}")
                
            if is_suspected_password(response_content):
                print(f"[+] Nghi ngờ rằng form này hoặc thẻ input này có thể chứa thông tin nhạy cảm như mật khẩu của admin.")
                print(form_details)
    
    print(f"[+] Kết thúc kiểm tra lỗ hổng SQL Injection trên {url}")

# Hàm chính để thiết lập CLI
def main():
    parser = argparse.ArgumentParser(description="Công cụ quét lỗ hổng SQL Injection đơn giản")
    parser.add_argument("url", help="URL của trang web cần quét")
    args = parser.parse_args()
    url = args.url
    scan_sql_injection(url)

if __name__ == "__main__":
    main()
