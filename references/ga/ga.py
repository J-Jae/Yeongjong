import networkx as nx


# configuration variables
generations = 100  # how many generations to evolve
generation_counter = 0  # keeps track of the current generation count
alpha = 1  # describes how strong the difference between dominant and recessive chromosomes wider

population_size = 20
crossover_rate = 0.6   # how frequently to apply PMX crossover
mutation1_rate = 0.03  # how frequently to apply Reciprocal Exchange mutation
mutation2_rate = 0.04  # how frequently to apply Inversion mutation


def run(networkx):
    g = networkx


def insertion(chromosome):
    positions = random.sample(range(len(chromosome)), 5)
    for i in range(len(positions)):
        pos = positions[i]
        tmp_list = list(chromosome[pos])
        tmp_list = tmp_list[::-1]
        chromosome[pos] = tuple(tmp_list)
