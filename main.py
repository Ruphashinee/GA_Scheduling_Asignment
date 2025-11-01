import csv
import random

########################################
# STEP 1 — READ CSV FILE
########################################
def read_csv_to_dict(file_path):
    program_ratings = {}
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip header row
        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]  # Convert ratings to floats
            program_ratings[program] = ratings
    return program_ratings

# Update this path to match your file location
file_path = "program_ratings_modified.csv"

# Read data
ratings = read_csv_to_dict(file_path)

########################################
# STEP 2 — DEFINE PARAMETERS
########################################
GEN = 100          # Number of generations
POP = 50           # Population size
CO_R = 0.8         # Default crossover rate
MUT_R = 0.2        # Default mutation rate
EL_S = 2           # Elitism size

all_programs = list(ratings.keys())
all_time_slots = list(range(6, 24))  # Time slots 6AM–11PM

########################################
# STEP 3 — FITNESS FUNCTION
########################################
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

########################################
# STEP 4 — POPULATION INITIALIZATION
########################################
def initialize_pop(programs, population_size):
    population = []
    for _ in range(population_size):
        schedule = random.sample(programs, len(programs))
        population.append(schedule)
    return population

########################################
# STEP 5 — GENETIC OPERATORS
########################################
def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

def mutate(schedule):
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

########################################
# STEP 6 — GENETIC ALGORITHM CORE
########################################
def genetic_algorithm(programs, generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
    population = initialize_pop(programs, population_size)

    for generation in range(generations):
        # Sort population by fitness (descending)
        population.sort(key=lambda s: fitness_function(s), reverse=True)
        new_population = population[:elitism_size]  # Elitism

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)

            # Crossover
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            # Mutation
            if random.random() < mutation_rate:
                mutate(child1)
            if random.random() < mutation_rate:
                mutate(child2)

            new_population.extend([child1, child2])

        population = new_population[:population_size]

    # Return the best schedule
    best = max(population, key=lambda s: fitness_function(s))
    return best

########################################
# STEP 7 — RUN & DISPLAY RESULTS
########################################
best_schedule = genetic_algorithm(all_programs)

print("\nFinal Optimal Schedule:")
for time_slot, program in enumerate(best_schedule):
    print(f"Time Slot {all_time_slots[time_slot]:02d}:00 - Program {program}")

print("\nTotal Ratings:", fitness_function(best_schedule))
