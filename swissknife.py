import socket
import json
import glitter
import os
import hashlib

USER_INFO = ""
sock = ""

def print_options_menu():
    """
    This function print the swissknife option and get the option from the user
    :return: the user's option
    :rtype: int
    """
    print(f"\n✨ MAIN MENU ✨")
    print("0. - Exit")
    print("1. - Get user's email")
    print("2. - Get user's password (Login challenge)")
    print("3. - Add likes to glit")
    print("4. - Post glit in the past")
    print("5. - Post glit with different background color")
    print("6. - Create a user with registration code that lower than 5")
    print("7. - Create a user with name longer than the max")
    print("8. - Create a user with screen name longer than the max")
    print("9. - Post a comment with no name")
    print("10. - Get user's search history (Privacy challenge)")
    print("11. - Get user's cookie (Cookie challenge)")
    print("12. - Get user's password (Password challenge)")

    return int(input("Please choose: ")) # Return the user option without saving it to a variable
    

def main():
    global sock
    login = False
    user_choice = 1
    global USER_INFO
    print()
    print("Welcome to Ido's swissknife⚔️  , Please login to your glitter account")
    while not login:
        user_name = input("Please enter username: ")
        password = input("Please enter password: ")
        print("") # To make a nice and clean console
        try:
            print("Logging in...")
            sock = glitter.open_socket_connection()
            USER_INFO = glitter.app_login(user_name, password, sock)
            if USER_INFO:
                login = True
                print(f"Logged in as \"{USER_INFO['screen_name']}\" 🔓")
        except Exception:
            login = False
    
    while user_choice != 0: # While the user isn't chose to exit the swissknife
        user_choice = print_options_menu()
        if user_choice == 0: # Exit
            print("Goodbye 👋")
        elif user_choice == 1: # Steal E-Mail
            user_screen_name = input("Enter the user screen name to get his email: ")
            emails = glitter.steal_email(sock, user_screen_name)
            if emails:
                print("\nHere the emails that were found:")
                print(emails)
            else:
                print(f"No emails were found to \"{user_screen_name}\"")
        elif user_choice == 2: # Steal Password
            user_name = input("Enter the name of the user to steal his password: ")
            password = glitter.steal_password(user_name)
            if password:
                print(f"Password for \"{user_name}\": {password}")
            else:
                print(f"Can't find password for \"{user_name}\"")
        elif user_choice == 3: # Add likes
            if glitter.add_likes_to_glit(sock, USER_INFO['screen_name'], USER_INFO['id']) == 0:
                print("3 Likes added to glit.")
            else:
                print("Can't add likes, please try again later.")
        elif user_choice == 4: # Post glit in the past
            if glitter.post_glit_past(sock, USER_INFO['id']):
                print("The post has been success!")
            else:
                print("There is an error, please try again later :(")
        elif user_choice == 5: # Post glit with diffrent color from the options
            if glitter.post_glit_different_color(sock, USER_INFO['id']):
                print("The post has been success!")
            else:
                print("There is an error, please try again later :(")
        elif user_choice == 6: # Registration code that lower than 5 
            if glitter.registration_code_lower_than_five():
                print("The action has been success")
            else:
                print("There is an error, please try again later :(")
        elif user_choice == 7: # Create account with long name
            if glitter.create_acc_name_long():
                print("The action has been success")
            else:
                print("There is an error, please try again later :(")
        elif user_choice == 8: # Create account with long screen name
            if glitter.create_acc_screen_name_long():
                print("The action has been success")
            else:
                print("There is an error, please try again later :(")
        elif user_choice == 9: # Comment on glit with no name
            if glitter.post_comment_no_name(sock, USER_INFO['id']):
                print("The action has been success")
            else:
                print("There is an error, please try again later :(")
        elif user_choice == 10: # Search history
            res = glitter.get_history(USER_INFO['id'])
            if res:
                print(f"\n{USER_INFO['screen_name']}'s History:")
                print("\n".join(res))
            else:
                print("There is an error, please try again later :(")
        elif user_choice == 11: # Get user's cookie
            res = glitter.get_cookie()
            if res:
                print(f"\n{USER_INFO['screen_name']}'s Cookie:")
                print(res)
            else:
                print("There is an error, please try again later :(")
        elif user_choice == 12: # Get user's cookie
            res = glitter.get_password_by_name(USER_INFO['user_name'], USER_INFO['id'])
            if res:
                print(f"\n{USER_INFO['screen_name']}'s Password:")
                print(res)
            else:
                print("There is an error, please try again later :(")

    sock.close() # Close the socket connection

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            sock.close()
        except None:
            pass
        print("\nThe program has been shutdown. (CTRL-C Pressed)")