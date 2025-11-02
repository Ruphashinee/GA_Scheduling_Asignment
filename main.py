import random
import pandas as pd

# === Load Data ===
def load_data(path):
    """Load program ratings from CSV file"""
    data = pd.read_csv(path)
    print("Columns detected in dataset:", list(data.columns))
    return data

# === Initialize Population ===
def init_population(programs, pop_size=10):
    """Generate random schedules (permutations of programs)"""
    return [random.sample(programs, len(programs)) for _ in range(pop_size)]

# === Fitness Function ===
def fitness(schedule, ratings):
    """Calculate total rating as fitness value"""
    return sum(ratings[p] for p in schedule)

# === Selection ===
def selection(pop, ratings):
    """Select top two individuals with best fitness"""
    return sorted(pop, key=lambda s: fitness(s, ratings), reverse=True)[:2]

# === Crossover ===
def crossover(parent1, parent2, co_rate):
    """Perform single-point crossover"""
    if random.random() < co_rate:
        point = random.randint(1, len(parent1) - 2)
        child = parent1[:point] + [p for p in parent2 if p not in parent1[:point]]
        return child
    return parent1.copy()

# === Mutation ===
def mutate(schedule, mut_rate):
    """Swap two random positions"""
    if random.random() < mut_rate:
        i, j = random.sample(range(len(schedule)), 2)
        schedule[i], schedule[j] = schedule[j], schedule[i]
    return schedule

# === Genetic Algorithm ===
def genetic_algorithm(data, co_rate=0.8, mut_rate=0.02, generations=50, pop_size=10):
    """Main GA loop with robust column detection"""

    # --- Flexible program column detection ---
    program_col_candidates = ['Program', 'Type of Program', 'Show', 'Title']
    program_col = None
    for col in program_col_candidates:
        if col in data.columns:
            program_col = col
            break
    if program_col is None:
        raise KeyError(f"Dataset must contain a program column. Tried: {program_col_candidates}")

    # --- Flexible rating column detection ---
    rating_col_candidates = ['Rating', 'Ratings', 'Score', 'Popularity']
    rating_col = None
    for col in rating_col_candidates:
        if col in data.columns:
            rating_col = col
            break
    if rating_col is None:
        raise KeyError(f"Dataset must contain a rating column. Tried: {rating_col_candidates}")

    # --- Prepare programs and ratings dictionary ---
    programs = list(data[program_col])
    ratings = dict(zip(data[program_col], data[rating_col]))

    # --- Initialize population ---
    population = init_population(programs, pop_size)

    # --- Evolution loop ---
    for _ in range(generations):
        new_population = []
        for _ in range(pop_size):
            parents = selection(population, ratings)
            child = crossover(parents[0], parents[1], co_rate)
            child = mutate(child, mut_rate)
            new_population.append(child)
        population = new_population

    # --- Get best schedule ---
    best_schedule = selection(population, ratings)[0]
    best_fitness = fitness(best_schedule, ratings)

    return best_schedule, best_fitness
