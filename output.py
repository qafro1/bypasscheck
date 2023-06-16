from colorama import Fore, Style
from fake_useragent import UserAgent
import requests
import argparse
import sys


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
    try:
        with open("lowercase-headers.txt") as file_in:
            return [line.strip() for line in file_in.readlines()]
    except FileNotFoundError as fnf_err:
        print(f"FileNotFoundError: {fnf_err}")
        sys.exit(1)


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
                result = f"{url} {header} {status_color}[{r.status_code}]{Style.RESET_ALL}"
                print(result)
                if args.output:
                    with open(args.output, 'a') as f:
                        f.write(result + '\n')
    except requests.exceptions.RequestException as err:
        print("Some Ambiguous Exception:", err)


def main():
    bypass_list = read_wordlist("bypasses.txt")

    if args.domains:
        print(Fore.CYAN + "Checking domains to bypass....")
        checklist = read_wordlist(args.domains)
        for line in checklist:
            for bypass in bypass_list:
                links = f"{line}/{args.path}" if args.path else f"{line}"
                do_request(links, stream=True, path=args.path)
    elif args.file:
        print(Fore.CYAN + "Checking endpoints to bypass....")
        endpoints = read_wordlist(args.file)
        for endpoint in endpoints:
            for bypass in bypass_list:
                links = f"{endpoint}/{args.path}" if args.path else f"{endpoint}"
                do_request(links, stream=True, path=args.path)
    elif args.target:
        print(Fore.GREEN + f"Checking {args.target}...")
        for method in http_methods:
            for bypass in bypass_list:
                links = f"{args.target}/{args.path}" if args.path else f"{args.target}"
                do_request(links, path=args.path, method=method)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
