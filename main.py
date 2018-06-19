from imgurpython import ImgurClient
from datetime import datetime
from datetime import timedelta
from os import listdir
from os.path import isfile, join
import numpy as np
from time import sleep
from pathlib import Path
import pickle
from pprint import pprint
import credentials
import directories
import pause
import shutil

def get_new_tokens(credentials_dict):
    client_id = credentials_dict['client_id']
    client_secret = credentials_dict['client_secret']
    client = ImgurClient(client_id, client_secret )
    print (client.get_auth_url('pin')) #go to page and copy down pin
    creds = client.authorize(input('Pin: '), 'pin')
    print(creds)
    credentials_dict['access_token'] = creds['access_token']
    credentials_dict['refresh_token'] = creds['refresh_token']

    client.set_user_auth(credentials_dict['access_token'], credentials_dict['refresh_token'])

    print("Access Token")
    print(creds['access_token'])
    print("Refresh Token")
    print(creds['refresh_token'])
    print()

    pickle_out = open("credentials.dict","wb") #open file
    pickle.dump(credentials_dict, pickle_out) #save limits dict to file
    pickle_out.close()

    return credentials_dict

def set_old_tokens(credentials_dict):

    client = ImgurClient(credentials_dict['client_id'],credentials_dict['client_secret'], credentials_dict['refresh_token'])
    client.set_user_auth(credentials_dict['access_token'], credentials_dict['refresh_token'])
    return client

def get_files(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f != '.DS_Store' and f != "._.DS_Store" and f != 'Thumbs.db']
    image_list = []

    for x in onlyfiles:
        x = x.replace(u'\xa0', u' ')
        image_list.append(mypath+"/"+x)
    return image_list

def upload_images(dir_path,image_list):
    image_ids = []
    for picture_path in image_list:

        done = False
        while not done:
            try:
                print("uploading: "+picture_path)
                uploaded_image = client.upload_from_path(picture_path, config=None, anon=False)
                print(uploaded_image['link'])
                sleep(90)
                image_ids.append(uploaded_image['id'])
                done = True

            except BaseException as e:

                if "Rate-limit exceeded" in str(e):
                    print("Rate Limit Error: Sleeping 60 Minutes")
                    with open(credentials.log_file, "a") as myfile: #apppend to log file
                        myfile.write("\n"+str(datetime.now())+" Error: "+str(e))
                    sleep(3600)

                else:
                    print("Other Error, sleeping for 1 min")
                    print("error:" + str(e))
                    with open(credentials.log_file, "a") as myfile: #apppend to log file
                        myfile.write("\n"+str(datetime.now())+" Error: "+str(e))
                    sleep(90)

                try:
                    print("Second Attempt Uploading: "+picture_path)
                    uploaded_image = client.upload_from_path(picture_path, config=None, anon=False)
                    print(uploaded_image['link'])
                    sleep(90)
                    image_ids.append(uploaded_image['id'])
                    done = True #mark as done and return to top

                except BaseException as e:

                    if "Rate-limit exceeded" in str(e):
                        print("Rate Limit Error (Again): Sleeping 60 Minutes") #returns to try above this one to try a third time?
                        with open(credentials.log_file, "a") as myfile: #apppend to log file
                            myfile.write("\n"+str(datetime.now())+" Error: "+str(e))
                        sleep(3600)

                    else:
                        print("Other Error for 2nd time, skipping")
                        print("error:" + str(e))
                        print("skipping directory which holds this file")
                        print("Dir: "+str(dir_path))
                        #shutil.rmtree(dir_path) #remove dir
                        with open(credentials.log_file, "a") as myfile: #apppend to log file
                            myfile.write("\n"+str(datetime.now())+" Skipped: "+str(path)+" Error: "+str(e))
                        image_ids = None #wipe out uploaded images - abandoning them
                        return None

    return image_ids

def create_album(name,image_ids):
    #take name, check to see if album name exists
    #if yes, return id
    #if no, create album and return id

    config = {
    'name': name,
    'title': name,
    'description': name,
    'cover': image_ids[0],
    'privacy': 'public'
    }

    new_album = client.create_album(config)
    return new_album['id']

def album_cover_image(album_id,image_id_list):
    #def update_album(self, album_id, fields)
    config = {
    'cover': image_id_list[0]
    }
    result = client.update_album(album_id,config)

def add_to_album(album_id,image_id_list):
    result = client.album_add_images(album_id,image_id_list)

def album_loop(page_number):
    sleep(4)
    albums = client.get_account_albums('5moke5creen',page=page_number)
    n = 0
    album_dict = {}
    for x in albums:
        album_dict[x.title] = x.id
        n = n+1
    return album_dict,n

def get_user_albums():
    #get_account_albums(self, username, page=0)
    page_number = 0
    album_dict,count = album_loop(page_number)

    while count == 50:
        page_number = page_number + 1
        album_dict_part,count = album_loop(page_number)
        album_dict = {**album_dict, **album_dict_part}
    print("Album Count: "+str(len(list(album_dict.keys()))))
    with open(credentials.log_file, "a") as myfile: #apppend to log file
        myfile.write("\n\n"+str(datetime.now())+" User Albums: "+str(len(list(album_dict.keys()))))
    return album_dict


creds_file = Path(credentials.creds_file)
if creds_file.is_file():
#pricing import
    pickle_in = open(str(creds_file),"rb")
    credentials_dict = pickle.load(pickle_in)
    pprint(credentials_dict)
else:
    f=open("credentials.dict","w+") #create file
    f.close()
    credentials_dict = {} #create limits dict and variables
    credentials_dict['client_id'] = credentials.client_id
    credentials_dict['client_secret'] = credentials.client_secret

    pickle_out = open("credentials.dict","wb") #open file
    pickle.dump(credentials_dict, pickle_out) #save limits dict to file
    pickle_out.close()

    #sets up new tokens for first time
    credentials_dict = get_new_tokens(credentials_dict)

#credentials_dict = get_new_tokens(credentials_dict)


client = set_old_tokens(credentials_dict)
pprint(client.credits)

#sets up pause until api ban is lifted
print(client.credits['UserReset'])
#pause_time = datetime.fromtimestamp(client.credits['UserReset'])
#pause_time_safe = pause_time + timedelta(minutes=1) #add one minute for safety
#print("Pause until: "+str(pause_time_safe))
#pause.until(pause_time_safe)

event_list = directories.generate_file_list()
album_dict = get_user_albums()
print("User Albums:")
for album in list(sorted(album_dict.keys())):
    print(album)
print("******")

for path in reversed(sorted(event_list)):
    if event_list[path] in album_dict:
        print("album "+event_list[path]+" exists already, skipping")
    else:
        file_list = get_files(path) #get files to upload
        if file_list:
            #print("This is key: "+str(path)) #this is the dir path
            #print("This is value: "+str(event_list[path])) #this is the name of the album
            image_ids = upload_images(path,file_list) #upload images and return list of ids
            if image_ids != None:
                album_id = create_album(event_list[path],image_ids) #create album and get album id
                add_to_album(album_id,image_ids) #add images to album
                #album_cover_image(album_id,image_ids) #set cover image
                print("www.imgur.com/a/"+album_id) #pring album link
            else:
                print("Directory was skipped after waiting 1 hr, moving to next")
                print()

#get_user_albums()
