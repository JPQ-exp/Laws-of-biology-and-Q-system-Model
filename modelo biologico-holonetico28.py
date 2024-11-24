import numpy as np
import typing as t

class BioHoloneticModel:
    def __init__(
        self, 
        n_dimensions: int, 
        n_clusters: int,
        noise_sigma: float = 0.1
    ):
        """
        Initialize the Bio-Holonetic Model
        
        Parameters:
        - n_dimensions: State space dimensionality
        - n_clusters: Number of regulatory clusters
        - noise_sigma: Standard deviation for external noise
        """
        self.n_dimensions = n_dimensions
        self.n_clusters = n_clusters
        self.noise_sigma = noise_sigma
        
        # Initialize state variables
        self.state = np.zeros(n_dimensions)
        self.prev_state = np.zeros(n_dimensions)
        
        # Goal vector with specific fixed numbers inside them and a fixed number of them
        self.goals = np.array([
            [1, 2, 3],  # First goal
            [-1, -2, -3],  # Second goal
            [0.5, 0.5, 0.5]   # Third goal
        ])
        
        # Fixed cluster configurations with twin clusters and opposite signs
        self.clusters_positive = np.array([
            [0.9, 0.5, 0.3],
            [0.3, 0.9, 0.5],
            [0.5, 0.3, 0.9]
        ])
        self.clusters_negative = -self.clusters_positive  # Corrected negative cluster creation
        
        # Initialize the cue generator
        self.cue_generator = np.random.RandomState()

        # Initialize the current goal
        self.goal = self.goals[0]

        # Counter for stop signal condition
        self.stop_counter = 0
        self.stop_threshold = 5

    def compute_delta_state(self, external_force: np.ndarray) -> np.ndarray:
        """
        Compute state change based on regulated clusters and external force.
    
        Equation 1: Δst = ∑(D_i * c_i) + F_t
        """
        # Compute delta as the difference between state and goal
        delta = self.state - self.goal
        print(f"Delta: {delta}")

        # Check for stop condition
        if np.any(np.abs(delta) > 3):
            self.stop_counter += 1
        else:
            self.stop_counter = 0  # Reset counter if condition is not met

        # Compute cluster contributions
        cluster_contributions = np.zeros(self.n_dimensions)

        for i in range(self.n_dimensions):
            # Determine the cluster (positive or negative) to regulate
            if delta[i] < 0:
                # Select the negative cluster for the current dimension
                selected_cluster = self.clusters_negative[:, i]
            else:
                # Select the positive cluster for the current dimension
                selected_cluster = self.clusters_positive[:, i]

            # Compute dynamic regulation factor
            Di = self._compute_dynamic_regulation(delta, i)

            # Regulate the entire selected cluster
            regulated_cluster = Di * selected_cluster
            cluster_contributions[i] += np.sum(regulated_cluster)

            # Add contributions from non-selected clusters
            for j in range(self.n_clusters):
                if np.all(self.clusters_positive[j, i] != selected_cluster):
                    cluster_contributions[i] += self.clusters_positive[j, i]
                if np.all(self.clusters_negative[j, i] != selected_cluster):
                    cluster_contributions[i] += self.clusters_negative[j, i]

            print(f"Dimension {i}: Regulated Cluster = {regulated_cluster}, Total Contribution = {cluster_contributions[i]}")

        # Add external force with noise
        noise = np.random.normal(0, self.noise_sigma, self.n_dimensions)
        external_force_with_noise = external_force + noise

        delta_state = cluster_contributions + external_force_with_noise
        return delta_state

    
    def _compute_dynamic_regulation(self, delta: np.ndarray, cluster_idx: int) -> float:
        """
        Compute dynamic regulation factor for a cluster
    
        Use a combination of a fixed amplification factor and a sigmoid activation
        """
        # Sigmoid function to determine regulation strength
        sigmoid_activation = lambda x: 1.5 / (1 + np.exp(-x)) - 1  # Adjusted sigmoid to range [-1, 1]
    
        # Calculate the activation level based on delta
        # Scaling the dot product to ensure a meaningful range for sigmoid input
        activation_level = np.dot(delta, self.clusters_positive[cluster_idx]) * 10
        regulation_factor = sigmoid_activation(activation_level)
    
        return regulation_factor
    
    def trigger_goal_transition(
    self, 
    external_input: t.Optional[np.ndarray] = None
) -> np.ndarray:
        """
        Goal transition mechanism with internal state dependency.
    
        Conditions:
        1. Cue-based trigger selects the second goal.
        2. State-based trigger selects the first goal.
        3. Out-of-range delta for 3 turns selects the third goal.
        4. Otherwise, the goal remains unchanged.
        """
        # Cue-based trigger
        cue = self.cue_generator.randint(1, 6)  # Random cue between 1 and 5
        if cue == 5:
            print("Cue-based trigger activated. Switching to the second goal.")
            return self.goals[1]  # Second goal

        # State-based trigger
        transition_mask = self._identify_transition_regions()
        if np.any(transition_mask):
            print("State-based trigger activated. Switching to the first goal.")
            return self.goals[0]  # First goal

    # Out-of-range trigger
        if self.stop_counter >= 3:
            print("Out-of-range trigger activated. Switching to the third goal.")
            return self.goals[2]  # Third goal

        # No trigger, retain current goal
        print("No trigger activated. Retaining current goal.")
        return self.goal

    
    def _identify_transition_regions(self) -> np.ndarray:
        """
        Identify critical regions in state space for goal transition.
        """
        # Example transition criteria: specific state ranges or patterns
        transition_mask = (
            (self.state > 0.8) | 
            (self.state < -0.8) | 
            (np.abs(self.state) < 0.1)
        )
        return transition_mask

    
    def update(self, external_force: np.ndarray) -> bool:
        """
        Update system state in a single time step.
    
        Returns:
        - A boolean indicating whether the simulation should continue.
        """
        # Compute state change
        delta_state = self.compute_delta_state(external_force)
    
        # Update state
        self.prev_state = self.state.copy()
        self.state += delta_state
    
        # Trigger goal transition if necessary
        self.goal = self.trigger_goal_transition()

        # Check if stop condition is met
        return self.stop_counter < self.stop_threshold


# Example usage and demonstration
def main():
    model = BioHoloneticModel(n_dimensions=3, n_clusters=3, noise_sigma=0.1)
    
    # Simulate several time steps
    for t in range(100):
        external_force = np.random.uniform(-0.5, 0.5, 3)
        continue_simulation = model.update(external_force)
        print(f"Time {t}: State = {model.state}, Goal = {model.goal}")
        
        if not continue_simulation:
            print("Simulation stopped due to delta exceeding threshold for consecutive iterations.")
            break

if __name__ == "__main__":
    main()
