import os
import argparse

#add argument from the command line  
parser = argparse.ArgumentParser(description='Get the commit message.')
#we want to add the commit message
parser.add_argument('--commit', type=str, nargs='+',
                    help='get a message for the commit')
#get the commit message 
commit_message = vars(parser.parse_args())['commit'][0]

if __name__=="__main__":
    print("-------------------- ADD --------------------")
    os.system("git add .")
    print("-------------------- COMMIT --------------------")
    os.system('git commit -m "{}"'.format(commit_message))
    print("-------------------- PUSH --------------------")
    os.system("git push")
    

