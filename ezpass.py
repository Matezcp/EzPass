import base64
import os
import pwinput
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Setup
#Choose a secret and put it in a file name "SECRET.KEY"
with open("SECRET.KEY",'r') as f:
    secret = f.read()

secret = bytes(secret,'utf-8')

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=secret,
    iterations=390000,
)


#Get universal pass or if it's the first time set the universal pass
try:
    f = open("passwords.bin",'rb')

    master_pass = pwinput.pwinput(prompt="Enter the universal password:")
    master_pass_bytes = bytes(master_pass,'utf-8')

    #Prepare Fernet
    key = base64.urlsafe_b64encode(kdf.derive(master_pass_bytes))
    encoder = Fernet(key)

    #Verify if master_pass is correct
    verification = f.readlines()[0].rstrip()
    try:
        encoder.decrypt(verification)
    except InvalidToken as e:
        print(f"{bcolors.FAIL}Incorrect Password{bcolors.ENDC}")
        f.close()
        quit()


except FileNotFoundError:
    print("Set your universal password!")
    answer = 'N'
    while answer == 'N':
        master_pass = input("Enter the universal password:")
        answer = input(f"You really want your universal password to be: {master_pass} (Y/N)\n")
    
    f = open("passwords.bin",'wb')
    master_pass_bytes = bytes(master_pass,'utf-8')

    #Prepare Fernet
    key = base64.urlsafe_b64encode(kdf.derive(master_pass_bytes))
    encoder = Fernet(key)

    f.write(encoder.encrypt(master_pass_bytes) + b'\n')
finally:
    os.system('cls' if os.name == 'nt' else 'clear')
    f.close()


#Add new passwords
def add():
    name = input('Account name:')
    pwd = input('Account password:')
    os.system('cls' if os.name == 'nt' else 'clear')

    with open('passwords.bin','ab') as f:
        name_bytes = bytes(name,'utf-8')
        pwd_bytes = bytes(pwd,'utf-8')
        f.write(encoder.encrypt(name_bytes) + b"|" + encoder.encrypt(pwd_bytes) + b'\n')
    
    print(f"{bcolors.OKCYAN}successfully added{bcolors().ENDC}")

#View existing passwords:
def view():
    with open('passwords.bin','rb') as f:

        lines = f.readlines()
        
        if len(lines) <= 1:
            print(f"{bcolors.WARNING}No Passwords Found{bcolors.ENDC}")
            return

        print("==========================================================================")
        #Skip first Line
        for i,line in enumerate(lines[1:]):
            data = line.rstrip()
            name, pwd = data.split(b"|")
            print(f"{bcolors.HEADER}({i}){bcolors.ENDC} Name: {(encoder.decrypt(name)).decode('utf-8')} || Password: {(encoder.decrypt(pwd)).decode('utf-8')}")
    print("==========================================================================")
    input("Press any button to continue\n")
    os.system('cls' if os.name == 'nt' else 'clear')


#Edit a existing password
def edit():
    lines = []
    with open('passwords.bin','rb') as f:
        i = 0
        lines = f.readlines()

        if len(lines) <= 1:
            print(f"{bcolors.WARNING}No Passwords Found{bcolors.ENDC}")
            return

        print("Which password would you like to edit:")
        #Skip first Line
        for line in lines[1:]:
            data = line.rstrip()
            name, pwd = data.split(b"|")
            print(f"({i}) Name: {(encoder.decrypt(name)).decode('utf-8')} || Password: {(encoder.decrypt(pwd)).decode('utf-8')}")
            i += 1


    selected = input()
    os.system('cls' if os.name == 'nt' else 'clear')
    valid = True

    try:
        selected = int(selected)
        if selected > (len(lines[1:]) - 1):
            valid = False
    except ValueError:
        valid = False

    if not valid:
        print(f"{bcolors.FAIL}Invalid Option{bcolors.ENDC}")
    else:
        invalid = True
        while invalid:
            action = input("Would you like to:\n(0) Change the name\n(1) Change the password\n(2) Change the name and the password\n(3) Delete it\n(4) Do nothing\n")
            os.system('cls' if os.name == 'nt' else 'clear')
            try:
                action = int(action)
                if action >= 0 and action <= 4:
                    invalid = False
                else:
                    print(f"{bcolors.FAIL}Invalid Option{bcolors.ENDC}")
            except ValueError:
                print(f"{bcolors.FAIL}Invalid Option{bcolors.ENDC}")
            
        if action == 4:
            return
        elif action == 0:
            newname = input("Enter the new name:")
            newname_bytes = bytes(newname,'utf-8')
            _, pwd = lines[selected+1].rstrip().split(b"|")
            newline = encoder.encrypt(newname_bytes) + b"|" + pwd + b'\n'
            lines[selected+1] = newline

            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{bcolors.OKCYAN}Name Updated{bcolors().ENDC}")
        elif action == 1:
            newpwd = input("Enter the new password:")
            newpwd_bytes = bytes(newpwd,'utf-8')
            name, _ = lines[selected+1].rstrip().split(b"|")
            newline = name + b"|" + encoder.encrypt(newpwd_bytes) + b'\n'
            lines[selected+1] = newline

            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{bcolors.OKCYAN}Password Updated{bcolors().ENDC}")
        elif action == 2:
            newname = input("Enter the new name:")
            newname_bytes = bytes(newname,'utf-8')
            newpwd = input("Enter the new password:")
            newpwd_bytes = bytes(newpwd,'utf-8')
            newline = encoder.encrypt(newname_bytes) + b"|" + encoder.encrypt(newpwd_bytes) + b'\n'
            lines[selected+1] = newline

            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{bcolors.OKCYAN}Name and Password Updated{bcolors().ENDC}")
        else:
            lines.pop(selected+1)

            print(f"{bcolors.OKCYAN}successfully Removed{bcolors().ENDC}")
            
        with open('passwords.bin','wb') as f:
            f.writelines(lines)
        return


#Main loop
while True:
    
    invalid = True
    while invalid:
        action = input("Would you like to:\n(0) Add new password\n(1) View existing passwords\n(2) Edit existing passwords\n(3) Quit\n")
        os.system('cls' if os.name == 'nt' else 'clear')
        try:
            action = int(action)
            if action >= 0 and action <= 3:
                invalid = False
            else:
                print(f"{bcolors.FAIL}Invalid Option{bcolors.ENDC}")
        except ValueError:
            print(f"{bcolors.FAIL}Invalid Option{bcolors.ENDC}")
    
    if action == 3:
        break
    elif action == 0:
        add()
    elif action == 1:
        view()
    elif action == 2:
        edit()
