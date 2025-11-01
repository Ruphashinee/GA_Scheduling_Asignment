import csv
import random

# ============================ READ CSV DATA ===============================

def read_csv_to_dict(file_path):
    program_ratings = {}

    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)  # skip header

        for row in reader:
            program = row[0]
            ratings = [float(x) for x in row[1:]]  # convert ratings to float
            program_ratings[program] = ratings

    return program_ratings

# Path to your CSV file (change name if needed)
file_path = 'program_ratings_modified.csv'
program_ratings_dict = read_csv_to_dict(file_path)

# ==========================================================================

# Dataset
ratings = program_ratings_dict
all_programs = list(ratings.keys())
num_slots = len(next(iter(ratings.values())))  # total time slots (e.g., 18)
time_slots = list(range(6, 6 + num_slots))     # 6 AM to midnight

# ========================== GA PARAMETERS =================================
GEN = 200            # number of generations
POP = 50             # population size
CO_R = 0.8           # crossover rate
MUT_R = 0.02         # mutation rate (within range 0.01–0.05)
EL_S = 2             # elitism count
# ==========================================================================


# ======================== FITNESS FUNCTION ================================

def fitness_function(schedule):
    """Calculate total rating for a given schedule"""
    total = 0
    for i, program in enumerate(schedule):
        total += ratings[program][i]
    return total


# ========================== GA FUNCTIONS ==================================

def initialize_population(programs, pop_size, num_slots):
    """Create random initial population"""
    population = []
    for _ in range(pop_size):
        individual = random.choices(programs, k=num_slots)
        population.append(individual)
    return population


def crossover(parent1, parent2, crossover_rate):
    """Single-point crossover"""
    if random.random() < crossover_rate:
        point = random.randint(1, len(parent1) - 2)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
    else:
        child1, child2 = parent1.copy(), parent2.copy()
    return child1, child2


def mutate(individual, mutation_rate, programs):
    """Random mutation"""
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            individual[i] = random.choice(programs)
    return individual


def select_parents(population, fitness_scores):
    """Tournament selection"""
    tournament_size = 3
    participants = random.sample(list(zip(population, fitness_scores)), tournament_size)
    best = max(participants, key=lambda x: x[1])
    return best[0]


# ========================== MAIN GA LOOP ==================================

def genetic_algorithm():
    population = initialize_population(all_programs, POP, num_slots)
    best_individual = None
    best_fitness = float('-inf')

    for gen in range(GEN):
        fitness_scores = [fitness_function(ind) for ind in population]

        # Keep best
        sorted_pop = [x for _, x in sorted(zip(fitness_scores, population), reverse=True)]
        population = sorted_pop

        if fitness_scores[0] > best_fitness:
            best_fitness = fitness_scores[0]
            best_individual = population[0]

        new_population = population[:EL_S]  # elitism

        while len(new_population) < POP:
            parent1 = select_parents(population, fitness_scores)
            parent2 = select_parents(population, fitness_scores)
            child1, child2 = crossover(parent1, parent2, CO_R)
            child1 = mutate(child1, MUT_R, all_programs)
            child2 = mutate(child2, MUT_R, all_programs)
            new_population.extend([child1, child2])

        population = new_population[:POP]

    return best_individual, best_fitness


# ========================== RUN TRIALS ====================================

for trial in range(1, 4):
    print(f"\n=================== TRIAL {trial} ===================")
    best_schedule, total_rating = genetic_algorithm()
    for i, program in enumerate(best_schedule):
        print(f"Time Slot {time_slots[i]:02d}:00 - {program}")
    print("Total Ratings:", round(total_rating, 3))
