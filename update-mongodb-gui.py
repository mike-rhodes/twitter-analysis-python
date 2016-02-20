'''
Created on Dec 13, 2014

@author: mrhodes

Used "http://zetcode.com/gui/tkinter/layout/" as a guide.
'''

from Tkinter import *
from ttk import Frame, Style
from pymongo import MongoClient

# Set up MongoDB
client = MongoClient()
db = client.tweetdb
collection = db.tweetdata

# ============= Tkinter GUI Functions ============= #

# Function to pull the first tweet with
def get_tweet_data():
    
    # Find a tweet that has not been analyzed ('azd' will not exist if it is hasnt been analyzed)
    the_data = collection.find_one({'azd': {'$exists': False}}) # Fetch the results
    
    # Pull id of the tweet and store it in a variable
    global curr_tweet_id
    curr_tweet_id = the_data['_id']
    
    # Clear current text
    txtbox_keyword.delete(0.0, END) # Clears the tweet text
    txtbox_tweet.delete(0.0, END) # Clears the tweet text
    txtbox_user.delete(0.0, END) # Clears the username text
    txtbox_user_desc.delete(0.0, END) # Clears the user description text
    txtbox_user_loc.delete(0.0, END) # Clears the user location text
    txtbox_nStatuses.delete(0.0, END) # Clears the number of statuses value
    
    # Deselect all boxes
    chk_relevant_to_kw.deselect()
    chk_ambiguous.deselect()
    chk_spam.deselect()
    chk_ignore.deselect()
    chk_advert.deselect()
    chk_news.deselect()
    chk_rt.deselect()
    chk_opinion.deselect()
    chk_desire.deselect()
    
    # Populate the textboxes with tweet info to be evaluated
    txtbox_keyword.insert(INSERT, the_data['keyword']) # Adds tweet text to box
    txtbox_tweet.insert(INSERT, the_data['tweet']) # Adds tweet text to box
    txtbox_user.insert(INSERT, the_data['username']) # Adds username text to box
    
    #print curr_tweet_id
    
    try:
        txtbox_user_desc.insert(INSERT, the_data['user_desc']) # Adds user description text to box
    except TclError:
        txtbox_user_desc.insert(INSERT, "No user description provided") # If no user description provided 
        
    try:
        txtbox_user_loc.insert(INSERT, the_data['location']) # Adds user description text to box
    except TclError:
        txtbox_user_loc.insert(INSERT, "No location provided") # If no location provided
        
    txtbox_nStatuses.insert(INSERT, the_data['nstatuses']) # Adds number of statuses text to box

# Function to update the row in the table with metadata about the tweet
def post_tweet_meta ():
    
    try:
        
        # Get the index of the listbox selection
        tone_value = map(int, lb_tone.curselection())
        
        global tone_value_scale
        # Since indicies go from zero to n in Python, we want to take the response indices of 0-4 and map them from 2,1,0,-1,-2
        # Probably a more efficient way to do this but let's make it work first
        if tone_value[0] == 0:
            tone_value_scale = 2
        elif tone_value[0] == 1:
            tone_value_scale = 1
        elif tone_value[0] == 2:
            tone_value_scale = 0
        elif tone_value[0] == 3:
            tone_value_scale = -1
        elif tone_value[0] == 4:
            tone_value_scale = -2
            
    # If all good, then insert info into the db
        try:
            # Execute the update statement
            collection.update({'_id': curr_tweet_id}, 
                                {'$set': {
                                'relevant_to_kw': chk_relevant_to_kw_var.get(),
                                'ambiguous': chk_ambiguous_var.get(),
                                'tweet_tone': tone_value_scale,
                                'desire': chk_desire_var.get(),
                                'ignore_tweet': chk_ignore_var.get(),
                                'spam': chk_spam_var.get(),
                                'advertisement': chk_advert_var.get(),
                                'news_tweet': chk_news_var.get(),
                                'retweet': chk_rt_var.get(),
                                'opinion_tweet': chk_opinion_var.get(),
                                'azd': 1}})
            
            # Deselect all checkboxes
            chk_relevant_to_kw.deselect()
            chk_ambiguous.deselect()
            chk_spam.deselect()
            chk_ignore.deselect()
            chk_advert.deselect()
            chk_news.deselect()
            chk_rt.deselect()
            chk_opinion.deselect()
            chk_desire.deselect()
            
            lb_tone.select_clear(0, 4)
            
            # Pull next tweet
            get_tweet_data()
            
        except NameError:
            print "SQL error"
    
    except IndexError:
        print "Please make tone selection"
    

# Function to mark the tweet as one to ignore
def post_ignore_tweet ():
    
    try:
        # Execute the update statement
        collection.update({'_id': curr_tweet_id},
                          {'$set': {
                                'ignore_tweet': 1,
                                'azd': 1}})
        
        # Deselect all checkboxes
        chk_relevant_to_kw.deselect()
        chk_ambiguous.deselect()
        chk_spam.deselect()
        chk_ignore.deselect()
        chk_advert.deselect()
        chk_news.deselect()
        chk_rt.deselect()
        chk_opinion.deselect()
        chk_desire.deselect()
        
        lb_tone.select_clear(0, 4)
        
        # Pull next tweet
        get_tweet_data()
            
    except NameError:
        print "SQL error"
    

# ============= Tkinter GUI Section ============= #
# Instantiate the main Tkinter object
my_window = Tk()

my_window.title("Tweet Tone Analyzer") # Set title
my_window.minsize(800, 600) # Min size of the window

# ============= Instantiate menu bar
menubar = Menu(my_window)
menubar.add_command(label="Hello!")
menubar.add_command(label="Quit!")

# Add menubar to the 
my_window.config(menu=menubar, background='#333')
#, background='#333'

# ============= Instantiate frames
fr_first_bttns = Frame(my_window) # First frame for all the buttons
fr_tweet_info = Frame(my_window) # Frame to hold the tweet info
fr_user_inp = Frame(my_window) # Frame to hold the user analysis buttons

# ============= First Frame
# Instantiate Buttons
bttn_pft = Button(fr_first_bttns, text = "Pull Tweet")
bttn_close = Button(fr_first_bttns, text = "Close")

#Add command for pull tweet button
bttn_pft.configure(command = get_tweet_data)

# Add buttons to fr_first_bttns
bttn_pft.pack(side = LEFT)
bttn_close.pack(side = LEFT)

# ============= Second Frame
# Create keyword textbox
txtbox_keyword = Text(fr_tweet_info, height = 1)
txtbox_keyword.insert(INSERT, "Keyword")

# Create tweet textbox
txtbox_tweet = Text(fr_tweet_info, height = 2)
txtbox_tweet.insert(INSERT, "Tweet")

# Create username textbox
txtbox_user = Text(fr_tweet_info, height = 1)
txtbox_user.insert(INSERT, "Username")

# Create user description textbox
txtbox_user_desc = Text(fr_tweet_info, height = 2)
txtbox_user_desc.insert(INSERT, "User Desc")

# Create user loacation textbox
txtbox_user_loc = Text(fr_tweet_info, height = 2)
txtbox_user_loc.insert(INSERT, "User Location")

txtbox_nStatuses = Text(fr_tweet_info, height = 1)
txtbox_nStatuses.insert(INSERT, "Number of Statuses")

# Add text boxes to second frame
txtbox_keyword.pack()
txtbox_tweet.pack()
txtbox_user.pack()
txtbox_user_desc.pack()
txtbox_user_loc.pack()
txtbox_nStatuses.pack()

# ============= Third Frame
# Instantiate Listbox
lb_tone = Listbox(fr_user_inp, height = 5, selectmode = SINGLE)

# Add listbox entries
lb_tone.insert(END, "Very Positive")
lb_tone.insert(END, "Positive")
lb_tone.insert(END, "Neutral")
lb_tone.insert(END, "Negative")
lb_tone.insert(END, "Very Negative")

# Add listbox to frame
lb_tone.pack()

# Create checkbutton variables
chk_relevant_to_kw_var = IntVar()
chk_ambiguous_var = IntVar()
chk_spam_var = IntVar()
chk_ignore_var = IntVar()
chk_advert_var = IntVar()
chk_news_var = IntVar()
chk_rt_var = IntVar()
chk_opinion_var = IntVar()
chk_desire_var = IntVar()

# Instantiate checkbuttons
chk_relevant_to_kw = Checkbutton(fr_user_inp, text = "Relevant to Keyword?", height=3, width = 20, variable = chk_relevant_to_kw_var)
chk_ambiguous = Checkbutton(fr_user_inp, text = "Tweet Ambiguous?", height=3, width = 20, variable = chk_ambiguous_var)
chk_spam = Checkbutton(fr_user_inp, text = "Spam?", height=3, width = 15, variable = chk_spam_var)
chk_ignore = Checkbutton(fr_user_inp, text = "Ignore?", height=3, width = 15, variable = chk_ignore_var)
chk_advert = Checkbutton(fr_user_inp, text = "Advertisement?", height=3, width = 15, variable = chk_advert_var)
chk_news = Checkbutton(fr_user_inp, text = "News Article?", height=3, width = 15, variable = chk_news_var)
chk_rt = Checkbutton(fr_user_inp, text = "Retweet?", height=3, width = 15, variable = chk_rt_var)
chk_opinion = Checkbutton(fr_user_inp, text = "Personal Opinion?", height=3, width = 15, variable = chk_opinion_var)
chk_desire = Checkbutton(fr_user_inp, text = "Desire for KW?", height=3, width = 15, variable = chk_desire_var)

# Add checkbuttons to frame
chk_relevant_to_kw.pack()
chk_ambiguous.pack()
chk_spam.pack()
chk_ignore.pack()
chk_advert.pack()
chk_news.pack()
chk_rt.pack()
chk_opinion.pack()
chk_desire.pack()

# Instantiate submit buttons
bttn_submit = Button(fr_user_inp, text = "Submit")
bttn_ignore = Button(fr_user_inp, text = "Ignore")
bttn_submit.configure(command = post_tweet_meta)
bttn_ignore.configure(command = post_ignore_tweet)
bttn_submit.pack()
bttn_ignore.pack()

# ============= Add frames to main Tkinter object
fr_first_bttns.pack()
fr_tweet_info.pack()
fr_user_inp.pack()

# Start main loop to run the program
my_window.mainloop()