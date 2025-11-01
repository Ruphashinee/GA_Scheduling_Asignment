import streamlit as st
import pandas as pd
import numpy as np

# --- 1. GENETIC ALGORITHM CORE FUNCTIONS ---

# Function to load the ratings data
@st.cache_data # Caches the data so we don't reload it every time
def load_data():
    # This line reads the file you uploaded: program_ratings_modified.csv
    df = pd.read_csv("program_ratings_modified.csv") 
    df = df.set_index("Type of Program")
    return df

# Function to create one random "chromosome" (a full 18-hour schedule)
# THIS IS THE CORRECT, RANDOM START
def create_individual(num_programs, num_hours):
    # A schedule is a list of 18 integers, where each integer is the row index of a program
    # e.g., [0, 5, 2, ..., 9] means 'news' at Hour 6, 'tv_series_a' at Hour 7, etc.
    return [np.random.randint(0, num_programs) for _ in range(num_hours)]

# Function to calculate the "fitness" (total rating) of a schedule
def calculate_fitness(individual, ratings_matrix):
    total_rating = 0
    # Loop through each hour (column) in the schedule
    for hour_index, program_index in enumerate(individual):
        # Add the rating for the selected program (row) at that specific hour (column)
        total_rating += ratings_matrix[hour_index, program_index]
    return total_rating

# Function to select two "parents" for breeding
def selection(population, fitness_scores):
    # This is "Tournament Selection"
    # Pick 3 random individuals and return the one with the best fitness
    def tournament():
        tournament_size = 3
        competitor_indices = np.random.choice(len(population), tournament_size, replace=False)
        competitor_fitnesses = [fitness_scores[i] for i in competitor_indices]
        winner_index = competitor_indices[np.argmax(competitor_fitnesses)]
        return population[winner_index]

    parent1 = tournament()
    parent2 = tournament()
    return parent1, parent2

# Function to "breed" two parents to create a child
def crossover(parent1, parent2, crossover_rate):
    if np.random.rand() < crossover_rate:
        # Perform single-point crossover
        split_point = np.random.randint(1, len(parent1) - 1)
        child = parent1[:split_point] + parent2[split_point:]
        return child
    else:
        # No crossover, just return one of the parents
        return parent1

# Function to apply random "mutations" to a child
def mutate(individual, mutation_rate, num_programs):
    mutated_individual = individual[:]
    for i in range(len(mutated_individual)):
        if np.random.rand() < mutation_rate:
            # Change this hour's program to a new random one
            mutated_individual[i] = np.random.randint(0, num_programs)
    return mutated_individual

# --- 2. STREAMLIT USER INTERFACE ---

st.set_page_config(layout="wide")
st.title("📺 TV Schedule Genetic Algorithm")
st.write("This app finds the best 18-hour TV schedule to maximize audience ratings using a Genetic Algorithm.")

# --- Parameter Input (Task 3) ---
st.sidebar.header("Genetic Algorithm Parameters")

# Note on the parameter contradiction:
st.sidebar.info(
    "**Note:** The assignment's default `MUT_R` (0.2) was outside its "
    "allowed range (0.01-0.05). We are assuming the range is correct "
    "and have set the default to **0.02**."
)

# Sliders for GA parameters
CO_R = st.sidebar.slider(
    "Crossover Rate (CO_R)",
    min_value=0.0,
    max_value=0.95,
    value=0.8, # Default value
    step=0.05
)

MUT_R = st.sidebar.slider(
    "Mutation Rate (MUT_R)",
    min_value=0.01,
    max_value=0.05,
    value=0.02, # Corrected default value
    step=0.005
)

# Added more parameters for better control
POPULATION_SIZE = st.sidebar.number_input("Population Size", min_value=20, max_value=1000, value=100)
GENERATIONS = st.sidebar.number_input("Number of Generations", min_value=10, max_value=2000, value=200)

# --- 3. RUN ALGORITHM AND DISPLAY RESULTS ---

if st.sidebar.button("Run Algorithm", type="primary"):
    # Load the data
    ratings_df = load_data()
    program_names = ratings_df.index.tolist()
    hour_names = ratings_df.columns.tolist()
    
    # Convert dataframe to numpy array for much faster fitness calculation
    # We transpose it (.T) so that hours are rows and programs are columns,
    # which makes lookup easier: ratings_matrix[hour, program]
    ratings_matrix = ratings_df.to_numpy().T 
    
    num_programs = len(program_names)
    num_hours = len(hour_names)

    # --- Main GA Loop ---
    st.write(f"Running GA with {GENERATIONS} generations, {POPULATION_SIZE} individuals...")
    
    # 1. Create initial population
    # THIS IS THE CORRECT, RANDOM POPULATION
    population = [create_individual(num_programs, num_hours) for _ in range(POPULATION_SIZE)]

    best_schedule = None
    best_fitness = -1

    # Keep track of progress
    progress_bar = st.progress(0)
    
    for gen in range(GENERATIONS):
        # 2. Calculate fitness for all
        fitness_scores = [calculate_fitness(ind, ratings_matrix) for ind in population]

        new_population = []
        
        # Elitism: Keep the best individual from this generation
        best_gen_index = np.argmax(fitness_scores)
        best_gen_fitness = fitness_scores[best_gen_index]
        best_gen_schedule = population[best_gen_index]
        
        if best_gen_fitness > best_fitness:
            best_fitness = best_gen_fitness
            best_schedule = best_gen_schedule
            
        new_population.append(best_schedule) # Add the best one to the new population

        # 3. Create the rest of the new generation
        while len(new_population) < POPULATION_SIZE:
            # 4. Selection
            parent1, parent2 = selection(population, fitness_scores)
            
            # 5. Crossover
            child = crossover(parent1, parent2, CO_R)
            
            # 6. Mutation
            child = mutate(child, MUT_R, num_programs)
            
            new_population.append(child)
        
        population = new_population
        progress_bar.progress((gen + 1) / GENERATIONS)
    
    st.success(f"Algorithm finished! Best possible schedule found.")

    # --- Display Schedule in Table (Task 4) ---
    
    st.header(f"Best Schedule (Total Rating: {best_fitness:.3f})")
    
    # Get the names of the programs from the best schedule's indices
    schedule_program_names = [program_names[i] for i in best_schedule]
    
    # Get the ratings for each of those programs at each hour
    schedule_ratings = []
    for hour_index, program_index in enumerate(best_schedule):
        schedule_ratings.append(ratings_df.iloc[program_index, hour_index])

    # Create the final table
    final_schedule_df = pd.DataFrame({
        "Hour": hour_names,
        "Scheduled Program": schedule_program_names,
        "Rating for this Hour": schedule_ratings
    })
    
    st.dataframe(final_schedule_df)
    
    st.info("To run another trial (Task 5), change the parameters in the sidebar and click 'Run Algorithm' again.")
