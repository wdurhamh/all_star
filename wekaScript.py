import subprocess
from organism import Organism
import random as rand


TRAIN_SPLIT = 75
MAX_GENERATIONS = 20
MAX_EPOCHS = 1000000
VALIDATION_PERCENT = 15
POPULATION_SIZE = 10
MAX_HIDDEN_LAYERS = 3
MAX_HIDDEN_NODES = 15
BSSF = Organism(0,0,0)
BSSF.set_score(0)

def initialize_pop():
    population = []
    for i in range(POPULATION_SIZE):
        rate = rand.random()
        momentum = rand.random()
        hidden_layers = rand.randint(1,MAX_HIDDEN_LAYERS)
        struct = ""
        first = True
        for j in range(hidden_layers):
            if not first:
                struct +=","
            first = False
            struct += str(rand.randint(1,MAX_HIDDEN_NODES))
        org = Organism(rate, momentum, struct)
        population.append(org)
    return population

def update_BSSF(org):
    global BSSF
    BSSF = Organism(org.rate, org.momentum, org.structure)
    BSSF.set_score(org.score)
    print org.rate, org.momentum, org.structure, org.score

def evaluate_fitness(org):
    rate = org.rate
    momentum = org.momentum
    structure = org.structure

    command_format = "java -classpath ~/Documents/weka.jar weka.classifiers.functions.MultilayerPerceptron  -t allstar.arff -split-percentage %d -L %f -M %f -N %d -V %d -H %s -o -S %d"
    call = command_format % (TRAIN_SPLIT, rate, momentum, MAX_EPOCHS, 
                             VALIDATION_PERCENT, structure, 
                             rand.randint(0,10000))
    score = 0
    for i in range(10):
        p = subprocess.Popen(call, shell=True, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out,err = p.communicate()
        if err:
            print err
        values = [line for line in out.split("\n") if 'Correctly Classified Instances' in line][1].split(" ")
        if values[len(values)- 2]:
            score += float(values[len(values) - 2])
    score = score/10
    org.set_score(score)
    #print BSSF.score
    if score > BSSF.score:
        update_BSSF(org)

def reproduce(parents):
    children = []
    #divide the parents into gorups of two
    #for each couple, generate two children
    for i in range(len(parents)/2):
        p1 = parents[i]
        i += 1
        p2 = parents[i]
        s1, s2 = get_structs(p1, p2)
        n1, n2, n3, n4 = add_noise(p1, p2)
        child1 = Organism(n1, n2, s1)
        child2 = Organism(n3, n4, s2)
        children.append(child1)
        children.append(child2)
    return children

def get_structs(p1, p2):
    p1_values = p1.structure.split(",")
    p2_values = p2.structure.split(",")
    p1_l = len(p1_values)
    p2_l = len(p2_values)
    s1 = ",".join(p1_values[:(p1_l/2)]) + "," + ",".join(p2_values[p2_l/2:])
    s2 = ",".join(p2_values[:(p2_l/2)]) + "," + ",".join(p1_values[p1_l/2:])
    return s1, s2

def add_noise(p1, p2):
    n1 = p1.rate + rand.gauss(.05,.05)
    if n1 >=1: n1 = .999
    n2 = p2.momentum + rand.gauss(.05,.05)
    if n2 >=1: n2 = .999
    n3 = p2.rate + rand.gauss(.05,.05)
    if n3 >=1: n3 = .999
    n4 = p1.momentum + rand.gauss(.05,.05)
    if n4 >=1: n4 = .999
    return n1, n2, n3, n4 

def get_next_gen(population):
    #get the top half of the list
    population.sort(key=lambda org: org.score, reverse = True)
    parents = population[:(POPULATION_SIZE/2)]
    offspring = reproduce(parents)
    return parents + offspring

def main():
    population = initialize_pop()
    for gen in range(MAX_GENERATIONS):
        print "Generation", gen 
        for org in population:
            evaluate_fitness(org)
        population = get_next_gen(population)

main()
