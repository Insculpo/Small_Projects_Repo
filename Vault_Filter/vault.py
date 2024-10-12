import os
import re
from collections import Counter, defaultdict
import shutil
import regex
import json

def build_filtered_vault(new_directory, profiles, the_picks,pattern=r'(#\w+)'):
    has_bl = False
    has_wl = False
    black_list_tags = []
    white_list_tags = []
    purge_list = []
    print(the_picks)
    tag_pattern = re.compile(pattern)
    print(tag_pattern)
    for pro in the_picks:
        if pro in profiles[0].keys():
            setted = profiles[0][pro]
            print(setted['description'])
            print(list(setted['bl_tags']))
            print(list(setted['wl_tags']))
            bl_tag_list = list(setted['bl_tags'])
            wl_tag_list = list(setted['wl_tags'])
            if len(bl_tag_list) > 0:
                has_bl = True
                for tag in bl_tag_list:
                    black_list_tags.append(tag)
            if len(wl_tag_list) > 0:
                has_wl = True
                for tag in wl_tag_list:
                    white_list_tags.append(tag)
    print("Black List: ",black_list_tags)
    print("White List: ",white_list_tags)
    Input = input("Do you want to continue? (y/n)")
    if Input == 'n':
        print("Exiting...")
        exit()
    # Create a new directory
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    # Copy the vault over
    for root, dirs, files in os.walk(new_directory):
        if '.obsidian' in root:
            continue
        if '.git' in root:
            continue
        if '.smart-connections' in root:
            continue
        if '.trash' in root:
            continue
        if '.ignore' in root:
            continue
        print(f"Checking {root} for clearance level.")
        for file in files:
                pathway = os.path.join(root, file)
                with open(pathway,'r',encoding='utf-8') as f:
                    print(f"Checking {file} for clearance level.")
                    # Check for the tags
                    to_purge = False
                    if file.endswith('.md'):   
                        if has_wl:
                            to_purge = True
                        else:
                            to_purge = False
                        while True:
                            line = f.readline()
                            if not line and has_wl== True:
                                 break
                            elif not line:
                                break
                            result = tag_pattern.findall(line)
                            print("tags: ",result)
                            if result == []:
                                continue
                            print("Checking tags...")
                            #White list first priority
                            #This is since a white list exlcudes everything else first.
                            #So a vault with both a white list and a black list narrows the file down to whitelist files then checks to see if any blacklist files are present in the whitelist to also remove.
                            if has_wl:
                                for tag in white_list_tags:
                                    print(tag)
                                    if tag in result:
                                        print(f"Found whitelisted {tag} in {file}")
                                        to_purge = False
                                        break
                            if has_bl:
                                for tag in black_list_tags:
                                    print(tag)
                                    if tag in result:
                                        print(f"Found blacklisted {tag} in {file}")
                                        to_purge = True
                                        break
                        if to_purge == True:
                            print(f"Adding {file} to the purge list.")
                            purge_list.append(pathway)

    print(purge_list)
    for purge_file in purge_list:
        print(f"Purging {purge_file}...")
        os.remove(purge_file)

                            
    print(f"Filtered vault created at {new_directory}")

clearance_profiles = []
rooted = os.getcwd()
path_file = os.path.join(rooted,'clearance_profiles.json')
if os.path.isfile(path_file):
    print("Found clearance_profiles.json")
    clearance_profiles = json.load(open('clearance_profiles.json','r'))
    # Load the json file
    pass
else:
    # Create the json file
    clearance_profiles = [{
        "template-blacklist": {
            "bl_tags": ['#blacklisted'],
            "wl_tags": [],
            "description": "An example profile with a blacklisted tag."
        },
        "template-whitelist": {
            "bl_tags": [],
            "wl_tags": ['#whitelisted'],
            "description": "An example profile with a whitelisted tag.",
        },
        "template-combined": {
            "bl_tags": ['#blacklisted'],
            "wl_tags": ['#whitelisted'],
            "description": "An example profile with both a blacklisted and whitelisted tag."
        },
        "All-Knowledge": {
            "bl_tags": [],
            "wl_tags": [],
            "description": "The god perspective of the setting."
        }
    }]
    
    convert_json = json.dumps(clearance_profiles,indent=4)
    with open('clearance_profiles.json','w') as f:
        f.write(convert_json)
    print("Created clearance_profiles.json")

print("Pick your profile.  Type q to quit.")
i = 0
for k in clearance_profiles[0].keys():
    print(f"{i+1}. {k}: {clearance_profiles[0][k]['description']}")
    i+=1
spoiler_level = -1
picked = False
clearance_pick = ""
profile = []
while True:
    print("--------------------------------------------------")
    print("Pick from one of the valid options above.")
    clearance_pick = input("")
    if clearance_pick == 'q':
        print("Exiting...")
        exit()
    for k in  clearance_profiles[0].keys():
        if clearance_pick == k:
            print(f"Selected {k}.")
            profile.append(k)
            picked = True
    if picked:
        print("Add another? (y/n)")
        response = input("")
        if response == 'y':
            continue
        elif response == 'q':
            print("Exiting...")
            exit()
        else:
            break

if clearance_pick == 'q':
    print("Exiting...")
    exit()
else:
    print("Now name the vault. (q to quit)")
    out_vault = input("")
    # Example usage
    if out_vault == 'q':
        print("Exiting...")
        exit()
    vault_path = 'testiest_vault'
    new_directory = shutil.copytree(vault_path, out_vault)
    #new_directory = 'nope'
    #directory, the files and pick.
    build_filtered_vault(new_directory,clearance_profiles,profile,pattern=r'#[\w\/\-]+')
input("Press Enter to continue...")