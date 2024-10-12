import json
import csv
import time
import datetime as dt
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import pytz

PST_TO_UTC = -8
DIE = ""
ALREADY = ""
class TimeKeeper:
    def __init__(self,root,task_name,task_data):
        self.root = root
        self.curr_task = task_name
        self.data_ref = task_data
        self.root.title(f"Current Task: {self.curr_task}")
        self.raw_seconds = 0
        self.seconds = 0
        self.time_date = f"{self.seconds//3600}:{self.seconds//60}:{self.seconds%60}"
        self.is_playing = True
        self.stop_hiding = ""
        root.iconbitmap(False,'LogoThree.ico')
    def play(self):
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def auto_update(self):
        self.raw_seconds += 1
        if self.is_playing:
            self.seconds += 1
        self.root.attributes("-topmost",True)
        self.time_date = f"{dt.timedelta(seconds=self.seconds)}"
        self.widget_label.config(text=self.time_date)
        self.stop_hiding  = self.root.after(1000,self.auto_update)

    def end_of_session(self):
        self.root.after_cancel(self.auto_update)
        trojan_clean = self.data_ref["from"]
        clean_time =  f"{datetime.date(datetime.now().astimezone(pytz.utc))}  {datetime.time(datetime.now().astimezone(pytz.utc))}"
        self.data_ref["to"] = clean_time
        dur = datetime.now().astimezone(pytz.utc) - self.data_ref["raw_time"]
        self.data_ref["raw_time"] = round(dur.total_seconds()/3600,2)
        self.data_ref["hours_logged"] = round(self.seconds/3600,2)
        if self.data_ref["raw_time"] == 0:
            self.data_ref["disparity"] = 0
        else:
            self.data_ref["disparity"] = round(self.data_ref["hours_logged"] / self.data_ref["raw_time"],2)
        self.data_ref["memo"] = input("Explain what you did: ")
        return self.data_ref

    def build_widget(self):
        s = ttk.Style()
        self.root.geometry('320x90-0-40')
        self.root.configure(bg='black')
        s.configure('IW_Violet.TFrame',background='#301E59',font='calibri')
        s.configure('IW_Mucosal.TButton',background='#AE5044',font='calibri')
        self.custom_frame = ttk.Frame(self.root, style='IW_Violet.TFrame')
        self.custom_frame.pack()
        self.widget_task = tk.Label(self.custom_frame,text=f"Current Task: {self.curr_task}", font=14,fg='white',bg='#40378A')
        self.widget_label = tk.Label(self.custom_frame,text=self.time_date, font=12,fg='white',bg='#5043AD')
        self.widget_play = ttk.Button(self.custom_frame,text="Play",style='IW_Mucosal.TButton',command=self.play)
        self.widget_pause = ttk.Button(self.custom_frame,text="Pause",style='IW_Mucosal.TButton',command=self.pause)
        self.widget_exit = ttk.Button(self.custom_frame,text="Exit",style='IW_Mucosal.TButton',command=self.root.destroy)
        self.custom_frame.update()
        self.widget_label.update()
        self.widget_task.pack()
        self.widget_label.pack()
        self.widget_play.pack(side=tk.LEFT)
        self.widget_exit.pack(side=tk.RIGHT)
        self.widget_pause.pack(side=tk.TOP)
        DIE = self.root.after(1,self.auto_update)
        tk.mainloop()
        self.root.after_cancel(DIE)
        self.root.after_cancel(self.stop_hiding)
        return self.end_of_session()

def start_session(task_name,task_data):
    clean_time =  f"{datetime.date(datetime.now().astimezone(pytz.utc))}  {datetime.time(datetime.now().astimezone(pytz.utc))}"
    session_builder = {
        "from":clean_time,
        "to": None,
        "raw_time": datetime.now().astimezone(pytz.utc), 
        "hours_logged": 0,
        "disparity": 0, 
        "memo": ""
    }
    keeper = TimeKeeper(tk.Tk(),task_name,session_builder)
    session_builder = keeper.build_widget()
    task_data["sessions"].append(session_builder)
    return task_data

def task_set(task):
    session = task
    task_set = False
    print("Welcome to the task setting module!  Once you pick a task and confirm, the timer will begin!")
    current_task = "none"
    while task_set == False:    
        print("What will be your current task?")
        current_task = input("")
        if current_task in task.keys():
            print(f"Do you want to continue the following task: {current_task}?")
            response = input("")
            if response == 'y':            
                print(f"You now continue the following task: {current_task}")
                task_set = True
                task[current_task] = start_session(current_task,task[current_task])
            elif "exit":
                print("Exiting task setting module...")
                break
            else:
                print("Reseting loop...")
        else:
            print(f"Is {current_task} a new task? (y/n)")
            response = input("")
            if response == 'y':
                print(f"Please describe the task: {current_task}")
                desc = input("")
                print(f"Rate your sentiment level for the following task: {current_task}")
                sent = input("")
                task[current_task] = {
                    "description": desc,
                    "sentiment": sent,
                    "sessions": []
                }
                print(f"You now will begin the following task: {current_task}")
                task[current_task] = start_session(current_task,task[current_task])
                task_set = True
            elif "exit":
                print("Exiting task setting module...")
                break
            else:
                print("Reseting loop...")
    current_time = datetime.now()
    return task

def display_tasks(task):
    for k in task.keys():
        sess = task[k]["sessions"]
        print(f"Task: {k} | Time Spent: {calc_sessions(sess):.2f}")

def calc_sessions(k):
    amount = 0
    for s in k:
        amount += float(s["hours_logged"])
    return amount

time_dict = {}

with open('time_logs.json', 'r') as file:
    j_load = json.load(file)
    time_dict = j_load
    pick = 0

    while pick != 4:
        print("--------- Insculpo Works Time Logger -----------")
        print("Begin Task - 1")
        print("List Task Logs - 2")
        print("Sent to CSV - 3")
        print("quit - 4")
        print("Pick an option from 1-4")
        try:
            pick = int(input(""))
        except:
            print("Please enter a number")
        if pick == 1:
            time_dict = task_set(time_dict)
        if pick == 2:
            if time_dict == {}:
                print("There are currently no task logs.")
            display_tasks(time_dict)
        if pick == 3:
            with open('time_logs.csv', 'w',newline='') as file:
                try:
                    writer = csv.writer(file)
                    writer.writerow(["Task","From","To","Raw Time","Hours Logged","Disparity","Memo"])
                    for k in time_dict.keys():
                        for s in time_dict[k]["sessions"]:
                            writer.writerow([str(k),s["from"],s["to"],s["raw_time"],s["hours_logged"],s["disparity"],s["memo"]])
                    print("Wrote the CSV, look for the file time_logs.csv in the current directory!")
                except:
                    print("Failed to write the CSV!")
        if pick == 4:
            print("Thank you for using the insculpo works time logger!")
            time.sleep(2)
    with open('time_logs.json', 'w') as file:
        json.dump(time_dict, file, indent=4)
