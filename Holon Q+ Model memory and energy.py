import random

class CoreHolon:
    def __init__(self, starting_energy, starting_materials):
        self.energy = starting_energy
        self.materials = starting_materials
        self.dopamine = 0
        self.pain = 0

    def modulate(self, waste_holon, energy_holon, energy_disposal_holon):
        waste_holon.reset()
        energy_holon.reset()
        energy_disposal_holon.reset()

        if self.energy < 30:
            energy_holon.amplify()
            energy_disposal_holon.suppress()
        elif self.energy > 70:
            energy_disposal_holon.amplify()
            energy_holon.suppress()

        if self.materials < 30:
            waste_holon.suppress()
        elif self.materials > 70:
            waste_holon.amplify()

class PerceptionHolon:
    def perceive(self, num_rewards=6, reward_cost_percentage=0.25):
        rewards = [random.randint(5, 20) for _ in range(num_rewards)]
        energy_costs = [reward_cost_percentage * reward for reward in rewards]
        return rewards, energy_costs

class ActionHolon:
    def act(self, core_holon, reward, energy_cost):
        core_holon.energy -= energy_cost
        core_holon.materials += reward

class WasteHolon:
    def __init__(self):
        self.activity_level = 1

    def dispose(self, core_holon):
        if core_holon.materials > 70:
            core_holon.materials -= self.activity_level * 5

    def amplify(self):
        self.activity_level = 2

    def suppress(self):
        self.activity_level = 0.5

    def reset(self):
        self.activity_level = 1

class EnergyHolon:
    def __init__(self, materials_needed, energy_generated):
        self.activity_level = 1
        self.materials_needed = materials_needed
        self.energy_generated = energy_generated

    def convert(self, core_holon):
        materials_needed = self.materials_needed * self.activity_level
        energy_generated = self.energy_generated * self.activity_level
        if core_holon.materials >= materials_needed:
            core_holon.materials -= materials_needed
            core_holon.energy += energy_generated

    def amplify(self):
        self.activity_level = 2

    def suppress(self):
        self.activity_level = 0.5

    def reset(self):
        self.activity_level = 1

class EnergyDisposalHolon:
    def __init__(self):
        self.activity_level = 1

    def dispose(self, core_holon):
        if core_holon.energy > 70:
            core_holon.energy -= self.activity_level * 5

    def amplify(self):
        self.activity_level = 2

    def suppress(self):
        self.activity_level = 0.5

    def reset(self):
        self.activity_level = 1

class MemoryHolon:
    def __init__(self, max_memory_size=6):
        self.max_memory_size = max_memory_size
        self.memory = []

    def remember(self, reward, feedback_type, feedback_value, core_holon):
        if feedback_type == 'dopamine':
            outcome_tag = 'h' if 30 <= core_holon.energy <= 70 and 30 <= core_holon.materials <= 70 else '-h'
        elif feedback_type == 'pain':
            outcome_tag = '-h' if core_holon.energy < 30 or core_holon.materials < 30 else 'h'
        else:
            outcome_tag = '-h'  # Default to negative outcome for unrecognized feedback_type

        self.memory.append((reward, feedback_type, feedback_value, outcome_tag))
        self.memory.sort(key=lambda x: abs(x[2]), reverse=True)
        if len(self.memory) > self.max_memory_size:
            self.memory.pop()

    def get_significant_feedback(self):
        dopamine_feedback = [item for item in self.memory if item[1] == 'dopamine']
        pain_feedback = [item for item in self.memory if item[1] == 'pain']
        return dopamine_feedback, pain_feedback

class SuperHolon:
    def __init__(self, core_holon, perception_holon, action_holon, waste_holon, energy_holon, energy_disposal_holon, memory_holon, energy_maintenance_cost, reward_cost_percentage, materials_needed, energy_generated):
        self.core_holon = core_holon
        self.perception_holon = perception_holon
        self.action_holon = action_holon
        self.waste_holon = waste_holon
        self.energy_holon = energy_holon
        self.energy_disposal_holon = energy_disposal_holon
        self.memory_holon = memory_holon
        self.energy_maintenance_cost = energy_maintenance_cost
        self.reward_cost_percentage = reward_cost_percentage
        self.materials_needed = materials_needed
        self.energy_generated = energy_generated

    def make_decision(self):
        rewards, energy_costs = self.perception_holon.perceive(reward_cost_percentage=self.reward_cost_percentage)
        
        valid_choices = [(reward, cost) for reward, cost in zip(rewards, energy_costs) if cost <= self.core_holon.energy]
        
        if not valid_choices:
            return None, None, -1

        rewards, energy_costs = zip(*valid_choices)

        dopamine_feedback, pain_feedback = self.memory_holon.get_significant_feedback()

        best_choice = None
        highest_dopamine = float('-inf')
        lowest_pain = float('inf')

        for i, (reward, cost) in enumerate(zip(rewards, energy_costs)):
            dopamine_memory = sum(val for rwd, mem, val, tag in dopamine_feedback if rwd == reward)
            pain_memory = sum(val for rwd, mem, val, tag in pain_feedback if rwd == reward)
            if dopamine_memory - pain_memory > highest_dopamine - lowest_pain:
                best_choice = i
                highest_dopamine = dopamine_memory
                lowest_pain = pain_memory

        if best_choice is not None:
            return rewards, energy_costs, best_choice

        # No significant feedback, choose randomly
        chosen_index = random.choice(range(len(rewards)))
        return rewards, energy_costs, chosen_index

    def simulate_step(self):
        rewards, energy_costs, chosen_index = self.make_decision()
        if chosen_index == -1:
            print("  No valid reward to choose from.")
            return False

        reward = rewards[chosen_index]
        energy_cost = energy_costs[chosen_index]

        print(f"  Available rewards: {rewards}")
        print(f"  Selected reward: {reward} with energy cost: {energy_cost}")

        self.action_holon.act(self.core_holon, reward, energy_cost)
        
        self.core_holon.energy -= self.energy_maintenance_cost

        self.core_holon.modulate(self.waste_holon, self.energy_holon, self.energy_disposal_holon)
        self.waste_holon.dispose(self.core_holon)
        self.energy_holon.convert(self.core_holon)
        self.energy_disposal_holon.dispose(self.core_holon)

        was_successful = 30 <= self.core_holon.energy <= 70 and 30 <= self.core_holon.materials <= 70
        feedback_type = 'dopamine' if was_successful else 'pain'
        feedback_value = reward if was_successful else -reward
        self.memory_holon.remember(reward, feedback_type, feedback_value, self.core_holon)

        print(f"  Energy = {self.core_holon.energy}, Materials = {self.core_holon.materials}")
        print(f"  Waste Level = {self.waste_holon.activity_level}, Energy Level = {self.energy_holon.activity_level}, Energy Disposal Level = {self.energy_disposal_holon.activity_level}")
        print(f"  Dopamine = {self.core_holon.dopamine}, Pain = {self.core_holon.pain}")
        print(f"  Memory: {self.memory_holon.memory}")

        return self.core_holon.energy > 0 and self.core_holon.materials > 0

# Get user inputs
num_iterations = int(input("Enter the number of iterations: "))
starting_materials = int(input("Enter the starting materials: "))
starting_energy = int(input("Enter the starting energy: "))
energy_maintenance_cost = float(input("Enter the energy maintenance cost: "))
reward_cost_percentage = float(input("Enter the reward cost percentage (e.g., 0.25 for 25%): "))
materials_needed = int(input("Enter the materials needed for energy conversion: "))
energy_generated = int(input("Enter the energy generated per conversion: "))

# Initialize holons
core_holon = CoreHolon(starting_energy, starting_materials)
perception_holon = PerceptionHolon()
action_holon = ActionHolon()
waste_holon = WasteHolon()
energy_holon = EnergyHolon(materials_needed, energy_generated)
energy_disposal_holon = EnergyDisposalHolon()
memory_holon = MemoryHolon()
super_holon = SuperHolon(core_holon, perception_holon, action_holon, waste_holon, energy_holon, energy_disposal_holon, memory_holon, energy_maintenance_cost, reward_cost_percentage, materials_needed, energy_generated)

# Simulation
for step in range(num_iterations):
    print(f"\nStep {step + 1}:")
    success = super_holon.simulate_step()

    if not success:
        print("System failed to maintain homeostasis. Ending simulation.")
        break

print("\nSimulation complete.")

