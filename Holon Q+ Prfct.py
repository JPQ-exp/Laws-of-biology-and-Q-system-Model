import random

class CoreHolon:
    def __init__(self, starting_energy, starting_materials):
        self.energy = starting_energy
        self.materials = starting_materials

    def modulate(self, waste_holon, energy_holon, energy_disposal_holon):
        # Reset activity levels to 1 at the start of each modulation
        waste_holon.reset()
        energy_holon.reset()
        energy_disposal_holon.reset()

        # Modulate clusters to maintain homeostasis
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
    def perceive(self, num_rewards=6):
        # Generate random rewards and calculate energy costs
        rewards = [random.randint(5, 20) for _ in range(num_rewards)]
        energy_costs = [0.25 * reward for reward in rewards]
        return rewards, energy_costs

class ActionHolon:
    def __init__(self):
        self.activity_level = 1

    def act(self, core_holon, reward, energy_cost):
        # Spend energy to obtain materials
        core_holon.energy -= energy_cost
        core_holon.materials += reward * self.activity_level

class WasteHolon:
    def __init__(self):
        self.activity_level = 1

    def dispose(self, core_holon):
        if core_holon.materials > 70:
            # Dispose of extra materials
            core_holon.materials -= self.activity_level * 5

    def amplify(self):
        self.activity_level = 2

    def suppress(self):
        self.activity_level = 0.5

    def reset(self):
        self.activity_level = 1

class EnergyHolon:
    def __init__(self):
        self.activity_level = 1

    def convert(self, core_holon):
        if core_holon.materials >= self.activity_level * 3:
            # Convert materials to energy
            core_holon.materials -= self.activity_level * 3
            core_holon.energy += self.activity_level * 5

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
            # Dispose of extra energy
            core_holon.energy -= self.activity_level * 5

    def amplify(self):
        self.activity_level = 2

    def suppress(self):
        self.activity_level = 0.5

    def reset(self):
        self.activity_level = 1

class SuperHolon:
    def __init__(self, core_holon, perception_holon, action_holon, waste_holon, energy_holon, energy_disposal_holon, energy_maintenance_cost):
        self.core_holon = core_holon
        self.perception_holon = perception_holon
        self.action_holon = action_holon
        self.waste_holon = waste_holon
        self.energy_holon = energy_holon
        self.energy_disposal_holon = energy_disposal_holon
        self.energy_maintenance_cost = energy_maintenance_cost

    def make_decision(self):
        rewards, energy_costs = self.perception_holon.perceive()
        valid_choices = [(reward, cost) for reward, cost in zip(rewards, energy_costs) if cost <= self.core_holon.energy]
        
        if not valid_choices:
            return None, None, -1  # No valid choice available

        rewards, energy_costs = zip(*valid_choices)

        if self.core_holon.energy < 30:
            # Select the reward with the lowest energy cost
            chosen_index = energy_costs.index(min(energy_costs))
        elif self.core_holon.materials < 30:
            # Select the reward with the highest material
            chosen_index = rewards.index(max(rewards))
        else:
            # Otherwise, select a random reward
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

        if self.core_holon.energy > energy_cost:
            self.action_holon.act(self.core_holon, reward, energy_cost)
        
        # Subtract the constant energy maintenance cost
        self.core_holon.energy -= self.energy_maintenance_cost
        
        self.core_holon.modulate(self.waste_holon, self.energy_holon, self.energy_disposal_holon)
        self.waste_holon.dispose(self.core_holon)
        self.energy_holon.convert(self.core_holon)
        self.energy_disposal_holon.dispose(self.core_holon)

        print(f"  Energy = {self.core_holon.energy}, Materials = {self.core_holon.materials}")
        print(f"  Waste Level = {self.waste_holon.activity_level}, Energy Level = {self.energy_holon.activity_level}, Energy Disposal Level = {self.energy_disposal_holon.activity_level}")

        return self.core_holon.energy > 0 and self.core_holon.materials > 0

# Get user inputs
num_iterations = int(input("Enter the number of iterations: "))
starting_materials = int(input("Enter the starting materials: "))
starting_energy = int(input("Enter the starting energy: "))
energy_maintenance_cost = float(input("Enter the energy maintenance cost: "))

# Initialize holons
core_holon = CoreHolon(starting_energy, starting_materials)
perception_holon = PerceptionHolon()
action_holon = ActionHolon()
waste_holon = WasteHolon()
energy_holon = EnergyHolon()
energy_disposal_holon = EnergyDisposalHolon()
super_holon = SuperHolon(core_holon, perception_holon, action_holon, waste_holon, energy_holon, energy_disposal_holon, energy_maintenance_cost)

# Simulation
for step in range(num_iterations):  # Simulate for the specified number of steps
    print(f"Step {step+1}:")
    if not super_holon.simulate_step():
        print("Simulation stopped due to zero energy or materials.")
        break

print("Simulation complete.")
