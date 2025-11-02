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
    # THIS IS THE LINE THAT LIKELY CAUSED YOUR ERROR
    raise ValueError("Critical Error: No programs available from CSV or sample data. The script cannot continue.")

######################################### DEFINING FUNCTIONS ########################################################################

# defining fitness function
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        if program in ratings:
            if time_slot < len(ratings[program]):
                total_rating += ratings[program][time_slot]
            else:
                print(f"Warning: Rating for program '{program}' at time slot {time_slot} is missing.")
        else:
            print(f"Warning: Program '{program}' not found in ratings directory.")
    return total_rating

# Create a single, completely random schedule
def create_random_schedule():
    return [random.choice(all_programs) for _ in range(SCHEDULE_LENGTH)]

# Crossover
def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, SCHEDULE_LENGTH - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

# Mutating
def mutate(schedule):
    schedule_copy = schedule.copy()
    mutation_point = random.randint(0, SCHEDULE_LENGTH - 1)
    new_program = random.choice(all_programs)
    schedule_copy[mutation_point] = new_program
    return schedule_copy

# genetic algorithm
def genetic_algorithm(generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):

    population = [create_random_schedule() for _ in range(population_size)]
    
    best_schedule_ever = []
    best_fitness_ever = 0

    for generation in range(generations):
        pop_with_fitness = []
        for schedule in population:
            fitness = fitness_function(schedule)
            pop_with_fitness.append((schedule, fitness))
            
            if fitness > best_fitness_ever:
                best_fitness_ever = fitness
                best_schedule_ever = schedule

        pop_with_fitness.sort(key=lambda x: x[1], reverse=True)
        
        new_population = []

        # Elitism
        for i in range(elitism_size):
            new_population.append(pop_with_fitness[i][0])

        while len(new_population) < population_size:
            # Selection
            parent1 = random.choice(pop_with_fitness[:population_size // 2])[0]
            parent2 = random.choice(pop_with_fitness[:population_size // 2])[0]

            # Crossover
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            # Mutation
            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.append(child1)
            if len(new_population) < population_size:
                new_population.append(child2)

        population = new_population

    # Return the best one found across all generations
    return best_schedule_ever, best_fitness_ever

##################################################### RESULTS ###################################################################################

# Call the Genetic Algorithm
final_schedule, final_rating = genetic_algorithm()

print("\nFinal Optimal Schedule (from GA):")
if not final_schedule:
    print("No valid schedule could be generated.")
else:
    for time_slot, program in enumerate(final_schedule):
        # Handle cases where all_time_slots might be shorter than final_schedule
        if time_slot < len(all_time_slots):
            print(f"Time Slot {all_time_slots[time_slot]:02d}:00 - Program {program}")
        else:
            print(f"Extra Time Slot {time_slot}: Program {program}")

print(f"\nTotal Ratings: {final_rating:.2f}")
