"""
    Implementation of the evolutionary approach for finding approximate solutions to the Rural Postman Problem
    proposed by Kang and Han in this paper:
    http://algorithms.khu.ac.kr/algo_lab/paper_pdf/mjkang/acm98-1.pdf

    Solutions are encoded as orderings of the required edges in a graph

    author: Zach Jones
    date: 4/29/17
"""

import random
import bisect
import collections
import time
from copy import deepcopy
from GraphUtils import * 

class GenericAlgorithm:
    generation_counter = 0 # keeps track of the current generation count
    def __init__(self, path, generations=1000, alpha=1, population_size=100, crossover_rate=0.5, 
                mutation1_rate=0.03, mutation2_rate=0.03, mutation3_rate=0.06, mutation4_rate=0.1, debug=False):
       
        self.verbose = debug  # enable/disable verbose mode
        self.g = Graph(filename=path, consider_zero_disconnected=True)
        
        self.shortest_paths = {}
        for vertex in range(0, self.g.num_vertices):
            paths_for_vertex = djikstra(self.g, vertex)
            self.shortest_paths[vertex] = paths_for_vertex

        # configuration variables
        self.generations = generations  # how many generations to evolve
        self.alpha = alpha              # describes how strong the difference between dominant and recessive chromosomes wider
        self.population_size = population_size
        self.crossover_rate = crossover_rate   # how frequently to apply PMX crossover
        self.mutation1_rate = mutation1_rate  # how frequently to apply Reciprocal Exchange mutation
        self.mutation2_rate = mutation2_rate  # how frequently to apply Inversion mutation
        self.mutation3_rate = mutation3_rate  # how frequently to apply (i,j) = (j,i)
        self.mutation4_rate = mutation4_rate
        
    def run(self):
        required_edges = self.g.get_required()
        if self.verbose:
            print(required_edges)
        solution_pool = []
        start_time = time.time()
        for i in range(0, self.population_size):
            # It's remotely possible, but EXTREMELY unlikely, that we would pick two identical orderings
            starting_solution = random.sample(required_edges, len(required_edges))
            solution_pool.append(starting_solution)

        while self.generation_counter < self.generations:
            if self.generation_counter % 100 == 0:
                print("Iteration %s" % self.generation_counter)

            # crossover
            crossover_parent_count = int(self.crossover_rate * self.population_size)
            if crossover_parent_count % 2 == 1:
                crossover_parent_count -= 1  # ensure even number of parents

            # randomly select which parents will "breed"
            crossover_parents = random.sample(solution_pool, crossover_parent_count)
            idx = 0
            # iterate over pairs of parents and get children
            while idx < len(crossover_parents):
                parent_a = crossover_parents[idx]
                parent_b = crossover_parents[idx+1]
                child_a, child_b = self.pmx(parent_a, parent_b)
                solution_pool.extend([child_a, child_b])
                idx += 2

            # mutation
            for chromosome in solution_pool:
                if random.random() < self.mutation1_rate:
                    self.reciprocal_exchange(chromosome)
                if random.random() < self.mutation2_rate:
                    self.inversion(chromosome)
                if random.random() < self.mutation3_rate:
                    self.direction(chromosome)
                if random.random() < self.mutation4_rate:
                    self.reduction(chromosome)

            # selection of new generation
            fitness_sum = 0
            for chromosome in solution_pool:
                fitness_sum += self.score_chromosome(chromosome)

            weights = []
            for chromosome in solution_pool:
                weights.append(self.score_chromosome(chromosome)/fitness_sum)

            new_generation = []
            for idx in range(0, self.population_size):
                new_generation.append(self.choice(solution_pool, weights))

            solution_pool = new_generation

            self.generation_counter += 1

        # finished computing generations - find the solution with lowest cost and report the result
        best_chromosome = None
        best_chromosome_score = -10000000
        for chromosome in solution_pool:
            score = self.score_chromosome(chromosome)
            if score > best_chromosome_score:
                best_chromosome = chromosome
                best_chromosome_score = score

        time_elapsed = time.time() - start_time
        print("Terminated.  Found tour with cost: %s" % (1/best_chromosome_score))
        # print(f'chromosome type : {best_chromosome}')
        tmp = self.best_score_chromosome(best_chromosome)
        print("Time elapsed: %s ms" % (time_elapsed*1000))

        result = {
            'time' : time_elapsed*1000,
            'cost' : float(best_chromosome_score),
            'chromosome' : best_chromosome,
            'route' : self.get_route(best_chromosome)
        }
        return result

    def score_chromosome(self, chromosome):
        cost = 0
        for index in range(len(chromosome) - 1):
            this_edge = chromosome[index]
            next_edge = chromosome[index+1]

            cost += self.g.get_weight(this_edge[0], this_edge[1])
            # shortest path from the end of this edge to the beginning of the next edge
            path = self.shortest_paths[this_edge[1]][next_edge[0]]
            cost += path.cost

        return 1/(cost ** self.alpha)

    def best_score_chromosome(self, chromosome):
        cost = 0
        for index in range(len(chromosome) - 1):
            this_edge = chromosome[index]
            next_edge = chromosome[index+1]

            cost += self.g.get_weight(this_edge[0], this_edge[1])
            # shortest path from the end of this edge to the beginning of the next edge
            path = self.shortest_paths[this_edge[1]][next_edge[0]]
            cost += path.cost
            # print('--index : ', index)
            # print('chromosome : ', chromosome)
            # print('this_edge : ', this_edge)
            # print('next_edge : ', next_edge)
            # print('edge_weight : ', self.g.get_weight(this_edge[0], this_edge[1]))
            # print(f'path {this_edge[1]} to {next_edge[0]} : ',
            #     self.shortest_paths[this_edge[1]][next_edge[0]])
            # print('path.cost : ', path.cost)
            # print('tot cost : ', cost)
            # print('--------------------------------------------------------')

        # the chromosome with highest fitness minimizes cost
        return 1/(cost ** self.alpha)

    def get_route(self, chromosome):
        route = []
        for index in range(len(chromosome) - 1):
            this_edge = chromosome[index]
            next_edge = chromosome[index+1]
            
            path = self.shortest_paths[this_edge[1]][next_edge[0]]
            edges = path.get_edges()

            route.append(this_edge)
            
            for idx in range(len(edges)):
                route.append(edges[idx])
            # print(f'this_edge : {this_edge} , next_edge : {next_edge}')
        # print(f'route : {route}')
        return route
    # pmx crossover
    def pmx(self, parentA, parentB):
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
    def reciprocal_exchange(self, chromosome):
        # get two distinct positions:
        positions = random.sample(range(len(chromosome)), 2)
        # swap the elements at those positions
        chromosome[positions[0]], chromosome[positions[1]
                                            ] = chromosome[positions[1]], chromosome[positions[0]]
        return chromosome

    # mutation 2 - modifies chromosome in place by inverting a subsequence of the chromosome
    def inversion(self, chromosome):
        positions = random.sample(range(len(chromosome)), 2)
        inversion_point1 = min(positions[0], positions[1])
        inversion_point2 = max(positions[0], positions[1])
        chromosome[inversion_point1:inversion_point2] = chromosome[inversion_point1:inversion_point2][::-1]


    def direction(self, chromosome):
        positions = random.sample(range(len(chromosome)), 5)
        for i in range(len(positions)):
            pos = positions[i]
            tmp_list = list(chromosome[pos])
            tmp_list = tmp_list[::-1]
            chromosome[pos] = tuple(tmp_list)

    def reduction(self, chromosome):
        for index in range(len(chromosome) - 1):
            this_edge = chromosome[index]
            next_edge = chromosome[index+1]
            # print(chromosome)
            # print(this_edge)
            # print(next_edge)

            path = self.shortest_paths[this_edge[1]][next_edge[0]]
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


    def cdf(self, weights):
        total = sum(weights)
        result = []
        cumsum = 0
        for w in weights:
            cumsum += w
            result.append(cumsum / total)
        return result

    # randomly chooses from the population given a list of weights for each member
    def choice(self, population, weights):
        assert len(population) == len(weights)
        cdf_vals = self.cdf(weights)
        x = random.random()
        idx = bisect.bisect(cdf_vals, x)
        return population[idx]
