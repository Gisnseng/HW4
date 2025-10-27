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
gene_list = [] # list of genes
index = 0 #index
fitness_list = [] # list of fitnesses
population_size = 3 # inital population size
games_left = 5 # games_left to determine fitness
file_path = "phamt27_population.txt" # file path

#genes
#1 player food amount
#2 player soldier amount
#3 player ranger amount
#4 player drone amount
#5 player worker amount
#6 hp of player queen
#7 how many more food player has than enemy
#8 how much more health player queen has than enemy queen
#9 enemy worker amount
#10 distance of closest ally combatant to enemy queen

#strange genes
closest_worker_queen = 0 #11 distance of closest ally worker to enemy queen
engagement = 0 #12 distance between closest ally and enemy combatant


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
    #set gene variables
    #Gene 1

def vertical_dance(list1, list2): # input two lists of floats, return two lists of floats
    list3 = []
    list4 = []
    for i in range(len(list1) - 1):
        diff = list1[i] - list2[i]
        mutate = (random.random()-.5) #random between -0.5 and 0.5
        list3[i] = list1[i] - random.random() * diff + mutate
        mutate2 = (random.random()-.5) #random between -0.5 and 0.5
        list4[i] = list1[i] - random.random() * diff + mutate2
    ret = [list[3], list[4]]
    return ret

def generate_new_generation():
    half = population_size / 2 #divide population by two, rounded down

# kill half, prioritize bad


# mate the remaining genes
    pass

def read_genes(index):
#increment to index
    index_to_go = index
    file = open(file_path, "w")
    while index_to_go > 0:
        pass

def gene_utility():
    pass

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
    #HW 4 genes






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

    init_population()

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
        """Modified to use minimax with alpha-beta pruning instead of best-first search"""
        # CRITICAL CHECK: Verify it's actually our turn
        if currentState.whoseTurn != self.playerId:
            actual_player_id = currentState.whoseTurn
        else:
            actual_player_id = self.playerId
        
        # Get all legal moves from current state
        legal_moves = listAllLegalMoves(currentState)
        
        # SPEED OPTIMIZATION: Limit number of moves to explore at root
        if len(legal_moves) > 10:
            # Quick evaluation to rank moves
            scored_moves = []
            for move in legal_moves:
                # Skip most BUILD moves early game
                if move.moveType == BUILD:
                    my_ants = len(getAntList(currentState, actual_player_id, (WORKER, R_SOLDIER)))
                    if my_ants > 2:
                        continue
                
                # Quick score
                next_state = getNextStateAdversarial(currentState, move)
                quick_score = utility(next_state, actual_player_id)
                scored_moves.append((quick_score, move))
            
            # Keep top 10 moves (sort by score, which is first element of tuple)
            scored_moves.sort(key=lambda x: x[0])
            legal_moves = [move for score, move in scored_moves[:10]]
        
        best_move = None
        best_value = float('inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Evaluate each root-level move using minimax
        for move in legal_moves:
            node = createNode(move, currentState, 1, None, actual_player_id)
            
            # Search depth 1 (total 2 ply) for speed
            value, _ = minimax_alpha_beta(node, 1, alpha, beta, actual_player_id)
            
            if value < best_value:
                best_value = value
                best_move = move
        
        return best_move
    
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    def registerWin(self, hasWon):
        if (games_left > 0): # decrement game counter or reset if done
            games_left -= 1
        else:
            games_left = 5 # reset and increase index
            if (index < population_size - 1):
                index += 1
            else: #if all indexes tested, create new generation
                generate_new_generation()
                index = 0
        pass