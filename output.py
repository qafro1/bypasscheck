from colorama import Fore, Style
from fake_useragent import UserAgent
import requests
import argparse
import json
import sys

banner = r"""
___________         ___.   .__    .___  .___           
\_   _____/_________\_ |__ |__| __| _/__| _/____   ____
 |    __)/  _ \_  __ \ __ \|  |/ __ |/ __ |/ __ \ /    \
 |     \(  <_> )  | \/ \_\ \  / /_/ / /_/ \  ___/|   |  \ 
 \___  / \____/|__|  |___  /__\____ \____ |\___  >___|  /
     \/                  \/        \/    \/    \/     \/    v2.1

"""

print(Fore.CYAN + banner)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

group.add_argument('-p', '--path', action='store', type=str, help='path to check', metavar='domain.com')
parser.add_argument('-d', '--domains', action='store', help="domains to check", metavar="filename.txt")
parser.add_argument('-t', '--target', action='store', help="domain to check", metavar="site.com")
parser.add_argument('-f', '--file', action='store', help="file containing multiple API endpoints", metavar="endpoints.txt")
parser.add_argument('-o', '--output', action='store', help="output file path", metavar="output.txt")

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


def get_headers(path=None, method='GET'):
    headers = []
    # Read additional headers from lowercase-headers.txt file
    try:
        with open('lowercase-headers.txt', 'r') as f:
            lowercase_headers = [x.strip() for x in f.readlines()]
            for header in lowercase_headers:
                # Split header into name and value
                header_parts = header.split(':', 1)
                if len(header_parts) == 2:
                    name, value = header_parts
                    name = name.strip()
                    headers.append({'User-Agent': str(ua.chrome), name: value.strip()})
    except FileNotFoundError as fnf_err:
        print(f"FileNotFoundError: {fnf_err}")
        sys.exit(1)
    
    return headers


def do_request(url, stream=False, path=None, method='GET'):
    headers = get_headers(path=path, method=method)
    try:
        for header in headers:
            session = requests.Session()
            if stream:
                r = session.request(method, url, stream=True, headers=header)
            else:
                r = session.request(method, url, headers=header)
            if r.status_code == 200 or r.status_code >= 500:
                status_color = Fore.GREEN if r.status_code == 200 else Fore.RED
                result = f"{url} {json.dumps(list(header.items())[-1])} {status_color}[{r.status_code}]{Style.RESET_ALL}"
                print(result)
                if args.output:
                    with open(args.output, 'a') as f:
                        f.write(result + '\n')
    except requests.exceptions.RequestException as err:
        print("Some Ambiguous Exception:", err)


def main():
    bypass_list = read_wordlist("bypasses.txt")

    if args.domains:
        if args.path:
            print(Fore.CYAN + "Checking domains to bypass....")
            checklist = read_wordlist(args.domains)
            for line in checklist:
                for bypass in bypass_list:
                    links = f"{line}/{args.path}{bypass}"
                    do_request(links, stream=True, path=args.path)
        else:
            print(Fore.CYAN + "Checking domains to bypass....")
            checklist = read_wordlist(args.domains)
            for line in checklist:
                for bypass in bypass_list:
                    links = f"{line}{bypass}"
                    do_request(links, stream=True)
    elif args.file:
        if args.path:
            print(Fore.CYAN + "Checking endpoints to bypass....")
            endpoints = read_wordlist(args.file)
            for endpoint in endpoints:
                for bypass in bypass_list:
                    links = f"{endpoint}/{args.path}{bypass}"
                    do_request(links, stream=True, path=args.path)
        else:
            print(Fore.CYAN + "Checking endpoints to bypass....")
            endpoints = read_wordlist(args.file)
            for endpoint in endpoints:
                for bypass in bypass_list:
                    links = f"{endpoint}{bypass}"
                    do_request(links, stream=True)
    if args.target:
        if args.path:
            print(Fore.GREEN + f"Checking {args.target}...")
            for method in http_methods:
                for bypass in bypass_list:
                    links = f"{args.target}/{args.path}{bypass}"
                    do_request(links, path=args.path, method=method)
        else:
            print(Fore.GREEN + f"Checking {args.target}...")
            for method in http_methods:
                for bypass in bypass_list:
                    links = f"{args.target}{bypass}"
                    do_request(links, method=method)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
