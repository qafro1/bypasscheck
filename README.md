# bypassCheck
Bypass 401 &amp; 403 and scans multiple endpoints only output 200 or 500   


INSTALLATION


git clone https://github.com/gotr00t0day/forbiddenpass.git

cd forbiddenpass

pip3 install -r requirements.txt

python3 forbiddenpass.py -h

USAGE


___________         ___.   .__    .___  .___           __________                                        
\_   _____/_________\_ |__ |__| __| _/__| _/____   ____\                
 |    __)/  _ \_  __ \ __ \|  |/ __ |/ __ |/ __ \ /    \|           
 |     \(  <_> )  | \/ \_\ \  / /_/ / /_/ \  ___/|   |  \                   
 \___  / \____/|__|  |___  /__\____ \____ |\___  >___|  /               
     \/                  \/        \/    \/    \/     \/   v0.1           
                                                                                                         
                                                                                                         
                                                                                                         
usage: forbiddenpass.py [-h] [-p domain.com] [-d filename.txt] [-t site.com]                             
                                                                                                         
optional arguments:                                                                                      
  -h, --help            show this help message and exit                                                  
  -f filename.txt       scan multipule endpoints
  -p domain.com, --path domain.com                                                                       
                        path to check                                                                    
  -d filename.txt, --domains filename.txt                                                                
                        domains to check                                                                 
  -t site.com, --target site.com                                                                         
                        domain to check 
                        
                        
EXAMPLE

scan  multi endpoints target

python filename.py -f endpoints.txt

domains to check

python3 forbiddenpass.py -d domains.txt

domains to check with a path

python3 forbiddenpass.py -d domains.txt --path login

scan a single target with a path

python3 forbiddenpass.py -t https://site --path login

DISCLAIMER

inspired by https://github.com/gotr00t0day/forbiddenpass
 
