from colorama import Fore, Style
from fake_useragent import UserAgent
import concurrent.futures
import requests
import argparse
import sys
import json

banner = r"""
___________         ___.   .__    .___  .___           
\_   _____/_________\_ |__ |__| __| _/__| _/____   ____
 |    __)/  _ \_  __ \ __ \|  |/ __ |/ __ |/ __ \ /    \
 |     \(  <_> )  | \/ \_\ \  / /_/ / /_/ \  ___/|   |  \ 
 \___  / \____/|__|  |___  /__\____ \____ |\___  >___|  /
     \/                  \/        \/    \/    \/     \/    v0.1

"""

print(Fore.CYAN + banner)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

group.add_argument('-p', '--path', action='store', type=str, help='path to check', metavar='domain.com')

parser.add_argument('-d', '--domains', action='store', help="domains to check", metavar="filename.txt")

parser.add_argument('-t', '--target', action='store', help="domain to check", metavar="site.com")

parser.add_argument('-f', '--file', action='store', help="file containing multiple API endpoints", metavar="endpoints.txt")

args = parser.parse_args()

ua = UserAgent()

# List of HTTP verbs/methods to fuzz
http_methods = ['GET', 'HEAD', 'POST', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PUT', 'INVENTED']

def read_wordlist(wordlist):
    try:
        with open(wordlist, 'r') as f:
            return [x.strip() for x in f.readlines()]
    except FileNotFoundError as fnf_err:
        print(f"FileNotFoundError: {fnf_err}")
        sys.exit(1)


wordlist = read_wordlist("bypasses.txt")


def get_headers(path=None, method='GET'):
    headers = [
        {'User-Agent': str(ua.chrome), 'X-HTTP-Method-Override': method},
        {'User-Agent': str(ua.chrome), 'X-Original-URL': path or '/', 'X-HTTP-Method-Override': method},
        {'User-Agent': str(ua.chrome), 'X-Custom-IP-Authorization': '127.0.0.1', 'X-HTTP-Method-Override': method},
        # Add more headers with different combinations of HTTP verbs and other headers
    ]
    return headers


def do_request(url, stream=False, path=None, method='GET'):
    headers = get_headers(path=path, method=method)
    try:
        for header in headers:
            if stream:
                r = requests.request(method, url, stream=True, headers=header)
            else:
                r = requests.request(method, url, headers=header)
            if r.status_code == 200 or r.status_code == 500:
                status_color = Fore.GREEN if r.status_code == 200 else Fore.RED
                print(f"{Fore.WHITE}{url} {json.dumps(list(header.items())[-1])} {status_color}[{r.status_code}]{Style.RESET_ALL}")
    except requests.exceptions.RequestException as err:
        print("Some Ambiguous Exception:", err)


def main(wordlist):
    if args.domains:
        if args.path:
            print(Fore.CYAN + "Checking domains to bypass....")
            checklist = read_wordlist(args.domains)
            for line in checklist:
                for bypass in wordlist:
                    links = f"{line}/{args.path}{bypass}"
                    do_request(links, stream=True, path=args.path)
        else:
            print(Fore.CYAN + "Checking domains to bypass....")
            checklist = read_wordlist(args.domains)
            for line in checklist:
                for bypass in wordlist:
                    links = f"{line}{bypass}"
                    do_request(links, stream=True)
    elif args.file:
        if args.path:
            print(Fore.CYAN + "Checking endpoints to bypass....")
            endpoints = read_wordlist(args.file)
            for endpoint in endpoints:
                for bypass in wordlist:
                    links = f"{endpoint}/{args.path}{bypass}"
                    do_request(links, stream=True, path=args.path)
        else:
            print(Fore.CYAN + "Checking endpoints to bypass....")
            endpoints = read_wordlist(args.file)
            for endpoint in endpoints:
                for bypass in wordlist:
                    links = f"{endpoint}{bypass}"
                    do_request(links, stream=True)
    if args.target:
        if args.path:
            print(Fore.GREEN + f"Checking {args.target}...")
            for method in http_methods:
                for bypass in wordlist:
                    links = f"{args.target}/{args.path}{bypass}"
                    do_request(links, path=args.path, method=method)
        else:
            print(Fore.GREEN + f"Checking {args.target}...")
            for method in http_methods:
                for bypass in wordlist:
                    links = f"{args.target}{bypass}"
                    do_request(links, method=method)


if __name__ == "__main__":
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(main, wordlist)
    except KeyboardInterrupt:
        sys.exit(0)
