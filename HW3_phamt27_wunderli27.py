import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
import os
import random


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
## HW 4 variables
games_to_play = 5
games_left = games_to_play # games_left to determine fitness
gene_list = [] # list of genes
index = 0 #index
fitness_list = [] # list of fitnesses
population_size = 10 # inital population size
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "phamt27_population.txt")
games_won = 0

#genes
#1 player food amount
#2 player soldier amount
#3 player ranger amount
#4 player drone amount
#5 player worker amount
#6 hp of player queen
#7 how many more food player has than enemy
#8 enemy queen hp
#9 enemy worker amount
#10 enemy drone amount

#strange genes
#11 distance of closest ally worker to enemy queen
#12 distance between closest ally and enemy combatant


#HW 4 methods
def init_population():
    for i in range(population_size): # reset fitness values
        fitness_list.append(-1)
    index = 0 #reset index

    if os.path.exists(file_path):
        pass
    else:
        file = open(file_path, "w")
        for i in range(population_size):
            for i in range(12):
                val = random.random() * 20 - 10
                file.write(str(val))
                file.write("\n")
            file.write("\n")
        file.close()


def vertical_dance(list1, list2): # input two lists of floats, return two lists of floats
    list3 = []
    list4 = []
    slice1 = random.randint(0, 11)
    slice2 = random.randint(0, 11)
    for a in list1[:slice1]:
        list3.append(a)
    for b in list2[slice1:]:
        list3.append(b)
    for c in list2[:slice2]:
        list4.append(c)
    for d in list1[slice2:]:
        list4.append(d)
    for e in range(len(list3)):
        list3[e] *= (random.random() - 0.5) * .2
    for f in range(len(list4)):
        list4[f] *= (random.random() - 0.5) * .2
    ret = [list3, list4]
    return ret

def generate_new_generation():
    print("kill started")
    half = population_size / 2 #divide population by two, rounded down
    pop_to_erase = [] # array of population numbers to "kill" and replace with mates
    remain_pop = []
    mean = 0 # mean population, kill all below this unless exceeds half
    for i in fitness_list:
        mean += i
    mean /= len(fitness_list)
    for i in range(len(fitness_list)): # mark half below mean for death
        if fitness_list[i] < (mean + .01) and half > 0:
            pop_to_erase.append(i)
            half -= 1
    for i in range(len(fitness_list)):
        if i in pop_to_erase:
            pass
        else:
            remain_pop.append(i)
    file = open(file_path, "r+")
    print(pop_to_erase)
    print(remain_pop)
    for i in range(len(pop_to_erase)): #kill and replace  
        file.seek(0, 0)
        list1 = read_genes(remain_pop[ random.randint(0, len(remain_pop)-1) ])
        list2 = read_genes(remain_pop[ random.randint(0, len(remain_pop)-1) ])
        replacement = vertical_dance(list1, list2)[random.randint(0, 1)]
        #random of the two children
        lines = file.readlines()
        counter = 0
        gene_num = 0
        for j in range(len(lines)):
            if counter == pop_to_erase[i] and gene_num < 12:
                lines[j] = str(replacement[gene_num]) + "\n"
                gene_num = gene_num + 1
            if lines[j] == "\n": counter +=1
        file.seek(0, 0)
        for k in lines:
            file.write(k)
    file.close()
        


def read_genes(gene_index):
#increment to index
    global file_path
    the_list = []
    index_to_go = gene_index
    file = open(file_path, "r")
    while index_to_go > 0:
        if file.readline() == "\n":
            index_to_go = index_to_go - 1
    for i in range(12):
        the_list.append(str(file.readline()))
    file.close()
    for i in range(len(the_list)):
        the_list[i] = the_list[i][:-2]
        the_list[i] = float(the_list[i])
    return the_list

def gene_utility(state):
    total_utility = 0 #sum of utility
    total_utility += state.inventories[state.whoseTurn].foodCount * float(gene_list[0]) #gene 1 food count
    total_utility += len(getAntList(state, state.whoseTurn, (SOLDIER,))) * float(gene_list[1]) #gene 2 soldier amount
    total_utility += len(getAntList(state, state.whoseTurn, (R_SOLDIER,))) * float(gene_list[2]) #gene 3 ranger amount
    total_utility += len(getAntList(state, state.whoseTurn, (DRONE,))) * float(gene_list[3]) #gene 4 drone amount
    total_utility += len(getAntList(state, state.whoseTurn, (WORKER,))) * float(gene_list[4]) #gene 5 worker amount
    total_utility += getAntList(state, state.whoseTurn, (QUEEN,))[0].health * float(gene_list[5]) #gene 6 hp of queen
    total_utility += (state.inventories[state.whoseTurn].foodCount - state.inventories[1 - state.whoseTurn].foodCount) * float(gene_list[6]) #gene 7 food differential
    total_utility += getAntList(state, 1 - state.whoseTurn, (QUEEN,))[0].health * float(gene_list[7]) #gene 8 enemy queen hp
    total_utility += len(getAntList(state, 1 - state.whoseTurn, (WORKER,))) * float(gene_list[8]) #gene 9 enemy worker amount
    total_utility += len(getAntList(state, 1 - state.whoseTurn, (DRONE,))) * float(gene_list[9]) #gene 10 enemy drone amount
    if (len(getAntList(state, state.whoseTurn, (WORKER,))) > 0) and (len(getAntList(state, 1 - state.whoseTurn, (QUEEN,))) > 0):
        total_utility += stepsToReach(state, getAntList(state, state.whoseTurn, (WORKER,))[0].coords, getAntList(state, 1 - state.whoseTurn, (QUEEN,))[0].coords) * float(gene_list[10]) #gene 11 distance from worker to queen
        pass

    if (len(getAntList(state, state.whoseTurn, (SOLDIER,))) > 0) and (len(getAntList(state, 1 - state.whoseTurn, (SOLDIER,))) > 0):
        total_utility += stepsToReach(state, getAntList(state, state.whoseTurn, (SOLDIER,))[0].coords, getAntList(state, 1 - state.whoseTurn, (SOLDIER,))[0].coords) * float(gene_list[11]) #gene 12 closest ally and enemy
        pass
    return total_utility

def get_best_move(state, move_list):
    best_util = -999
    best_move = None
    for move in move_list:
        if gene_utility(getNextState(state, move)) > best_util:
            best_util = gene_utility(getNextState(state, move))
            best_move = move
    return best_move

#HW 3 methods here - Modified for Minimax with alpha-beta pruning
def expandNode(node, player_id):
    """Expand node with adversarial moves"""
    state = node["state"]
    move_list = listAllLegalMoves(state)
    node_list = []
    for move in move_list:
        new_node = createNode(move, state, node["depth"] + 1, node, player_id)
        node_list.append(new_node)
    return node_list
    
def createNode(move, state, depth, parent_node, player_id):
    """Create node using adversarial state transition"""
    new_state = getNextStateAdversarial(state, move)  # Changed from getNextState
    new_node = {
        "move": move,
        "state": new_state,
        "depth": depth,
        "parent": parent_node,
        "evaluation": utility(new_state, player_id),
        "player_id": player_id
    }
    return new_node

def get_enemy_id(player_id):
    """Get the enemy player ID - handles the case where IDs might not be 0 and 1"""
    if player_id == 0:
        return 1
    elif player_id == 1:
        return 0
    elif player_id == 2:
        return 1  # If we're player 2, enemy is player 1
    else:
        return 1 - player_id  # Fallback

def utility(state, player_id): 






    """Modified to take player_id for proper evaluation"""
    enemy_id = get_enemy_id(player_id)
    
    # Check for terminal states first
    my_queen = getAntList(state, player_id, (QUEEN,))
    enemy_queen = getAntList(state, enemy_id, (QUEEN,))
    
    if len(my_queen) == 0:
        return 999.0  # We lost (high is bad)
    if len(enemy_queen) == 0:
        return -999.0  # We won (low is good)
    if state.inventories[player_id].foodCount >= 11:
        return -999.0  # We won
    if state.inventories[enemy_id].foodCount >= 11:
        return 999.0  # We lost
    
    worker_part = worker_utility(state, player_id)
    soldier_part = soldier_utility(state, player_id)
    eval_score = 140.001-(worker_part+soldier_part)/1.01
    return eval_score

def soldier_utility(state, player_id):
    """Modified to use player_id instead of state.whoseTurn"""
    enemy_id = get_enemy_id(player_id)
    
    if (len(getAntList(state, player_id, (R_SOLDIER,))) > 0):
        soldier = getAntList(state, player_id, (R_SOLDIER,))[0]
    else:
        soldier = None
    if not (soldier == None):
        my_soldier_part = 10
        if (len(getAntList(state, enemy_id, (WORKER,))) < 1) or (len(getAntList(state, enemy_id, (QUEEN,))) < 1):
            my_soldier_part += 60.0
        else:
            my_soldier_part += max(0, 12-stepsToReach(state, soldier.coords, getAntList(state, enemy_id, (WORKER,))[0].coords)- 0.1 *stepsToReach(state, soldier.coords, getAntList(state, enemy_id, (QUEEN,))[0].coords))
        if (len(getAntList(state, enemy_id, (WORKER,))) < 1) and (len(getAntList(state, enemy_id, (QUEEN,))) == 1):
            my_soldier_part += max(0, 12-stepsToReach(state, soldier.coords, getAntList(state, enemy_id, (QUEEN,))[0].coords))
        if (len(getAntList(state, enemy_id, (QUEEN,))) == 1):
            my_soldier_part +=  (5-0.5*getAntList(state, enemy_id, (QUEEN,))[0].health)
            if (stepsToReach(state, soldier.coords, getAntList(state, enemy_id, (QUEEN,))[0].coords) < 3):
                my_soldier_part = 0
        else:
            my_soldier_part += 60
        for drone in getAntList(state, enemy_id, (DRONE,)):
            if stepsToReach(state, soldier.coords, drone.coords) < 2:
                return -1
    else:
        my_soldier_part = 0
    return my_soldier_part

def worker_utility(state, player_id):
    """Modified to use player_id instead of state.whoseTurn"""
    bad = 99
    worker_part = 0
    
    # Check if queen exists
    queen_list = getAntList(state, player_id, (QUEEN,))
    if len(queen_list) == 0:
        return 0  # Queen is dead, game over
    queen = queen_list[0]
    
    if (len(getAntList(state, player_id, (WORKER,))) > 0):
        worker = getAntList(state, player_id, (WORKER,))[0]
    else:
        worker = None
        worker_part = 0
    
    tunnel = getConstrList(state, player_id, (TUNNEL,))[0]
    food = getCurrPlayerFood(player_id, state)
    
    if worker is None and state.inventories[player_id].foodCount > 0:
        return bad
    elif worker is None:
        return bad
    else:
         if not (worker.carrying):
            return 1.0-0.1*stepsToReach(state, worker.coords, food[0].coords) + 4.5*state.inventories[player_id].foodCount
         if (worker.carrying):
            return 1.0-0.1*stepsToReach(state, worker.coords, tunnel.coords) + 1.5 + 4.5*state.inventories[player_id].foodCount
    
    anthill = getConstrList(state, player_id, (ANTHILL,))[0]
    if (queen.coords == anthill.coords):
        return bad
    return 0


def minimax_alpha_beta(node, depth, alpha, beta, player_id):
    """
    Minimax with alpha-beta pruning
    NOTE: In your original code, LOWER scores are BETTER (minimization)
    So our agent wants to MINIMIZE and opponent wants to MAXIMIZE
    """
    state = node["state"]
    
    # Base case: reached maximum depth
    if depth == 0:
        return (node["evaluation"], node)
    
    # Check if current state is for our player (minimize) or opponent (maximize)
    is_our_turn = (state.whoseTurn == player_id)
    
    # Get all child nodes
    all_moves = listAllLegalMoves(state)
    
    # SPEED OPTIMIZATION: Limit branching at deeper levels
    if depth == 1 and len(all_moves) > 8:
        # At depth 1, only explore top 8 moves
        scored = []
        for move in all_moves:
            next_state = getNextStateAdversarial(state, move)
            score = utility(next_state, player_id)
            scored.append((score, move))
        # Sort by score (first element of tuple)
        scored.sort(key=lambda x: x[0]) if is_our_turn else scored.sort(key=lambda x: x[0], reverse=True)
        all_moves = [move for score, move in scored[:8]]
    
    if is_our_turn:
        # Our turn - MINIMIZE (lower scores are better)
        min_eval = float('inf')
        best_node = None
        
        for move in all_moves:
            child = createNode(move, state, node["depth"] + 1, node, player_id)
            eval_score, _ = minimax_alpha_beta(child, depth - 1, alpha, beta, player_id)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_node = child
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cutoff (pruning)
        
        return (min_eval, best_node)
    else:
        # Opponent's turn - MAXIMIZE (they want high scores for us = bad for us)
        max_eval = float('-inf')
        best_node = None
        
        for move in all_moves:
            child = createNode(move, state, node["depth"] + 1, node, player_id)
            eval_score, _ = minimax_alpha_beta(child, depth - 1, alpha, beta, player_id)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_node = child
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff (pruning)
        
        return (max_eval, best_node)


class AIPlayer(Player):

    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "soldier_rush2")


    def getPlacement(self, currentState):
        numToPlace = 0
        if currentState.phase == SETUP_PHASE_1:
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    x = random.randint(0, 9)
                    y = random.randint(0, 3)
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    x = random.randint(0, 9)
                    y = random.randint(6, 9)
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]
    
    def getMove(self, currentState):
        # Get all legal moves from current state
        legal_moves = listAllLegalMoves(currentState)
        best_move = get_best_move(currentState, legal_moves)
        return best_move
    
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    def registerWin(self, hasWon):
        global games_left
        global index
        global gene_list
        global games_won
        global games_to_play
        global fitness_list
        if hasWon:
            games_won += 1
        if (games_left > 0): # decrement game counter or reset if done
            games_left -= 1
        else:
            fitness_list[index] = games_won / games_to_play
            games_left = 5 # reset and increase index
            gene_list = []
            games_won = 0
            if (index < population_size - 1):
                index += 1
                gene_list = read_genes(index)
            else: #if all indexes tested, create new generation
                generate_new_generation()
                index = 0
                gene_list = read_genes(index)


init_population()
gene_list = read_genes(index)
print(str(gene_list))