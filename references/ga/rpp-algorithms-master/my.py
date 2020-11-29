"""
    Implementation of the evolutionary approach for finding approximate solutions to the Rural Postman Problem
    proposed by Kang and Han in this paper:
    http://algorithms.khu.ac.kr/algo_lab/paper_pdf/mjkang/acm98-1.pdf

    Solutions are encoded as orderings of the required edges in a graph

    author: Zach Jones
    date: 4/29/17
"""

import random
from GraphUtils import *
from copy import deepcopy
import bisect
import collections
import time


verbose = False  # enable/disable verbose mode
# g = Graph(filename="test-graphs/dense1")
g = Graph(filename="C:/Projcet/ga/rpp-algorithms-master/test-graphs/Incheon_matrix",
          consider_zero_disconnected=True)
# with open(filename+".csv", 'rt') as file:
shortest_paths = {}
# find shortest paths from all vertices to all other vertices
for vertex in range(0, g.num_vertices):
    paths_for_vertex = djikstra(g, vertex)
    shortest_paths[vertex] = paths_for_vertex
    # for dst in range(g.num_vertices):
    # print("vertex = ", vertex, "dst = ", dst,
    #       "path : ", shortest_paths[vertex][dst])

    # configuration variables
generations = 5000  # how many generations to evolve
generation_counter = 0  # keeps track of the current generation count
alpha = 1  # describes how strong the difference between dominant and recessive chromosomes wider

population_size = 100
crossover_rate = 0.5   # how frequently to apply PMX crossover
mutation1_rate = 0.03  # how frequently to apply Reciprocal Exchange mutation
mutation2_rate = 0.03  # how frequently to apply Inversion mutation
mutation3_rate = 0.06  # how frequently to apply (i,j) = (j,i)
mutation4_rate = 0.1

########################## helpful routines ##########################

# evaluates the fitness of the given chromosome


def score_chromosome(chromosome):
    cost = 0
    for index in range(len(chromosome) - 1):
        this_edge = chromosome[index]
        next_edge = chromosome[index+1]

        cost += g.get_weight(this_edge[0], this_edge[1])
        # shortest path from the end of this edge to the beginning of the next edge
        path = shortest_paths[this_edge[1]][next_edge[0]]
        cost += path.cost

        # print('--index : ', index)
        # print('chromosome : ', chromosome)
        # print('this_edge : ', this_edge)
        # print('next_edge : ', next_edge)
        # print('edge_weight : ', g.get_weight(this_edge[0], this_edge[1]))
        # print('path : ', shortest_paths[this_edge[1]][next_edge[0]])
        # print('path.cost : ', path.cost)
        # print('tot cost : ', cost)
        # print('--------------------------------------------------------')

    # the chromosome with highest fitness minimizes cost
    return 1/(cost ** alpha)


def best_score_chromosome(chromosome):
    cost = 0
    for index in range(len(chromosome) - 1):
        this_edge = chromosome[index]
        next_edge = chromosome[index+1]

        cost += g.get_weight(this_edge[0], this_edge[1])
        # shortest path from the end of this edge to the beginning of the next edge
        path = shortest_paths[this_edge[1]][next_edge[0]]
        cost += path.cost

        print('--index : ', index)
        print('chromosome : ', chromosome)
        print('this_edge : ', this_edge)
        print('next_edge : ', next_edge)
        print('edge_weight : ', g.get_weight(this_edge[0], this_edge[1]))
        print(f'path {this_edge[1]} to {next_edge[0]} : ',
              shortest_paths[this_edge[1]][next_edge[0]])
        print('path.cost : ', path.cost)
        print('tot cost : ', cost)
        print('--------------------------------------------------------')

    # the chromosome with highest fitness minimizes cost
    return 1/(cost ** alpha)

# pmx crossover


def pmx(parentA, parentB):
    assert len(parentA) == len(parentB)
    positions = random.sample(range(len(parentA)), 2)
    crossover_point1 = min(positions[0], positions[1])
    crossover_point2 = max(positions[0], positions[1])
    childA = deepcopy(parentA)
    childB = deepcopy(parentB)

    for idx in range(crossover_point1, crossover_point2):
        gene_a = childA[idx]
        gene_b = childB[idx]

        # make the swap for parent a
        try:
            gene_b_index = childA.index(gene_b)
        except ValueError:
            gene_b = gene_b[::-1]
            gene_b_index = childA.index(gene_b)

        childA[idx] = gene_b
        childA[gene_b_index] = gene_a

        # make the swap for parent b
        try:
            gene_a_index = childB.index(gene_a)
        except ValueError:
            gene_a = gene_a[::-1]
            gene_a_index = childB.index(gene_a)
        childB[idx] = gene_a
        childB[gene_a_index] = gene_b

    return childA, childB

# mutation 1 - modifies chromosome in place by exchanging two locations in the chromosome


def reciprocal_exchange(chromosome):
    # get two distinct positions:
    positions = random.sample(range(len(chromosome)), 2)
    # swap the elements at those positions
    chromosome[positions[0]], chromosome[positions[1]
                                         ] = chromosome[positions[1]], chromosome[positions[0]]
    return chromosome

# mutation 2 - modifies chromosome in place by inverting a subsequence of the chromosome


def inversion(chromosome):
    positions = random.sample(range(len(chromosome)), 2)
    inversion_point1 = min(positions[0], positions[1])
    inversion_point2 = max(positions[0], positions[1])
    chromosome[inversion_point1:inversion_point2] = chromosome[inversion_point1:inversion_point2][::-1]


def direction(chromosome):
    positions = random.sample(range(len(chromosome)), 5)
    for i in range(len(positions)):
        pos = positions[i]
        tmp_list = list(chromosome[pos])
        tmp_list = tmp_list[::-1]
        chromosome[pos] = tuple(tmp_list)


def reduction(chromosome):
    for index in range(len(chromosome) - 1):
        this_edge = chromosome[index]
        next_edge = chromosome[index+1]
        # print(chromosome)
        # print(this_edge)
        # print(next_edge)

        path = shortest_paths[this_edge[1]][next_edge[0]]
        # print(path)
        for i in range(len(path.vertices) - 1):
            tmp_edge = (path.vertices[i], path.vertices[i+1])
            for j in range(index, len(chromosome)):
                if tmp_edge == chromosome[j]:
                    # print(f'From {chromosome}')
                    # print(f'path:\t {path}')
                    chromosome.insert(index+1, tmp_edge)
                    del chromosome[j+1]
                    # print(f'To {chromosome}\n')
                    continue


def cdf(weights):
    total = sum(weights)
    result = []
    cumsum = 0
    for w in weights:
        cumsum += w
        result.append(cumsum / total)
    return result

# randomly chooses from the population given a list of weights for each member


def choice(population, weights):
    assert len(population) == len(weights)
    cdf_vals = cdf(weights)
    x = random.random()
    idx = bisect.bisect(cdf_vals, x)
    return population[idx]


########################## initialize and run GA ##########################
required_edges = g.get_required()
if verbose:
    print(required_edges)
solution_pool = []
start_time = time.time()
for i in range(0, population_size):
    # It's remotely possible, but EXTREMELY unlikely, that we would pick two identical orderings
    starting_solution = random.sample(required_edges, len(required_edges))
    solution_pool.append(starting_solution)

while generation_counter < generations:
    if generation_counter % 100 == 0:
        print("Iteration %s" % generation_counter)

    # crossover
    crossover_parent_count = int(crossover_rate * population_size)
    if crossover_parent_count % 2 == 1:
        crossover_parent_count -= 1  # ensure even number of parents

    # randomly select which parents will "breed"
    crossover_parents = random.sample(solution_pool, crossover_parent_count)
    idx = 0
    # iterate over pairs of parents and get children
    while idx < len(crossover_parents):
        parent_a = crossover_parents[idx]
        parent_b = crossover_parents[idx+1]
        child_a, child_b = pmx(parent_a, parent_b)
        solution_pool.extend([child_a, child_b])
        idx += 2

    # mutation
    for chromosome in solution_pool:
        if random.random() < mutation1_rate:
            reciprocal_exchange(chromosome)
        if random.random() < mutation2_rate:
            inversion(chromosome)
        if random.random() < mutation3_rate:
            direction(chromosome)
        if random.random() < mutation4_rate:
            reduction(chromosome)

    # selection of new generation
    fitness_sum = 0
    for chromosome in solution_pool:
        fitness_sum += score_chromosome(chromosome)

    weights = []
    for chromosome in solution_pool:
        weights.append(score_chromosome(chromosome)/fitness_sum)

    new_generation = []
    for idx in range(0, population_size):
        new_generation.append(choice(solution_pool, weights))

    solution_pool = new_generation

    generation_counter += 1

# finished computing generations - find the solution with lowest cost and report the result
best_chromosome = None
best_chromosome_score = -10000000
for chromosome in solution_pool:
    score = score_chromosome(chromosome)
    if score > best_chromosome_score:
        best_chromosome = chromosome
        best_chromosome_score = score

time_elapsed = time.time() - start_time
print("Terminated.  Found tour with cost: %s" % (1/best_chromosome_score))
print(best_chromosome)
my = best_score_chromosome(best_chromosome)
print("Time elapsed: %s ms" % (time_elapsed*1000))
