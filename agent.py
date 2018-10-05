import random, re, datetime
import time

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
        if player == 1:
            for col_player1 in pos_player1_list:
                h_value -= col_player1[0] 
            for col_player2 in pos_player2_list:
                h_value -= col_player2[0]
        else:
            for col_player1 in pos_player1_list:
                h_value += col_player1[0]
            for col_player2 in pos_player2_list:
                h_value += col_player2[0]
        return h_value

    def max_value(self, state, player, layer):
        if layer > 1:
            layer -= 1
            first_flag = True
            legal_actions = self.game.actions(state)
            value = 0
            for action in legal_actions:
                state_after = self.game.succ(state,action)
                min_v = self.min_value(state_after,player,layer)
                if first_flag or  min_v > value:
                    value = min_v
                    first_flag = False
            return value
        if layer <= 1:
            return self.evaluation(state,player)
    
    def min_value(self, state, player, layer):
        if layer > 1:
            layer -= 1
            first_flag = True
            legal_actions = self.game.actions(state)
            value = 0
            for action in legal_actions:
                state_after = self.game.succ(state,action)
                max_v = self.max_value(state_after,player,layer)
                if first_flag or max_v < value:
                    value = max_v
                    first_flag = False
            return value
        if layer <= 1:
            return self.evaluation(state,player)

    def getAction(self, state):
        start = time.clock()
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)
        player = self.game.player(state)
        layer = 3

        layer -= 1
        first_flag = True
        evaluation_candidate = 0
        for action in legal_actions:
            state_after = self.game.succ(state,action)
            min_v = self.min_value(state_after,player,layer)
            if first_flag or min_v > evaluation_candidate:
                evaluation_candidate = min_v
                first_flag = False
                self.action = action
                print('update',self.action)
        print('finish',self.action)
        print('time:',time.clock() - start)


class Alpha_beta(Agent):
    def evaluation(self, state, player):
        board = state[1]
        pos_player1_list = board.getPlayerPiecePositions(1)
        pos_player2_list = board.getPlayerPiecePositions(2)
        h_value = 0
        if player == 1:
            for col_player1 in pos_player1_list:
                h_value -= col_player1[0] 
            for col_player2 in pos_player2_list:
                h_value -= col_player2[0]
        else:
            for col_player1 in pos_player1_list:
                h_value += col_player1[0]
            for col_player2 in pos_player2_list:
                h_value += col_player2[0]
        return h_value

    def max_value(self, state, a, b, player, layer):
        if layer > 1:
            layer -= 1
            first_flag = True
            legal_actions = self.game.actions(state)
            value = 0
            for action in legal_actions:
                state_after = self.game.succ(state,action)
                min_v = self.min_value(state_after,a,b,player,layer)
                if first_flag or  min_v > value:
                    value = min_v
                    first_flag = False
                    if value > b: return value
                    a = max(a, value)
            return value
        if layer <= 1:
            return self.evaluation(state,player)

    def min_value(self, state, a, b, player, layer):
        if layer > 1:
            layer -= 1
            first_flag = True
            legal_actions = self.game.actions(state)
            value = 0
            for action in legal_actions:
                state_after = self.game.succ(state,action)
                max_v = self.max_value(state_after,a,b,player,layer)
                if first_flag or max_v < value:
                    value = max_v
                    first_flag = False
                    if value < a: return value
                    b = min(b, value)
            return value
        if layer <= 1:
            return self.evaluation(state,player)
        
    def getAction(self, state):
        start = time.clock()
        legal_actions = self.game.actions(state)
        self.action = random.choice(legal_actions)
        player = self.game.player(state)
        layer = 3
        a = -10000
        b = 10000

        layer -= 1
        first_flag = True
        evaluation_candidate = 0
        for action in legal_actions:
            state_after = self.game.succ(state,action)
            min_v = self.min_value(state_after,a,b,player,layer)
            if first_flag or min_v > evaluation_candidate:
                evaluation_candidate = min_v
                first_flag = False
                #if evaluation_candidate > b: break
                a = max(a,evaluation_candidate)
                self.action = action
                print('update',self.action)
        print('finish',self.action)
        print('time:',time.clock() - start)



