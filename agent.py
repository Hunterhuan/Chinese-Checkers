import random, re, datetime
import numpy as np


class Agent(object):
    def __init__(self, game):
        self.game = game

    def getAction(self, state):
        raise Exception("Not implemented yet")


class RandomAgent(Agent):
    def getAction(self, state):
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)


class SimpleGreedyAgent(Agent):
    # a one-step-lookahead greedy agent that returns action with max vertical advance
    def getAction(self, state):
        legal_actions = self.game.actions(state)

        self.action = random.choice(legal_actions)

        player = self.game.player(state)
        if player == 1:
            max_vertical_advance_one_step = max([action[0][0] - action[1][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[0][0] - action[1][0] == max_vertical_advance_one_step]
        else:
            max_vertical_advance_one_step = max([action[1][0] - action[0][0] for action in legal_actions])
            max_actions = [action for action in legal_actions if
                           action[1][0] - action[0][0] == max_vertical_advance_one_step]
        self.action = random.choice(max_actions)



class Frappuccino(Agent):
    def evaluation(self, state, player):
        board = state[1]
        pos_player1_list = board.getPlayerPiecePositions(1)
        pos_player2_list = board.getPlayerPiecePositions(2)
        h_value = 0
        board_size = self.game.size
        if player == 1:
            for col_player1 in pos_player1_list:
                h_value -= col_player1[0] ** 2
            for col_player2 in pos_player2_list:
                h_value += (2 * board_size - col_player2[0]) ** 2
        else:
            for col_player1 in pos_player1_list:
                h_value += col_player1[0] ** 2
            for col_player2 in pos_player2_list:
                h_value -= (2 * board_size - col_player2[0]) ** 2
        return h_value

    def max_value(self, state, a, b, player, layer, tobeend = False):
        if tobeend: state = (3-state[0],state[1])
        #assert state[0] == player
        EV = float('-inf')
        if layer == 1:
            for action in self.game.actions(state):
                state_after = self.game.succ(state,action)
                nextEV = self.get_nextEV(state,action,state_after,player)
                if nextEV > EV:
                    EV = nextEV
                    if EV > b: return EV
                    a = max(a, EV)
        elif layer > 1:
            actions = self.game.actions(state)
            state_after_dict = {}
            for action in actions:
                state_after_dict[action] = self.game.succ(state,action)
            action_state_tuple = sorted(state_after_dict.items(),key = lambda tuple: self.get_nextEV(state,tuple[0],tuple[1],player),reverse = True)
            for action,state_after in action_state_tuple:
                if self.isend(state_after,player):
                    nextEV = self.get_nextEV(state,action,state_after,player) + (layer-1)*30
                else:
                    if tobeend:
                        nextEV = self.max_value(state_after, a, b, player, layer - 1, True)
                    else:
                        nextEV = self.min_value(state_after, a, b, player, layer - 1)
                if nextEV > EV:
                    EV = nextEV
                    if EV > b: return EV
                    a = max(a, EV)
        return EV

    def min_value(self, state, a, b, player, layer):
        #assert state[0] == 3-player
        EV = float('inf')
        if layer == 1:
            for action in self.game.actions(state):
                state_after = self.game.succ(state,action)
                nextEV = self.get_nextEV(state,action,state_after,player)
                if nextEV < EV:
                    EV = nextEV
                    if EV < a: return EV
                    b = min(b, EV)
        elif layer > 1:
            actions = self.game.actions(state)
            state_after_dict = {}
            for action in actions:
                state_after_dict[action] = self.game.succ(state,action)
            action_state_tuple = sorted(state_after_dict.items(),key = lambda tuple: self.get_nextEV(state,tuple[0],tuple[1],player),reverse = False)
            for action,state_after in action_state_tuple:
                #state_after = self.game.succ(state,action)
                if self.isend(state_after,3-player):
                    nextEV = self.get_nextEV(state,action,state_after,player) - (layer-1)*30
                else:
                    nextEV = self.max_value(state_after, a, b, player, layer - 1)
                if nextEV < EV:
                    EV = nextEV
                    if EV < a: return EV
                    b = min(b, EV)
        return EV

    def get_nextEV(self,state,action,state_after,player):
        hash_state_after = self.hash_dict(state_after)
        if hash_state_after in self.dict:
            nextEV = self.dict[hash_state_after]
        else:
            hash_state = self.hash_dict(state)
            if hash_state in self.dict:
                nextEV = self.dict[hash_state] + self.deltaEV(state,action,player)
            else:
                nextEV = self.evaluation(state_after,player)
            self.dict[hash_state_after] = nextEV
        return nextEV


    def hash_dict(self, state):
        board = state[1]
        board_status = board.board_status
        size = board.size
        cvt_str = ''
        for row in range(1, size + 1):
            for col in range(1, board.getColNum(row) + 1):
                cvt_str += str(board_status[(row, col)])
        for row in range(size + 1, size * 2):
            for col in range(1, board.getColNum(row) + 1):
                cvt_str += str(board_status[(row, col)])
        return hash(cvt_str)

    def deltaEV(self, state, action, player):
        player_step = state[0]
        board_size = self.game.size
        if player == 1:
            if player_step == 1:
                return action[0][0]**2 - action[1][0]**2
            else:
                return (2 * board_size - action[1][0]) ** 2 - (2 * board_size - action[0][0]) ** 2
        else:
            if player_step == 2:
                return (2 * board_size - action[0][0]) ** 2 - (2 * board_size - action[1][0]) ** 2
            else:
                return action[1][0]**2 - action[0][0]**2

    def isend(self, state, player):
        board = state[1]
        board_status = board.board_status
        size = board.size
        piece_rows = board.piece_rows
        if player == 1:
            for row in range(1, piece_rows + 1):
                for col in range(1, board.getColNum(row) + 1):
                    if board_status[(row, col)] != 1:
                        return False
            return True
        else:
            for row in range(size * 2 - piece_rows, size * 2):
                for col in range(1, board.getColNum(row) + 1):
                    if board_status[(row, col)] != 2:
                        return False
            return True

    def tobeend(self, state, player):
        board = state[1]
        pos_player1_list = board.getPlayerPiecePositions(1)
        pos_player2_list = board.getPlayerPiecePositions(2)
        bottom1 = max([piece[0] for piece in pos_player1_list])
        top2 = min([piece[0] for piece in pos_player2_list])
        if player == 1:
            return bottom1 < top2
        else:
            return top2 > bottom1
    
    def getAction(self, state):
        self.dict = {}
        player = self.game.player(state)
        EVinit = self.evaluation(state,player)
        self.dict[self.hash_dict(state)] = EVinit
        EVcandidate = float('-inf')
        tobeend = self.tobeend(state, player)

        action_list = self.game.actions(state)
        random.shuffle(action_list)
        action_EV = np.zeros(len(action_list))

        for i in range(len(action_list)):
            action = action_list[i]
            newEV = EVinit + self.deltaEV(state,action,player)
            state_after = self.game.succ(state,action)
            self.dict[self.hash_dict(state_after)] = newEV
            action_EV[i] = newEV
            if newEV >= EVcandidate:
                if newEV == EVcandidate and random.choice([True,False]): continue
                EVcandidate = newEV
                self.action = action
                #print('update', 1, EVcandidate)

        L_last = 1
        for L in range(2,50):
            #print(L)
            a = float('-inf')
            b = float('inf')
            action_EV_index = action_EV.argsort()
            for i in range(len(action_EV_index) - 1, -1, -1):
                state_after = self.game.succ(state,action_list[action_EV_index[i]])
                if self.isend(state_after,player):
                    newEV = self.get_nextEV(state,action_list[action_EV_index[i]],state_after,player) + (L-1)*30
                else:
                    if tobeend:
                        newEV = self.max_value(state_after, a, b, player, L - 1, True)
                    else:
                        newEV = self.min_value(state_after, a, b, player, L - 1)
                action_EV[action_EV_index[i]] = newEV
                if newEV > EVcandidate or L > L_last:
                    EVcandidate = newEV
                    self.action = action_list[action_EV_index[i]]
                    #print('update', L, EVcandidate)
                    a = max(a, EVcandidate)
                L_last = L
