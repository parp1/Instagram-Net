import os
import sys
import requests
import json
from bs4 import BeautifulSoup
from pprint import pprint
from requests import get
import pickle
import ijson
from utilities import *

def getImage(content, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request not needed
        # response = get(url)
        # write to file
        file.write(content) # previously: file.write(response.content)

def find_data_script(scripts):
    for script in scripts:
        if script.text[:18] == "window._sharedData":
            return script
    return None

links = []
seen_usernames = set()
scraped_user_data = {"num_users": 0, "user_data": []}
scraped_usernames = set()
has_scraped_data_flag = False

print("\n")
print("-----")
print("-----")
print("-----")
print("-----")
print("-----")
print("\n")

### Getting file with href links ###
links_file = sys.argv[1]
if os.path.exists(links_file): # file exists
    print("Links loaded.")
    links = json.load(open(links_file))
    # pprint(links)
    print("----------------------------------------")
else:
    print(links_file + " does not exist.")
    print("----------------------------------------")

### Getting file with set of already seen usernames ###
seen_usernames_file = sys.argv[2]
if os.path.exists(seen_usernames_file): # file exists
    if os.path.getsize(seen_usernames_file) > 0:
        print("Previously seen usernames loaded.")
        with open(seen_usernames_file, "rb") as file:
            seen_usernames = pickle.load(file)
            print(str(len(seen_usernames)) + " already seen.")
        print("----------------------------------------")
else:
    print(seen_usernames_file + " does not exist.")
    print("----------------------------------------")

### Checking for file with previouly scraped data ###
scraped_user_data_file = sys.argv[3]
if os.path.exists(scraped_user_data_file): # file exists
    print("Previously scraped data found! Will skip to facecropping images.")
    has_scraped_data_flag = True
    print("----------------------------------------")
else:
    print(scraped_user_data_file + " does not exist.")
    print("----------------------------------------")

### Getting file with set of already scraped usernames ###
scraped_usernames_file = sys.argv[4]
if os.path.exists(scraped_usernames_file): # file exists
    if os.path.getsize(scraped_usernames_file) > 0:
        print("Previously scraped usernames loaded.")
        with open(scraped_usernames_file, "rb") as file:
            scraped_usernames = pickle.load(file)
            print(str(len(scraped_usernames)) + " already scraped.")
        print("----------------------------------------")
else:
    print(scraped_usernames_file + " does not exist.")
    print("----------------------------------------")

### Getting data directory to store final facecropped images in ###
data_directory = sys.argv[5]
if os.path.exists(data_directory): # file exists
    print("Data directory: " + data_directory)
    print("----------------------------------------")       
else:
    print(data_directory + " does not exist.")
    data_directory = "/tmp/"
    print("----------------------------------------")

if (has_scraped_data_flag):
    num_links = 0
else:
    num_links = len(links)

for i in range(num_links):
    try:
        post_page_req = requests.get("https://www.instagram.com" + links[i]).text
        post_page_soup = BeautifulSoup(post_page_req, "html.parser")
        post_page_scripts = post_page_soup.find_all("script")

        post_data_script = find_data_script(post_page_scripts)

        post_data = json.loads(post_data_script.contents[0][21:-1])
        # print(json.dumps(data, indent=4)) # use for debugging post

        username = str(post_data["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["owner"]["username"])
        
        if (username in seen_usernames):
            raise Exception("User already seen before!")
        else:
            seen_usernames.add(username)
    except Exception as e:
        print("Error " + str(e) + " for: " + links[i] + " (" + str(i + 1) + "/" + str(num_links) + ")")
        print("----------------------------------------")
        continue
    except KeyboardInterrupt:
        break

if (has_scraped_data_flag):
    num_seen_users = 0
else:
    num_seen_users = len(seen_usernames)

seen_usernames_list = list(seen_usernames)
user_data_scraped = scraped_user_data["user_data"]

for i in range(num_seen_users):
    try:
        username = seen_usernames_list[i]
        if (username in scraped_usernames):
            raise Exception("User already scraped before!")

        user_page_req = requests.get("https://www.instagram.com/" + username).text
        user_page_soup = BeautifulSoup(user_page_req, "html.parser")
        user_page_scripts = user_page_soup.find_all("script")

        user_data_script = find_data_script(user_page_scripts)

        user_data = json.loads(user_data_script.contents[0][21:-1])
        # print(json.dumps(user_data, indent=4)) # use for debugging user profile

        bio = str(user_data["entry_data"]["ProfilePage"][0]["user"]["biography"])
        num_followers = int(user_data["entry_data"]["ProfilePage"][0]["user"]["followed_by"]["count"])
        num_following = int(user_data["entry_data"]["ProfilePage"][0]["user"]["follows"]["count"])
        num_posts = int(user_data["entry_data"]["ProfilePage"][0]["user"]["media"]["count"])
        post_data = []

        if (num_following == 0 or num_followers == 0 or num_posts == 0):
            raise Exception("Spam account")

        # Getting post_data
        index = 0
        num_posts_scraped = 0
        while index < num_posts and index < 12: #12 is the max number of recent pics that can be shown on the page
            try:
                current_post_data = user_data["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"][index]

                if ("caption" in current_post_data):
                    post_caption = str(current_post_data["caption"])
                else:
                    post_caption = ""

                post_likes = int(current_post_data["likes"]["count"])
                post_comments = int(current_post_data["comments"]["count"])
                post_image_link = current_post_data["display_src"]
                post_image_id = current_post_data["id"]
                post_image_height = int(current_post_data["dimensions"]["height"])
                post_image_width = int(current_post_data["dimensions"]["width"])

                image_response = get(post_image_link)
                post_image_data = encode_image_data(image_response.content)

                post_data.append(create_post_entry(post_caption, post_likes, post_comments, post_image_link, post_image_data.decode(), post_image_height, post_image_width, post_image_id))
                index += 1
                num_posts_scraped += 1
            except Exception as e:
                print("Error " + str(e) + " for " + seen_usernames_list[i] + "'s post. (" + str(index + 1) + "/" + str(num_posts) + ")")
                index += 1

        if (num_posts_scraped != len(post_data)):
            raise Exception("num_posts_scraped does not match number of elements in post_data.")

        user_data_scraped.append(create_user_entry(username, bio, num_followers, num_following, num_posts, num_posts_scraped, post_data))
        scraped_usernames.add(username)
        print("Successfully scraped " + str(num_posts_scraped) + " posts from user: " + seen_usernames_list[i] + " (" + str(i + 1) + "/" + str(num_seen_users) + ")")
        print("----------------------------------------")
    except Exception as e:
        print("Error " + str(e) + " for: " + seen_usernames_list[i] + " (" + str(i + 1) + "/" + str(num_seen_users) + ")")
        print("----------------------------------------")
        continue
    except KeyboardInterrupt:
        break

scraped_user_data["num_users"] = len(scraped_usernames)
scraped_user_data["user_data"] = user_data_scraped

### Write to files only if we actually scraped, and scraped data wasn't already given ###
if (has_scraped_data_flag != True):
    with open(seen_usernames_file, "wb") as file:
        pickle.dump(seen_usernames, file)

    with open(scraped_user_data_file, "w") as file:
        json.dump(scraped_user_data, file)

    with open(scraped_usernames_file, "wb") as file:
        pickle.dump(scraped_usernames, file)

print("\n")
print("-----")
print("-----")
print("-----")
print("-----")
print("-----")
print("\n")

num_scraped_usernames = len(scraped_usernames)

with open(scraped_user_data_file, 'r') as file:
    scraped_items = ijson.items(file, 'user_data.item')

    i = 0
    for item in scraped_items:
        try:
            current_user_entry = item 

            # Calculating ratio
            ratio = current_user_entry["num_followers"] / current_user_entry["num_following"]
            if (ratio < 0.5):
                ratio = 0
            else:
                ratio = int(ratio * 100)

            # Getting most liked picture
            current_user_posts = current_user_entry["post_data"]
            num_posts_scraped = current_user_entry["num_posts_scraped"]

            # max_liked_post = 0
            # for j in range(current_user_entry["num_posts_scraped"]):
            
            #     current_post_likes = int(current_user_posts[j]["num_likes"])
            #     if (current_post_likes > current_user_posts[max_liked_post]["num_likes"]):
            #         max_liked_post = j
            #
            # Saving image
            # image_name = str(ratio) + "-" + current_user_entry["username"] + ".jpg"
            # getImage(decode_image_data(current_user_posts[max_liked_post]["image_data"].encode()), "/Users/parthpendurkar/Desktop/data/" + image_name)
            # num_faces = facecrop("/Users/parthpendurkar/Desktop/data/" + image_name)

            total_likes = 0
            total_comments = 0
            analyzed_posts = 0
            for j in range(num_posts_scraped):
                # Saving image
                try:
                    total_likes += current_user_posts[j]["num_likes"]
                    total_comments += current_user_posts[j]["num_comments"]
                    analyzed_posts += 1
                except Exception as e:
                    print("Error " + str(e) + " for " + current_user_entry["username"] + "'s post. (" + str(j + 1) + "/" + str(current_user_entry["num_posts_scraped"]) + ")")
                    continue

            average_likes = int(total_likes / analyzed_posts)
            average_comments = int(total_comments / analyzed_posts)

            total_num_faces = 0
            for j in range(current_user_entry["num_posts_scraped"]):
                # Saving image
                try:
                    likes = current_user_posts[j]["num_likes"]
                    comments = current_user_posts[j]["num_comments"]

                    like_difference = likes - average_likes
                    comment_difference = comments - average_comments

                    image_name = str(ratio + like_difference + comment_difference) + "-" + current_user_entry["username"] + "-post" + str(j) + ".jpg"
                    getImage(decode_image_data(current_user_posts[j]["image_data"].encode()), data_directory + image_name)
                    num_faces = facecrop(data_directory + image_name)
                    total_num_faces += num_faces
                except Exception as e:
                    print("Error " + str(e) + " for " + current_user_entry["username"] + "'s post. (" + str(j + 1) + "/" + str(current_user_entry["num_posts_scraped"]) + ")")
                    continue

            
            print("Got " + str(total_num_faces) + " faces from posts of user: " + current_user_entry["username"] + " (" + str(i + 1) + "/" + str(num_scraped_usernames) + ")")
            print("----------------------------------------")
            i += 1
        except Exception as e:
            print("Error " + str(e) + " for posts of user: " + current_user_entry["username"] + " (" + str(i + 1) + "/" + str(num_scraped_usernames) + ")")
            print("----------------------------------------")
            i += 1
            continue
        except KeyboardInterrupt:
            break

print("\n")
print("FINISHED")
