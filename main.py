import csv
import random

# Function to read the CSV file and convert it to the desired format
def read_csv_to_dict(file_path):
    program_ratings = {}
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            try:
                # Try to skip the header
                header = next(reader)
            except StopIteration:
                # This means the file is completely empty
                print(f"Warning: The file '{file_path}' is empty.")
                return {} # Return an empty dict

            # Now read the data rows
            for row in reader:
                # Ensure row has at least a name and one rating
                if len(row) > 1: 
                    program = row[0]
                    try:
                        # Convert all ratings to floats
                        ratings = [float(x) for x in row[1:]]
                        program_ratings[program] = ratings
                    except ValueError:
                        # This catches rows with non-numeric data
                        print(f"Warning: Skipping row for '{program}'. Contains non-numeric rating data.")
            
            if not program_ratings:
                # This means the file had a header but no valid data rows
                print(f"Warning: The file '{file_path}' has a header but no data rows.")
                
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    
    return program_ratings

# Path to the CSV file
# *** THIS IS THE UPDATED LINE ***
file_path = '/content/program_ratings_modified.csv'

# Try to load ratings from the file
ratings = read_csv_to_dict(file_path)

# If loading failed (ratings is empty), use sample data
if not ratings:
    print("Warning: Could not load data from CSV. Using sample data instead.")
    ratings = {
        'News': [4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5],
        'Movie': [3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
        'Sports': [4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5],
        'Comedy': [3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5],
        'Drama': [2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5]
    }

##################################### DEFINING PARAMETERS AND DATASET ################################################################
GEN = 100
POP = 50
CO_R = 0.8
MUT_R = 0.2
EL_S = 2

all_programs = list(ratings.keys()) # all programs
all_time_slots = list(range(6, 24)) # time slots [6, 7, ..., 23]
SCHEDULE_LENGTH = len(all_time_slots) # This is 18

# This check is now the final safeguard
if not all_programs:
    raise ValueError("Critical
