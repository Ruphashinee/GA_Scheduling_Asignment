import csv
import random

# Function to read the CSV file and convert it to the desired format
def read_csv_to_dict(file_path):
    program_ratings = {}
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            # Skip the header
            header = next(reader)
            
            for row in reader:
                program = row[0]
                # Ensure row has enough columns before processing
                if len(row) > 1:
                    ratings = [float(x) for x in row[1:]]  # Convert the ratings to floats
                    program_ratings[program] = ratings
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print("Using sample data instead.")
        # Provide sample data if file is missing, so the script can run
        program_ratings = {
            'News': [4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5],
            'Movie': [3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
            'Sports': [4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5],
            'Comedy': [3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5],
            'Drama': [2.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0, 3.5]
        }
    return program_ratings

# Path to the CSV file
file_path = '/content/program_ratings.csv'
ratings = read_csv_to_dict(file_path)

##################################### DEFINING PARAMETERS AND DATASET ################################################################
GEN = 100
POP = 50
CO_R = 0.8
MUT_R = 0.2
EL_S = 2

all_programs = list(ratings.keys()) # all programs
all_time_slots = list(range(6, 24)) # time slots [6, 7, ..., 23]
SCHEDULE_LENGTH = len(all_time_slots) # This is 18

# Ensure we have programs to work with
if not all_programs:
    raise ValueError("No programs loaded. Check your CSV file or sample data.")

######################################### DEFINING FUNCTIONS ########################################################################

# defining fitness function (This was correct)
def fitness_function(schedule):
    total_rating = 0
    # A schedule is a list of programs, e.g., ['News', 'Movie', 'Sports', ...]
    # The index 'time_slot' (0, 1, 2...) corresponds to the rating index
    for time_slot, program in enumerate(schedule):
        # Check if the program in the schedule is valid
        if program in ratings:
             # Ensure the ratings list is long enough
            if time_slot < len(ratings[program]):
                total_rating += ratings[program][time_slot]
            else:
                # This would happen if a program's rating list is shorter than the schedule
                print(f"Warning: Rating for program '{program}' at time slot {time_slot} is missing.")
        else:
            # This would happen if a mutated schedule has a program not in 'ratings'
            print(f"Warning: Program '{program}' not found in ratings directory.")
            
    return total_rating

# *** NEW FUNCTION ***
# Create a single, completely random schedule
def create_random_schedule():
    # A schedule is a list of [program, program, ...]
    # with length equal to the number of time slots.
    return [random.choice(all_programs) for _ in range(SCHEDULE_LENGTH)]

# Crossover (This was correct for an assignment problem)
def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, SCHEDULE_LENGTH - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

# Mutating (This was correct for an assignment problem)
def mutate(schedule):
    # Create a copy to avoid modifying the original schedule directly
    schedule_copy = schedule.copy()
    mutation_point = random.randint(0, SCHEDULE_LENGTH - 1)
    new_program = random.choice(all_programs)
    schedule_copy[mutation_point] = new_program
    return schedule_copy

# *** MODIFIED GENETIC ALGORITHM ***
def genetic_algorithm(generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):

    # 1. Initialize a PROPER population of random schedules
    population = [create_random_schedule() for _ in range(population_size)]
    
    best_schedule_ever = []
    best_fitness_ever = 0

    for generation in range(generations):
        # Evaluate fitness of all individuals
        pop_with_fitness = []
        for schedule in population:
            fitness = fitness_function(schedule)
            pop_with_fitness.append((schedule, fitness))
            
            # Keep track of the best schedule found so far
            if fitness > best_fitness_ever:
                best_fitness_ever = fitness
                best_schedule_ever = schedule

        # Sort the population by fitness (highest first)
        pop_with_fitness.sort(key=lambda x: x[1], reverse=True)
        
        # Start building the new population
        new_population = []

        # Elitism: Add the best 'elitism_size' individuals directly
        for i in range(elitism_size):
            new_population.append(pop_with_fitness[i][0])

        # Fill the rest of the population
        while len(new_population) < population_size:
            # Selection (using the sorted list, better than random.choices)
            # This is a simple form of tournament selection (picking from the top 50%)
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
            # Avoid overshooting the population size
            if len(new_population) < population_size:
                new_population.append(child2)

        population = new_population

    # After all generations, return the best schedule found
    return best_schedule_ever, best_fitness_ever

##################################################### RESULTS ###################################################################################

# *** REMOVED ALL THE BRUTE FORCE AND PATCHING CODE ***

# Call the corrected Genetic Algorithm
final_schedule, final_rating = genetic_algorithm()

print("Final Optimal Schedule (from GA):")
for time_slot, program in enumerate(final_schedule):
    print(f"Time Slot {all_time_slots[time_slot]:02d}:00 - Program {program}")

print(f"\nTotal Ratings: {final_rating:.2f}")
