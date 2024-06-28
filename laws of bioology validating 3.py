import random

# Define parameters
INITIAL_TEMPERATURE = 37.0
TEMPERATURE_RANGE = (36.5, 37.5)
EXTERNAL_TEMPERATURE_RANGE = (10.0, 40.0)
NUM_FOOD_OPTIONS = 6
ENERGY_COST = 0.25
TEMPERATURE_INCREASE_COST = 0.25
ENERGY_THRESHOLD = 0.2
P = 5
ALPHA = 0.5
BETA = 0.3
INITIAL_ENERGY = float(input('Enter initial energy: '))
NUM_ITERATIONS = int(input('Enter number of iterations: '))

# Initialize states
internal_temperature = INITIAL_TEMPERATURE
energy = INITIAL_ENERGY
num_iterations_out_of_temp_range = 0

# Generate p-adic metadata
def generate_p_adic_metadata(p, max_terms=100):
    metadata = 0
    for n in range(max_terms):
        coefficient = random.randint(0, p-1)
        metadata += coefficient * (p ** n)
    return metadata

# Activation function
def receptor_activation(metadata):
    return metadata

# Holon classes
class Holon:
    def __init__(self, initial_state):
        self.state = initial_state
    
    def process_metadata(self, metadata):
        return receptor_activation(metadata)

class CoreHolon(Holon):
    def __init__(self, initial_state):
        super().__init__(initial_state)
        self.clusters = []
    
    def regulate_clusters(self, metadata):
        for cluster in self.clusters:
            cluster.update_state(metadata)
    
    def update_state(self, metadata):
        self.state = (self.state + receptor_activation(metadata)) % (P ** len(str(self.state)))

class ClusterHolon(Holon):
    def update_state(self, metadata):
        self.state = (self.state + receptor_activation(metadata)) % (P ** len(str(self.state)))

# Initialize holons
core = CoreHolon(0)
clusters = [ClusterHolon(i) for i in range(1, NUM_FOOD_OPTIONS + 1)]
core.clusters = clusters

# Simulate the process
for iteration in range(NUM_ITERATIONS):
    if energy <= 0 or num_iterations_out_of_temp_range > 5:
        print("Simulation ended due to energy depletion or excessive temperature deviation.")
        break

    external_temperature = random.uniform(*EXTERNAL_TEMPERATURE_RANGE)
    
    if internal_temperature < TEMPERATURE_RANGE[0]:
        energy -= TEMPERATURE_INCREASE_COST
        internal_temperature += TEMPERATURE_INCREASE_COST * 10
    elif internal_temperature > TEMPERATURE_RANGE[1]:
        internal_temperature -= TEMPERATURE_INCREASE_COST * 10
    
    metadata = generate_p_adic_metadata(P)
    core.update_state(metadata)
    core.regulate_clusters(metadata)
    
    food_energy_values = [random.randint(5, 20) for _ in range(NUM_FOOD_OPTIONS)]
    selected_food_option = random.randint(0, NUM_FOOD_OPTIONS - 1)
    energy_cost = ENERGY_COST
    energy -= energy_cost
    food_energy = food_energy_values[selected_food_option]
    energy += food_energy
    
    if energy < INITIAL_ENERGY * ENERGY_THRESHOLD:
        feedback = "Punishment"
    else:
        feedback = "Reward"
    
    if internal_temperature < TEMPERATURE_RANGE[0] or internal_temperature > TEMPERATURE_RANGE[1]:
        num_iterations_out_of_temp_range += 1
    else:
        num_iterations_out_of_temp_range = 0
    
    if energy > 2 * INITIAL_ENERGY:
        energy = 2 * INITIAL_ENERGY
    
    print(f"Iteration {iteration + 1}:")
    print(f"  External Temperature: {external_temperature:.2f}")
    print(f"  Internal Temperature: {internal_temperature:.2f}")
    print(f"  Energy Level: {energy:.2f}")
    print(f"  Food Energy Values: {food_energy_values}")
    print(f"  Selected Food Option: {selected_food_option + 1}")
    print(f"  Feedback: {feedback}")
    print(f"  Core State: {core.state}\n")

print("Simulation complete.")
