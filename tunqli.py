import requests
from bs4 import BeautifulSoup
import argparse
import scan


# MESSAGE
WARNING_MESSAGE = f"[warning]\t"
ERROR_MESSAGE = f"[error]\t"
INFO_MESSAGE = f"[info]\t"

#Lấy đầu vào
def get_input(prompt):
    try:
        user_input = input(prompt)
        args = user_input.split()
        if args[0] != 'tqli':
            return None
        return args
    except Exception as e:
        print(f"[Error]: {e}")
        return None

#Banner cho đẹp
def banner_func():
    with open('banner.txt', 'r') as file:
        content = file.read()
    print(content)

#Hàm help
def help_func():
    with open('help.txt', 'r') as file:
        content = file.read()
    print(content)

#Hàm scan
def scan_func():
    url = None
    # Verify URL
    while True:
        url = input("\turl:\t")
        resScan = scan.scan_url(url)
        print("\t" + resScan[0])
        if resScan[1] == "1":
            break

    # Choose MODE
    while True:
        try:
            with open('modeChoosing.txt', 'r') as file:
                content = file.read()
            print(content)
            n_mode = int(input("\tMode\t > "))
            if n_mode == 1:
                #Mode bình thường
                print("\t" + INFO_MESSAGE + "Mode: NORMAL")
                scan.scan_vulnerability(url, 'Normal')
                break
            elif n_mode == 2:
                #Mode Time-based
                print("\t" + INFO_MESSAGE + "Mode: Time Based")
                scan.scan_vulnerability(url, 'Time Based')
                break
            elif n_mode == 3:
                #Mode Custom
                print("\t" + INFO_MESSAGE + "Mode: Custom")
                scan.scan_vulnerability(url, 'Custom')
            elif n_mode == 4:
                print("\t" + INFO_MESSAGE + "Mode: Custom")
                scan.scan_vulnerability(url, 'Error Based')
            elif n_mode == 5:
                print("\t" + INFO_MESSAGE + "Mode: Blind")
                scan.scan_vulnerability(url, 'Blind')
        except ValueError:
            print("\t" + WARNING_MESSAGE + "Invalid mode. Please choose again.")
            continue

    return


# Hàm chính để thiết lập CLI
def main():
    banner_func()
    while True:
        userinput = get_input(" >> ")
        if userinput is None:
            print(ERROR_MESSAGE + "\tundefined syntax")
            continue
        else:
            if userinput[1] == '-help':
                help_func()
            elif userinput[1] == '-scan':
                scan_func()
            elif userinput[1] == '-detect':
                print(INFO_MESSAGE + "\tnot available now")
            elif userinput[1] == '-exit':
                break
            else:
                print(ERROR_MESSAGE + "\tundefined option")

if __name__ == "__main__":
    main()