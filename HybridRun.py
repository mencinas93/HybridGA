import random
import math
import tkinter as tk
import matplotlib.pyplot as plt
import time
import numpy as np



max_generations = 1000
pop_size = 100
mutation_rate = 0.2


class Individual:
    def __init__(self, city_ids):
        #initialize an individual with list all city ids. 
        #making sure route starts and ends at same city id
        self.route = list(city_ids)
        self.fitness = None

    def swap_mutation(self):
        # Selects two random cities in the route and swaps their positions.
        index1, index2 = random.sample(range(1, len(self.route) - 1), 2)
        self.route[index1], self.route[index2] = self.route[index2], self.route[index1]
        self.fitness = None
        # Reset fitness to be recalculated
        # Select two random indices within the route, excluding the first and last city.

    def scramble_mutation(self):
        # It selects a random subset of cities and shuffles their order.
        start_index, end_index = sorted(random.sample(range(1, len(self.route) - 1), 2))
        # Shuffles the subset of cities
        subset = self.route[start_index:end_index + 1]
        random.shuffle(subset)
        # Replaces the shuffled subset in the route
        self.route[start_index:end_index + 1] = subset
        self.fitness = None


class Population:
    def __init__(self, size, city_ids):
        # Initialize a population with 'size' individuals, each wih a random route.
        self.individuals = [Individual(city_ids) for _ in range(size)]

    def uniform_crossover(self, parent1, parent2):
        # Uniform Crossover: Combines two parent routes to create two child routes.
        child1 = [-1] * len(parent1.route)
        child2 = [-1] * len(parent2.route)
        # Initialize child routes as lists of -1s.

        # Iterate through each city in the parent routes.
        for i in range(len(parent1.route)):
             # Randomly select a parent to inherit the city from (50% chance each).
            if random.random() < 0.5:
                child1[i] = parent1.route[i]
                child2[i] = parent2.route[i]
            else:
                child1[i] = parent2.route[i]
                child2[i] = parent1.route[i]
        #Fix an invalid routes for complete tour
        child1 = self.fix_invalid_route(child1)
        child2 = self.fix_invalid_route(child2)

        return child1, child2

    def cycle_crossover(self, parent1, parent2):
        # Combines two parent routes using the cycle crossover method.
        cycle = [-1] * len(parent1.route)
        start_idx = 0
        # Initialize a list to represent the cycle and starting index
        while -1 in cycle:
            if cycle[start_index] == -1:
                cycle[start_index] = parent1.route[start_idx]
                next_index = parent2.route.index(cycle[start_idx])
                while next_index != start_idx:
                    cycle[next_index] = parent1.route[next_index]
                    next_index = parent2.route.index(cycle[next_index])
            start_index = cycle.index(-1)
        # keep repeating until all elements in the cycle are filled. 
        # Create offspring routes based on the cycle
        child1 = [-1 if city not in cycle else city for city in parent1.route]
        child2 = [-1 if city not in cycle else city for city in parent2.route]

        # Ensure that each child is a valid route
        child1 = self.fix_invalid_route(child1)
        child2 = self.fix_invalid_route(child2)

        return child1, child2

    def fix_invalid_route(self, route):
        # Ensure that each city appears exactly once in the route
        missing_cities = set(range(1, len(route) + 1)) - set(route)
        for city in missing_cities:
            if -1 in route:
                index = route.index(-1)
                route[index] = city
        return route

# Euclid formula - calculates distance between two cities. 
def calculated_distance_cities(city1, city2):
    x1, y1 = city1
    x2, y2 = city2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def initialize_population(pop_total_size, city_ids):
    return Population(pop_total_size, city_ids)


def calculate_fitness(individual, city_coordinates):
    total_traveled_distance = 0.0
    #calculates the total distance traveled for route/path
    for i in range(len(individual.route) - 1):
        city1 = city_coordinates[individual.route[i]]
        city2 = city_coordinates[individual.route[i + 1]]
        total_traveled_distance += calculated_distance_cities(city1, city2)
    # Add the distance from the last city to the first city to complete the cycle
    total_traveled_distance += calculated_distance_cities(city_coordinates[individual.route[-1]], city_coordinates[individual.route[0]])
    individual.fitness = total_traveled_distance
    return total_traveled_distance
    # Path/tour distance traveled. 

    # Perform roulette wheel selection to choose an individual from the population
def roulette_wheel_selection(population):
    total_fitness = sum(1 / ind.fitness for ind in population.individuals)
    random_selection= random.uniform(0, total_fitness)
    accumaleted_fitness = 0
    for ind in population.individuals:
        if ind.fitness is not None:
            accumaleted_fitness += 1 / ind.fitness
            if accumaleted_fitness>= random_selection:
                return ind
    return None


def check_termination_criteria(population, generation, max_generations, fitness_threshold):
    # To check if the maximum number of generations has been reached
    if generation >= max_generations:
        return True
    # Filtering out individuals with invalid fitness values
    valid_individuals = [ind for ind in population.individuals if ind.fitness is not None]

    if not valid_individuals:
        return True

    # Checking if the best fitness meets a certain threshold
    best_fitness = min(population.individuals, key=lambda x: x.fitness).fitness
    if best_fitness <= fitness_threshold:
        return True

    return False



max_generations = 1000 # Desired maximum number of generations
fitness_threshold = 1000.0  # Desired fitness threshold

# Initialize variables to store data
city_data = {}
dimension = 0 # number of cities
read_coordinates = False  # Flag to indicate when to start reading coordinates

# Open the file for reading
file_path = 'Random222.tsp'  # Replace with the actual file path
with open(file_path, 'r') as file:
    for line in file:
        parts = line.strip().split()

        # Check for specific keywords to extract file data
        if parts[0] == "DIMENSION:":
            dimension = int(parts[1])
        elif parts[0] == "NODE_COORD_SECTION":
            read_coordinates = True
        elif read_coordinates and len(parts) == 3:
            city_id = int(parts[0])
            x_coordinate = float(parts[1])
            y_coordinate = float(parts[2])
            city_data[city_id] = (x_coordinate, y_coordinate)

city_ids = list(range(1, dimension + 1))


class TSPGUI:
    def __init__(self, root, city_data, crossover_method, mutation_method):
        self.root = root
        self.city_data = city_data
        self.best_solution = None  # Stores best solution
        self.city_labels = {}  # Initialize the city_labels dictionary
        self.scale_factor = 4  # Scaling factor
        self.crossover_method = crossover_method
        self.mutation_method = mutation_method

        self.canvas = tk.Canvas(root, width=600, height=600)  # Increase the width and height
        self.canvas.pack() # Canvas

        self.start_button = tk.Button(root, text="Click to start WOC GA run as well as GA after the displayed next graph", command=self.genetic_algorithm)
        self.start_button.pack()

        self.best_solution_label = tk.Label(root, text="Distance: ")
        self.best_solution_label.pack()

        self.method_label = tk.Label(root, text=f"GA Crossover: {crossover_method} and  Mutation: {mutation_method}")
        self.method_label.pack()

    def drawing_route(self, route):
        # Clear the canvas
        self.canvas.delete("all")

        for i in range(len(route) - 1):
            city1 = self.city_data[route[i]]
            city2 = self.city_data[route[i + 1]]
            x1, y1 = city1
            x2, y2 = city2
            x1_scaled, y1_scaled = x1 * self.scale_factor, y1 * self.scale_factor
            x2_scaled, y2_scaled = x2 * self.scale_factor, y2 * self.scale_factor
            self.canvas.create_line(x1_scaled, y1_scaled, x2_scaled, y2_scaled, fill="blue", width=1)
        # Draw a line connecting the last city to the first to complete the cycle
        city1 = self.city_data[route[-1]]
        city2 = self.city_data[route[0]]
        x1, y1 = city1
        x2, y2 = city2
        x1_scaled, y1_scaled = x1 * self.scale_factor, y1 * self.scale_factor
        x2_scaled, y2_scaled = x2 * self.scale_factor, y2 * self.scale_factor
        self.canvas.create_line(x1_scaled, y1_scaled, x2_scaled, y2_scaled, fill="green", width=5)
        # Labels
        for city_id, coordinates in self.city_data.items():
            x, y = coordinates
            x_scaled, y_scaled = x * self.scale_factor, y * self.scale_factor
            label = self.city_labels.get(city_id)
            if label:
                self.canvas.delete(label)  # Remove previous label
            label = self.canvas.create_text(x_scaled, y_scaled, text=str(city_id), font=("Arial", 12, "bold"), fill="black")
            self.city_labels[city_id] = label

    def update_gui(self):
        #Updating GUI with best solution's route and fitness
        if self.best_solution:
            self.drawing_route(self.best_solution.route)
            self.best_solution_label.config(text=f"Best Solution GA tour: {self.best_solution.fitness:.2f}")

    def genetic_algorithm(self):
        top_expert_solutions = []
        combined_costs = []

        average_costs = []
        min_costs = []
        max_costs = []
        #this will keep track of my complete TSP solutions to make comparison later on to GA

        start_time = time.time()
        
        crossover_methods = ["Cycle", "Uniform"]
        mutation_methods = ["Swap", "Scramble"]

        for crossover_method in crossover_methods:
            for mutation_method in mutation_methods:
            # Set the current crossover and mutation methods
                current_crossover_method = crossover_method
                current_mutation_method = mutation_method
    
                for _ in range(100):  # Number of runs
                    global max_generations, fitness_threshold, pop_size, mutation_rate

                    # Initialize the population
                    population = initialize_population(pop_size, city_ids)

                    for generation in range(max_generations):
                        # Calculate fitness for each individual
                        for individual in population.individuals:
                            calculate_fitness(individual, city_data)
            
                        # Select parents using roulette wheel selection
                        parents = [roulette_wheel_selection(population) for _ in range(pop_size)]

                        new_population = Population(pop_size, city_ids)
                        for i in range(0, pop_size, 2):
                            child1, child2 = population.uniform_crossover(parents[i], parents[i + 1])
                            new_population.individuals[i] = Individual(child1)
                            new_population.individuals[i + 1] = Individual(child2)

                        # Apply mutation to the new population
                        for individual in new_population.individuals:
                            if random.random() < mutation_rate:
                                individual.swap_mutation()
                            if random.random() < mutation_rate:
                                individual.scramble_mutation()

                        population = new_population

                        if check_termination_criteria(population, generation, max_generations, fitness_threshold):
                            break

                    # Calculate fitness for all individuals in the final total population
                    for individual in population.individuals:
                        calculate_fitness(individual, city_data)
                
                    valid_individuals = []
                    #valid_individuals = [ind for ind in population.individuals if ind.fitness is not None]

                    for individual in population.individuals:
                        calculate_fitness(individual, city_data)
                        if individual.fitness is not None:
                            valid_individuals.append(individual)


                    print("Expert Fitness Values:")
                    for expert in valid_individuals:
                        print(f"Expert fitness: {expert.fitness}")
        

                    if valid_individuals:
                        best_solution = min(valid_individuals, key=lambda x: x.fitness)
                        self.best_solution = best_solution
                        self.update_gui()  # Update the GUI with the best solution

                        experts = sorted(valid_individuals, key=lambda x: x.fitness)
                        num_experts = int(len(experts) * 0.10)
                        top_expert_routes = [expert.route for expert in experts[:num_experts]]


            
                        top_expert_solutions.extend(top_expert_routes)
                

                        print("Top 10% Expert Solutions:")

            
                        for i, route in enumerate(top_expert_routes):
                            individual = Individual(city_data.keys())
                            individual.route = route
                            calculate_fitness(individual, self.city_data)
                            print(f"Expert {i + 1} route: {route} Cost: {individual.fitness:.2f}")
                        #keeps track of the top ten percent of routes and their cost
                        #Append the top expert routes to the list
                        top_expert_solutions.extend(top_expert_routes)

                        combined_expert_solution = self.combine_expert_solutions(top_expert_routes)
                        combined_route = combined_expert_solution.route
                        #prints combined expert solution from top ten percent. 
                        print("Combined Expert Solution:")
                        print(f"Route: {combined_route}")
                        print(f"Cost of Combined Solution: {combined_expert_solution.fitness:.2f}")
                        print(f"Combination: {current_crossover_method} + {current_mutation_method}")
            
                        #combined_route = self.apply_greedy_algorithm(combined_route, self.city_data)
                        combined_route = self.complete_tsp_solution(combined_route)
                        combined_solution = Individual(city_data.keys())
                        combined_solution.route = combined_route
                        calculate_fitness(combined_solution, self.city_data)
                        #completes that Combined Expert Solution and ensures TSP solution
                        print("Complete TSP Solution:")
                        print(f"Route: {combined_route}")
                        print(f"Cost of Complete TSP Solution: {combined_solution.fitness:.2f}")

                        combined_costs.append(combined_solution.fitness)
                    else:
                        print("No valid solutions found!")

                    end_time = time.time()

            # Calculate execution time
                    execution_time = end_time - start_time
                    print(f"Execution time: {execution_time:.2f} seconds")

        average_costs.append(np.mean(combined_costs))
        min_costs.append(np.min(combined_costs))
        max_costs.append(np.max(combined_costs))
        #100 runs of Complete TSP solution then outputs average
        print(f"Average Cost of Complete TSP Solutions: {np.mean(average_costs):.2f}")
        print(f"Min Cost of Complete TSP Solutions: {np.min(min_costs):.2f}")
        print(f"Max Cost of Complete TSP Solutions: {np.max(max_costs):.2f}")
        
    def complete_tsp_solution(self, combined_route):
        visited_cities = set()
        new_route = []

        for city in combined_route:
            if city not in visited_cities:
                new_route.append(city)
                visited_cities.add(city)
            else:
                unvisited_city = None
                for i in range(1, len(combined_route) + 1):
                    if i not in visited_cities:
                        unvisited_city = i
                        break

                if unvisited_city is not None:
                    new_route.append(unvisited_city)
                    visited_cities.add(unvisited_city)

        if new_route[0] != new_route[-1]:
            new_route.append(new_route[0])

        return new_route

    def combine_expert_solutions(self, expert_routes):
        # Sort the experts based on fitness

        experts = []
        for route in expert_routes:
            individual = Individual(city_data.keys())
            individual.route = route
            calculate_fitness(individual, self.city_data)
            experts.append(individual)

        sorted_experts = sorted(experts, key=lambda x: x.fitness)

        # Calculate the number of experts to select (100% of the population)
        num_experts = int(len(sorted_experts) * 1.00)


        # Extract the routes of the top experts
        top_expert_routes = [expert.route for expert in sorted_experts[:num_experts]]

        # Combine the routes 
        combined_route = self.combine_routes(top_expert_routes)
        

        # Create an Individual object with the combined route
        combined_individual = Individual(city_data.keys())
        combined_individual.route = combined_route
        calculate_fitness(combined_individual, self.city_data)

        return combined_individual

    
    def combine_routes(self, routes):
       
        combined_route = []

        for i in range(len(routes[0])):
            total_position = sum(route[i] for route in routes)
            combined_position = total_position / len(routes)
            combined_route.append(int(combined_position))

        return combined_route
    
    def apply_greedy_algorithm(self, route, city_coordinates):
    # Start from the first city
        current_city = route[0]
        unvisited_cities = set(route[1:])  # Exclude the starting node

        new_route = [current_city]

        while unvisited_cities:
            nearest_city = min(unvisited_cities, key=lambda city: calculated_distance_cities(city_coordinates[current_city], city_coordinates[city]))
            new_route.append(nearest_city)
            unvisited_cities.remove(nearest_city)
            current_city = nearest_city

    # Adds the starting node to complete the TSP route
        new_route.append(new_route[0])

        return new_route

def main():

    root = tk.Tk()
    root.title("TSP GA")
    gui = TSPGUI(root, city_data, "Uniform", "Swap")
    root.mainloop()


if __name__ == "__main__":
    main()

# Crossover and mutation methods to be tested
crossover_methods = ["Cycle", "Uniform"]
mutation_methods = ["Swap", "Scramble"]

fitness_dict = {}

for crossover_method in crossover_methods:
    for mutation_method in mutation_methods:
        if crossover_method == "Uniform" and mutation_method == "Swap":
            pop_size = 100
            mutation_rate = 0.2
        elif crossover_method == "Cycle" and mutation_method == "Scramble":
            pop_size = 100
            mutation_rate = 0.2
        else:
            pop_size = 100
            mutation_rate = 0.2

        results = []
        start_time = time.time() 
        # Run the GA loop
        for _ in range(100):  # number of run times
            population = initialize_population(pop_size, city_ids)

            for generation in range(max_generations):
                for individual in population.individuals:
                    calculate_fitness(individual, city_data)

                parents = [roulette_wheel_selection(population) for _ in range(pop_size)]

                new_population = Population(pop_size, city_ids)
                for i in range(0, pop_size, 2):
                    child1, child2 = population.uniform_crossover(parents[i], parents[i + 1])
                    new_population.individuals[i] = Individual(child1)
                    new_population.individuals[i + 1] = Individual(child2)

                for individual in new_population.individuals:
                    if random.random() < mutation_rate:
                        individual.swap_mutation()
                    if random.random() < mutation_rate:
                        individual.scramble_mutation()

                population = new_population

                if check_termination_criteria(population, generation, max_generations, fitness_threshold):
                    break

            for individual in population.individuals:
                calculate_fitness(individual, city_data)

            valid_individuals = [ind for ind in population.individuals if ind.fitness is not None]

            expert_cost_data = {}


            if valid_individuals:
                best_solution = min(valid_individuals, key=lambda x: x.fitness)
                results.append(best_solution.fitness)
                print(f"Results for Crossover: {crossover_method}, Mutation is: {mutation_method}")
                print(f"Best solution found is: {best_solution.route}")
                print(f"Total distance traveled in tour: {best_solution.fitness}")

                expert_cost_data[(crossover_method, mutation_method)] = [ind.fitness for ind in valid_individuals]
            
            else:
                print("No valid solutions found!")


        fitness_dict[(crossover_method, mutation_method)] = results
        print(f"Results for Crossover: {crossover_method}, Mutation is: {mutation_method}")

        #calculations for my WOC 100 runs. 
        if results:
            mean_fitness = sum(results) / len(results)
            min_fitness = min(results)
            max_fitness = max(results)
            std_deviation = math.sqrt(sum((x - mean_fitness) ** 2 for x in results) / len(results))

            print(f"Mean fitness for 100 runs: {mean_fitness:.2f}")
            print(f"Minimum fitness for 100 runs: {min_fitness:.2f}")
            print(f"Maximum fitness for 100 runs: {max_fitness:.2f}")
            print(f"Standard deviation for 100 runs: {std_deviation:.2f}")
        else:
            print("No valid solutions found!")

        end_time = time.time()  # Records the end time
        execution_time = end_time - start_time
        print(f"Execution time for 100 runs: {execution_time:.2f} seconds")


# Display execution times for all combinations
results_dict = {}
execution_times = {} 

for combo, results in fitness_dict.items():
    crossover_method, mutation_method = combo
    if results:
        mean_fitness = sum(results) / len(results)
        min_fitness = min(results)
        max_fitness = max(results)
        std_deviation = math.sqrt(sum((x - mean_fitness) ** 2 for x in results) / len(results))
        #start_time = time.time()
        execution_time = 0
        execution_times[combo] = 0
        for _ in range(100):
            start_time = time.time()
            end_time = time.time()
            execution_time += end_time - start_time
            execution_times[combo] += execution_time  
      
        results_dict[combo] = {
            "mean_fitness": mean_fitness,
            "min_fitness": min_fitness,
            "max_fitness": max_fitness,
            "std_deviation": std_deviation,
            "execution_time": execution_time  # execution time
        }
       

# Display results for all combinations
for combo, results in results_dict.items():
    crossover_method, mutation_method = combo
    print(f"Results for Crossover: {crossover_method}, Mutation is: {mutation_method}")
    print(f"Mean fitness for 100 runs: {results['mean_fitness']:.2f}")
    print(f"Minimum fitness for 100 runs: {results['min_fitness']:.2f}")
    print(f"Maximum fitness for 100 runs: {results['max_fitness']:.2f}")
    print(f"Standard deviation for 100 runs: {results['std_deviation']:.2f}")
   


for combo, fitness_values in fitness_dict.items():
    crossover_method, mutation_method = combo
    generations = list(range(len(fitness_values)))
    
    #if (crossover_method == "Cycle" and mutation_method == "Swap") or (crossover_method == "Uniform" and mutation_method == "Scramble"):
    label = f"{crossover_method}, {mutation_method}"
        
    if fitness_values:
        plt.plot(generations, fitness_values, label=label)

plt.xlabel("Generation")
plt.ylabel("Cost")
plt.legend(loc="best")
plt.title("Improvement Curves for Four Selected GA combinations")
plt.show()

generation = list(range(1, 11))  # Use data for 10 generations
cost = [
    499.50, 519.49, 551.66, 551.66, 551.66, 559.88, 559.88, 561.31, 565.63, 573.45
]  # Replace with any cost values

plt.plot(generation, cost, marker='o', linestyle='-')
plt.title('Top Expert Routes By Rank')
plt.xlabel('Top ten expert index')
plt.ylabel('Cost')
plt.grid(True)
plt.show()


                        population = new_population

                        if check_termination_criteria(population, generation, max_generations, fitness_threshold):
                            break

        # Calculate fitness for all individuals in the final total population
                    for individual in population.individuals:
                        calculate_fitness(individual, city_data)
                
                    valid_individuals = []
            #valid_individuals = [ind for ind in population.individuals if ind.fitness is not None]

                    for individual in population.individuals:
                        calculate_fitness(individual, city_data)
                        if individual.fitness is not None:
                            valid_individuals.append(individual)

            



                    print("Expert Fitness Values:")
                    for expert in valid_individuals:
                        print(f"Expert fitness: {expert.fitness}")
        

                    if valid_individuals:
                        best_solution = min(valid_individuals, key=lambda x: x.fitness)
                        self.best_solution = best_solution
                        self.update_gui()  # Update the GUI with the best solution

                        experts = sorted(valid_individuals, key=lambda x: x.fitness)
                        num_experts = int(len(experts) * 0.10)
                        top_expert_routes = [expert.route for expert in experts[:num_experts]]


            # Append the top expert routes to the list
                        top_expert_solutions.extend(top_expert_routes)
                

                        print("Top 10% Expert Solutions:")

            
                        for i, route in enumerate(top_expert_routes):
                            individual = Individual(city_data.keys())
                            individual.route = route
                            calculate_fitness(individual, self.city_data)
                            print(f"Expert {i + 1} route: {route} Cost: {individual.fitness:.2f}")

            # Append the top expert routes to the list
                        top_expert_solutions.extend(top_expert_routes)

                        combined_expert_solution = self.combine_expert_solutions(top_expert_routes)
                        combined_route = combined_expert_solution.route

                        print("Combined Expert Solution:")
                        print(f"Route: {combined_route}")
                        print(f"Cost of Combined Solution: {combined_expert_solution.fitness:.2f}")
                        print(f"Combination: {current_crossover_method} + {current_mutation_method}")
            
                #combined_route = self.apply_greedy_algorithm(combined_route, self.city_data)
                        combined_route = self.complete_tsp_solution(combined_route)
                        combined_solution = Individual(city_data.keys())
                        combined_solution.route = combined_route
                        calculate_fitness(combined_solution, self.city_data)

                        print("Complete TSP Solution:")
                        print(f"Route: {combined_route}")
                        print(f"Cost of Complete TSP Solution: {combined_solution.fitness:.2f}")

                        combined_costs.append(combined_solution.fitness)
                    else:
                        print("No valid solutions found!")

                    end_time = time.time()

            # Calculate execution time
                    execution_time = end_time - start_time
                    print(f"Execution time: {execution_time:.2f} seconds")

        average_costs.append(np.mean(combined_costs))
        min_costs.append(np.min(combined_costs))
        max_costs.append(np.max(combined_costs))

        print(f"Average Cost of Complete TSP Solutions: {np.mean(average_costs):.2f}")
        print(f"Min Cost of Complete TSP Solutions: {np.min(min_costs):.2f}")
        print(f"Max Cost of Complete TSP Solutions: {np.max(max_costs):.2f}")
        
    def complete_tsp_solution(self, combined_route):
        visited_cities = set()
        new_route = []

        for city in combined_route:
            if city not in visited_cities:
                new_route.append(city)
                visited_cities.add(city)
            else:
                unvisited_city = None
                for i in range(1, len(combined_route) + 1):
                    if i not in visited_cities:
                        unvisited_city = i
                        break

                if unvisited_city is not None:
                    new_route.append(unvisited_city)
                    visited_cities.add(unvisited_city)

        if new_route[0] != new_route[-1]:
            new_route.append(new_route[0])

        return new_route

    def combine_expert_solutions(self, expert_routes):
        # Sort the experts based on fitness

        experts = []
        for route in expert_routes:
            individual = Individual(city_data.keys())
            individual.route = route
            calculate_fitness(individual, self.city_data)
            experts.append(individual)

        sorted_experts = sorted(experts, key=lambda x: x.fitness)

        # Calculate the number of experts to select (100% of the population)
        num_experts = int(len(sorted_experts) * 1.00)


        # Extract the routes of the top experts
        top_expert_routes = [expert.route for expert in sorted_experts[:num_experts]]

        # Combine the routes 
        combined_route = self.combine_routes(top_expert_routes)
        

        # Create an Individual object with the combined route
        combined_individual = Individual(city_data.keys())
        combined_individual.route = combined_route
        calculate_fitness(combined_individual, self.city_data)

        return combined_individual

    
    def combine_routes(self, routes):
       
        combined_route = []

        for i in range(len(routes[0])):
            total_position = sum(route[i] for route in routes)
            combined_position = total_position / len(routes)
            combined_route.append(int(combined_position))

        return combined_route
    
    def apply_greedy_algorithm(self, route, city_coordinates):
    # Start from the first city (starting node)
        current_city = route[0]
        unvisited_cities = set(route[1:])  # Exclude the starting node

        new_route = [current_city]

        while unvisited_cities:
            nearest_city = min(unvisited_cities, key=lambda city: calculated_distance_cities(city_coordinates[current_city], city_coordinates[city]))
            new_route.append(nearest_city)
            unvisited_cities.remove(nearest_city)
            current_city = nearest_city

    # Adds the starting node to complete the TSP route
        new_route.append(new_route[0])

        return new_route

def main():

    root = tk.Tk()
    root.title("TSP GA")
    gui = TSPGUI(root, city_data, "Uniform", "Swap")
    root.mainloop()


if __name__ == "__main__":
    main()

# Crossover and mutation methods to be tested
crossover_methods = ["Cycle", "Uniform"]
mutation_methods = ["Swap", "Scramble"]

fitness_dict = {}

for crossover_method in crossover_methods:
    for mutation_method in mutation_methods:
        if crossover_method == "Uniform" and mutation_method == "Swap":
            pop_size = 100
            mutation_rate = 0.2
        elif crossover_method == "Cycle" and mutation_method == "Scramble":
            pop_size = 100
            mutation_rate = 0.2
        else:
            pop_size = 100
            mutation_rate = 0.2

        results = []
        start_time = time.time() 
        # Run the GA loop
        for _ in range(100):  # number of run times
            population = initialize_population(pop_size, city_ids)

            for generation in range(max_generations):
                for individual in population.individuals:
                    calculate_fitness(individual, city_data)

                parents = [roulette_wheel_selection(population) for _ in range(pop_size)]

                new_population = Population(pop_size, city_ids)
                for i in range(0, pop_size, 2):
                    child1, child2 = population.uniform_crossover(parents[i], parents[i + 1])
                    new_population.individuals[i] = Individual(child1)
                    new_population.individuals[i + 1] = Individual(child2)

                for individual in new_population.individuals:
                    if random.random() < mutation_rate:
                        individual.swap_mutation()
                    if random.random() < mutation_rate:
                        individual.scramble_mutation()

                population = new_population

                if check_termination_criteria(population, generation, max_generations, fitness_threshold):
                    break

            for individual in population.individuals:
                calculate_fitness(individual, city_data)

            valid_individuals = [ind for ind in population.individuals if ind.fitness is not None]

            expert_cost_data = {}


            if valid_individuals:
                best_solution = min(valid_individuals, key=lambda x: x.fitness)
                results.append(best_solution.fitness)
                print(f"Results for Crossover: {crossover_method}, Mutation is: {mutation_method}")
                print(f"Best solution found is: {best_solution.route}")
                print(f"Total distance traveled in tour: {best_solution.fitness}")

                expert_cost_data[(crossover_method, mutation_method)] = [ind.fitness for ind in valid_individuals]
            
            else:
                print("No valid solutions found!")


        fitness_dict[(crossover_method, mutation_method)] = results
        print(f"Results for Crossover: {crossover_method}, Mutation is: {mutation_method}")


        if results:
            mean_fitness = sum(results) / len(results)
            min_fitness = min(results)
            max_fitness = max(results)
            std_deviation = math.sqrt(sum((x - mean_fitness) ** 2 for x in results) / len(results))

            print(f"Mean fitness for 100 runs: {mean_fitness:.2f}")
            print(f"Minimum fitness for 100 runs: {min_fitness:.2f}")
            print(f"Maximum fitness for 100 runs: {max_fitness:.2f}")
            print(f"Standard deviation for 100 runs: {std_deviation:.2f}")
        else:
            print("No valid solutions found!")

        end_time = time.time()  # Records the end time
        execution_time = end_time - start_time
        print(f"Execution time for 100 runs: {execution_time:.2f} seconds")


# Display execution times for all combinations
results_dict = {}
execution_times = {} 

for combo, results in fitness_dict.items():
    crossover_method, mutation_method = combo
    if results:
        mean_fitness = sum(results) / len(results)
        min_fitness = min(results)
        max_fitness = max(results)
        std_deviation = math.sqrt(sum((x - mean_fitness) ** 2 for x in results) / len(results))
        #start_time = time.time()
        execution_time = 0
        execution_times[combo] = 0
        for _ in range(100):
            start_time = time.time()
            end_time = time.time()
            execution_time += end_time - start_time
            execution_times[combo] += execution_time  
      
        results_dict[combo] = {
            "mean_fitness": mean_fitness,
            "min_fitness": min_fitness,
            "max_fitness": max_fitness,
            "std_deviation": std_deviation,
            "execution_time": execution_time  # execution time
        }
       

# Display results for all combinations
for combo, results in results_dict.items():
    crossover_method, mutation_method = combo
    print(f"Results for Crossover: {crossover_method}, Mutation is: {mutation_method}")
    print(f"Mean fitness for 100 runs: {results['mean_fitness']:.2f}")
    print(f"Minimum fitness for 100 runs: {results['min_fitness']:.2f}")
    print(f"Maximum fitness for 100 runs: {results['max_fitness']:.2f}")
    print(f"Standard deviation for 100 runs: {results['std_deviation']:.2f}")
   


for combo, fitness_values in fitness_dict.items():
    crossover_method, mutation_method = combo
    generations = list(range(len(fitness_values)))
    
    #if (crossover_method == "Cycle" and mutation_method == "Swap") or (crossover_method == "Uniform" and mutation_method == "Scramble"):
    label = f"{crossover_method}, {mutation_method}"
        
    if fitness_values:
        plt.plot(generations, fitness_values, label=label)

plt.xlabel("Generation")
plt.ylabel("Cost")
plt.legend(loc="best")
plt.title("Improvement Curves for four selected GA combinations")
plt.show()

generation = list(range(1, 11))  # Use data for 10 generations
cost = [
    499.50, 519.49, 551.66, 551.66, 551.66, 559.88, 559.88, 561.31, 565.63, 573.45
]  # Replace with any cost values

plt.plot(generation, cost, marker='o', linestyle='-')
plt.title('Top Expert Routes by order')
plt.xlabel('Expert index')
plt.ylabel('Cost')
plt.grid(True)
plt.show()

