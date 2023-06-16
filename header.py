import concurrent.futures
import requests
import argparse
import sys
import json
from colorama import Fore, Style
from fake_useragent import UserAgent

banner = r"""
___________         ___.   .__    .___  .___           
\_   _____/_________\_ |__ |__| __| _/__| _/____   ____
 |    __)/  _ \_  __ \ __ \|  |/ __ |/ __ |/ __ \ /    \
 |     \(  <_> )  | \/ \_\ \  / /_/ / /_/ \  ___/|   |  \ 
 \___  / \____/|__|  |___  /__\____ \____ |\___  >___|  /
     \/                  \/        \/    \/    \/     \/    v0.03

"""

print(Fore.CYAN + banner)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument('-p', '--path', action='store', type=str, help='path to check', metavar='domain.com')
parser.add_argument('-d', '--domains', action='store', help="domains to check", metavar="filename.txt")
parser.add_argument('-t', '--target', action='store', help="domain to check", metavar="site.com")
parser.add_argument('-f', '--file', action='store', help="file containing multiple API endpoints", metavar="endpoints.txt")
parser.add_argument('-o', '--output', action='store', help="output file path", metavar="output.txt")
args = parser.parse_args()

ua = UserAgent()

# List of HTTP verbs/methods to fuzz
http_methods = ['GET', 'HEAD', 'POST', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PUT', 'INVENTED']


def read_bypasses(wordlist):
    try:
        with open(wordlist, 'r') as f:
            return [x.strip() for x in f.readlines()]
    except FileNotFoundError as fnf_err:
        print(f"FileNotFoundError: {fnf_err}")
        sys.exit(1)


bypasses = read_bypasses("bypasses.txt")


def get_headers(path=None, method='GET'):
    headers = [
        {'User-Agent': str(ua.chrome), 'X-Original-URL': path or '/'},
        {'User-Agent': str(ua.chrome), 'X-Custom-IP-Authorization': '127.0.0.1', 'X-HTTP-Method-Override': method},
        # Add more headers with different combinations of HTTP verbs and other headers
    ]

    # Read additional headers from the file
    try:
        with open('lowercase-headers.txt', 'r') as f:
            additional_headers = [header.strip() for header in f.readlines()]

            # Add the additional headers to the list
            headers.extend({'Additional-Header': header} for header in additional_headers)
    except FileNotFoundError as fnf_err:
        print(f"FileNotFoundError: {fnf_err}")
        sys.exit(1)

    return headers


def do_request(url, stream=False, path=None, method='GET'):
    headers = get_headers(path=path, method=method)
    try:
        for header in headers:
            if stream:
                r = requests.request(method, url, stream=True, headers=header)
            else:
                r = requests.request(method, url, headers=header)
            if r.status_code == 200 or r.status_code >= 500:
                status_color = Fore.GREEN if r.status_code == 200 else Fore.RED
                print(
                    f"{Fore.WHITE}{url} {json.dumps(list(header.items())[-1])} {status_color}[{r.status_code}]{Style.RESET_ALL}")
    except requests.exceptions.RequestException as err:
        print("Some Ambiguous Exception:", err)


def check_urls(targets, path=None):
    print(Fore.CYAN + f"Checking {targets}...")
    for target in targets:
        for method in http_methods:
            for bypass in bypasses:
                links = f"{target}/{path}{bypass}"
                do_request(links, path=path, method=method)


def main():
    if args.domains:
        if args.path:
            print(Fore.CYAN + "Checking domains to bypass....")
            checklist = read_bypasses(args.domains)
            check_urls(checklist, path=args.path)
        else:
            print(Fore.CYAN + "Checking domains to bypass....")
            checklist = read_bypasses(args.domains)
            check_urls(checklist)
    elif args.file:
        if args.path:
            print(Fore.CYAN + "Checking endpoints to bypass....")
            endpoints = read_bypasses(args.file)
            check_urls(endpoints, path=args.path)
        else:
            print(Fore.CYAN + "Checking endpoints to bypass....")
            endpoints = read_bypasses(args.file)
            check_urls(endpoints)
    if args.target:
        if args.path:
            check_urls([args.target], path=args.path)
        else:
            check_urls([args.target])


if __name__ == "__main__":
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(main)
    except KeyboardInterrupt:
        sys.exit(0)
