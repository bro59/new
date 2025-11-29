from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os
import csv
import io
import backEnd
import re
import pandas as pd
import string

app = Flask(__name__)

# Finish working on setting up login required decorator and text set dropdown options

app.secret_key = os.urandom(32)  # Secret key for session management

#WRITE CODE FOR DEALING WITH ERRORS LATER(E.G., DUPLICATE ENTRIES, INVALID INPUTS, 
# INVALID FILE TYPES, ETC.) AND CONNEECTIONS TO OTHER TABLES IN THE DATABASEO

# Database configuration (default XAMPP credentials)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Default XAMPP password is empty
    'database': 'cs407p'
}

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)


def window(data_set,df,window_size,window_jump):

    if len(data_set) < window_size:
        print("Not enough words to form even one window.")
        return []

    # Make sure we stop before running past the end of the list
    total_jumps = (len(data_set) - window_size) // window_jump + 1
    
    start = 0
    window_list = []
    
    for i in range(total_jumps):
        window = data_set[start : start + window_size]
        start = start + window_jump
        window_score = 0
        
        for i in window:
            pattern = r'\b' + i + r'\b' # Makes sure contains doesn't look for every word containg i  
            matching_rows = df[df["Word in English"].astype(str).str.contains(pattern, case=False, na=False)]
            window_score = window_score + float(matching_rows["Happiness Score"].iloc[0]) # Grab row by position not label
           
        window_avg = window_score / window_size
        window_list.append(window_avg)
    left_over = data_set[start:]

    return window_list, left_over


@app.route('/')
#@login_required

def landing_page():
    """Renders the form page."""

    return render_template('landing_page_V1.html')


@app.route('/create1', methods=['POST'])
#@login_required

def create1():
    """Renders the form page."""
    # Reconnect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT (setName) FROM (textset)"
    #val = ("",)
    # Execute and commit
    cursor.execute(sql)
    possible_sets = cursor.fetchall()

    set_names = [item[0] for item in possible_sets]

    print(set_names)

    # Close connections
    cursor.close()
    conn.close()

    return render_template('create_page_V1.html', name=session.get('username'), set_names=set_names)


#def fetchUserName(name):
 #   userName = name

  #  return userName


@app.route('/register', methods=['POST'])
def register():
    """Handles the form submission and database insertion."""
    if request.method == 'POST':
        # Get data from the form
        user_name = request.form['username']
        user_email = request.form['email']

        session['username'] = user_name

        #fetchUserName(user_name)

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to insert data
        sql = "INSERT INTO user (Name, Email) VALUES (%s, %s)"
        val = (user_name, user_email)

        # Execute and commit
        cursor.execute(sql, val)
        conn.commit()

        # Close connections
        cursor.close()
        conn.close()

        # Redirect to a confirmation page or the home page
        return render_template('middle.html', name=user_name, email=user_email)




@app.route('/login', methods=['GET', 'POST'])
def success():
    """Renders the form page."""

    #user_name = request.form['username']
    #user_email = request.form['email']

    #session['username'] = user_name
    return render_template('login.html')




def callWindow( userData, windowSize, stepSize):
    file_path = userData

    scores_path = "hedonometer_scores.csv"  

    # Open CSV file containing dictionary
    try:
        df = pd.read_csv(scores_path)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return pd.DataFrame()
    
    # Open text file
    
    content = file_path
    words_list = content.split()  # Splits by whitespace

    # Remove any words with puncuation in them
    # Remove punctuation except apostrophes (straight or curly)
    punctuation_no_apostrophe = string.punctuation.replace("'", "")
    translator = str.maketrans("", "", punctuation_no_apostrophe)
    content_clean = content.translate(translator)

    # Also handle curly quotes explicitly
    content_clean = content_clean.replace("’", "'").replace("‘", "'")

    words_list = content_clean.split()

    cleaned_list = [s.translate(translator) for s in words_list]
        
    filtered_list = []
    for word in cleaned_list:
        pattern = r'\b' + re.escape(word) + r'\b'  # escape special chars like '
        if df["Word in English"].astype(str).str.contains(pattern, case=False, na=False).any():
            filtered_list.append(word)
    print(filtered_list)
    
    x,left_over = window(filtered_list,df,windowSize,stepSize)
    average = sum(x) / len(x)
    print(x)
    print(f"Average = {average}")
    if left_over:
        print("You have words left over")
        print(f"Words left over include: {left_over}")
    
    return (x, left_over, average)
@app.route('/CreateSet', methods=['GET', 'POST'])

def CreateSet():
    """Renders the form page."""

    return render_template('createSet.html', name=session.get('username'))



@app.route('/afterCreateSet', methods=['GET', 'POST'])

def afterCreateSet():
    """Renders the form page."""

    if request.method == 'POST':
        # Get data from the form
        set_name = request.form['CreateSet']

        session['set_name'] = set_name
    
    #Add drop down menu to select set name later
       #connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "INSERT INTO textset (setName) VALUES (%s)"
        val = (set_name,)

    # Execute and commit
    cursor.execute(sql, val)
    conn.commit()

    # Close connections
    cursor.close()
    conn.close()


    # Reconnect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT (setName) FROM (textset)"
    #val = ("",)
    # Execute and commit
    cursor.execute(sql)
    possible_sets = cursor.fetchall()

    set_names = [item[0] for item in possible_sets]

    print(set_names)

    # Close connections
    cursor.close()
    conn.close()
# select_option takes the value of the selected option in the dropdown menu and links it to the uploaded text.





    return render_template('create_page_V1.html', name=session.get('username'), set_name=set_name, set_names=set_names  )


@app.route('/select_option', methods=['POST'])

def select_option():
    """Renders the form page."""

    if request.method == 'POST':
        # Get data from the form
        selected_set = request.form.get('dropdown_menu')

        session['selected_set'] = selected_set

         # Reconnect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT (setName) FROM (textset)"
    #val = ("",)
    # Execute and commit
    cursor.execute(sql)
    possible_sets = cursor.fetchall()

    set_names = [item[0] for item in possible_sets]

    print(set_names)

    # Close connections
    cursor.close()
    conn.close()





  

    return render_template('create_page_V1.html', name=session.get('username'), selected_set=selected_set, set_names=set_names)


@app.route('/fileUpload', methods=['POST'])

#@login_required



def fileUpload():

    """Handles the form submission and database insertion."""
    if request.method == 'POST':
        # Get data from the form
        if 'input_file' not in request.files: # might remove this later
            return "No input file in the form"

        file = request.files['input_file']

        winSize = request.form.get('window_size')
        stepSize = request.form.get('step_size')

        if file.filename == '':
            return "No selected file"

        #file_stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)

        fileContent = file.stream.read().decode("UTF8")


        userData = () # to store user data from csv and txt. offers imutable structure

        if (file.filename.endswith('.csv')):

            csvData = csv.reader(io.StringIO(fileContent))

            for line in csvData:
                userData += (str(line).strip().split(),)
        else:

            userData += (fileContent.strip().split(),)
        
        
    changed= " ".join([" ".join(item) for item in userData])

    #changed = str(" ".join(userData))
    #print(changed)

     
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    user_name = session.get('username')
    print(user_name)

    sql = "SELECT UserID FROM user WHERE Name = %s"

# need to add a txt file name column to the text table later
 
    val = (user_name,)

    # Execute 
    cursor.execute(sql, val)
    
    user_id = cursor.fetchone()[0]
    print(user_id)

    # Close connections
    cursor.close()
    conn.close()

    # Reconnect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "INSERT INTO text (Content, UserID) VALUES (%s,%s)"
    val = (changed, user_id)

    # Execute and commit
    cursor.execute(sql, val)
    conn.commit()

    # Close connections
    cursor.close()
    conn.close()

    # Connect to the database
    
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT TextID FROM text WHERE UserID = %s"

    val = (user_id,)

    # Execute

    cursor.execute(sql, val)
    
    text_id = cursor.fetchone()[0]
    for x in range(1):
        print(text_id)

    # Close connections
 #   cursor.close()
#    conn.close()

    # Reconnect to the database
    conn = get_db_connection()
    cursor = conn.cursor()


    scoresArray, left_over, average = callWindow( changed, int(winSize), int(stepSize))

    sql = "INSERT INTO hscores (WindowSize, StepSize, TextID, HScores ) VALUES (%s,%s,%s,%s)"
    
    print(scoresArray)

    val = (winSize, stepSize, text_id, str(scoresArray))
    # Execute and commit
    cursor.execute(sql, val)
    conn.commit()

    
    # Close connections
    cursor.close()
    conn.close()

    # Reconnect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "Select TextSetID  FROM  textset WHERE setName = %s"
    val = (session.get('selected_set'),)
 
 
    cursor.execute(sql, val)

    textset_id = cursor.fetchone()[0]
    print(textset_id)

    print( text_id)
    sql = "INSERT INTO Text_TextSet (TextID, TextSetID) VALUES (%s,%s)"
    val = (text_id, textset_id)
    cursor.execute(sql, val)
    conn.commit()

    # Close connections
    cursor.close()
    conn.close()
#    conn.commit()

    



        # Redirect to a confirmation page or the home page
    return render_template('success1.html', file_contents=changed, name=session['username'])


@app.route('/login', methods=['POST'])


def login():

      return render_template('login.html')



@app.route('/uploadPage', methods=['POST'])


def uploadPage():

    # Reconnect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT (setName) FROM (textset)"
    #val = ("",)
    # Execute and commit
    cursor.execute(sql)
    possible_sets = cursor.fetchall()

    set_names = [item[0] for item in possible_sets]

    print(set_names)

    # Close connections
    cursor.close()
    conn.close()

    return render_template('create_page_V1.html', name=session['username'], set_names=set_names)





@app.route('/afterLogin', methods=['POST'])


def afterLogin():

    # look up user in database and if exists, we compare email to the one in the database
    if request.method == 'POST':
        user_email = request.form['Email']

        session['user_email'] = user_email

        session['username'] = request.form['username']

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to fetch user by email
        sql = "SELECT Email FROM user WHERE Name = %s"
        val = (request.form['username'],)

        # Execute the query
        cursor.execute(sql, val)
        result = cursor.fetchone()

        if result:
            if result[0] != user_email:
                return render_template('login.html', error="Email does not match our records. Please try again.")
            #user_name = result[0]
            session['username'] = request.form['username']

            return render_template('middle.html', name=session['username'])
        else:
            return render_template('login.html', error="Invalid email. Please try again.")
        
        # Close connections
        cursor.close()
        conn.close()

    #return render_template('login.html')

@app.route('/logout', methods=['POST'])

def logout():
    """Logs out the user by clearing the session."""
    session.pop('username', None)
    session.pop('user_email', None)
    session.pop('selected_set', None)
    session.pop('set_name', None)
    session.pop('set_names', None)


    return redirect(url_for('success'))

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)







