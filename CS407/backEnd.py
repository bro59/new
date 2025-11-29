import pandas as pd
import string
import re

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


def main():
    file_path = "testfile.txt"
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
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            words_list = content.split()  # Splits by whitespace

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

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
    
    x,left_over = window(filtered_list,df,2,2)
    average = sum(x) / len(x)
    print(x)
    print(f"Average = {average}")
    if left_over:
        print("You have words left over")
        print(f"Words left over include: {left_over}")

if __name__ == '__main__':
    main()