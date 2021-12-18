import numpy as np
import random
import util
import time
import sys

from pacman import Directions
from game import Agent
import game
from collections import deque
import tensorflow.compat.v1 as tf
from DQN import *

params = {
    'load_file': None,
    'save_file': None,
    'save_interval' : 10000, 
    'train_start': 5000,
    'buff_size': 32,
    'mem_size': 100000,
    'discount': 0.95, # гамма коэффициент, насколько далеко в    
                      # будущем агент, как ожидается, будет планировать
    'lr': .0002,
    'eps': 1.0, # Отвечает за количество рандомных движений, совершенных агентом
    'eps_final': 0.1, # 10% от всех ходов по-прежнему остаются рандомными
    'eps_step': 10000 
}                     



class PacmanDQN(game.Agent):
    def __init__(self, args):
        self.params = params
        self.params['width'] = args['width']
        self.params['height'] = args['height']
        self.params['num_training'] = args['numTraining']

        # Выделить 10% свободной видеопамяти на каждый процесс
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.1)
        # Конфигурация сессии
        self.sess = tf.Session(config = tf.ConfigProto(gpu_options = gpu_options))
        self.qnet = DQN(self.params) # Нейронная сеть
        self.general_record_time = time.strftime("%a_%d_%b_%Y_%H_%M_%S", time.localtime())
        self.Q_global = [] # Лучшие ходы, которые выдает нейронная сеть
        self.cost_disp = 0     
        self.cnt = self.qnet.session.run(self.qnet.global_step) # Запуск сессии
        self.local_cnt = 0

        self.numeps = 0
        self.last_score = 0
        self.s = time.time()
        self.last_reward = 0.

        self.replay_mem = deque()
        self.last_scores = deque()


    def getMove(self):
        # Если больше, чем eps - просчитывать ход
        # Иначе - совершать рандомный ход
        if np.random.rand() > self.params['eps']:
            # Запускаем сессию нейронной сети
            # После - выбираем лучший по ее мнению ход
            self.Q_pred = self.qnet.session.run(
                self.qnet.y,
                feed_dict = {self.qnet.x: np.reshape(self.current_state,
                                                     (1, self.params['width'], self.params['height'], 6)), 
                self.qnet.q_t: np.zeros(1),
                self.qnet.actions: np.zeros((1, 4)),
                self.qnet.terminals: np.zeros(1),
                self.qnet.rewards: np.zeros(1)}
            )[0]

            # Выбираем лучший по мнению сети ход
            self.Q_global.append(max(self.Q_pred))
            a_winner = np.argwhere(self.Q_pred == np.amax(self.Q_pred))

            # Выбираем любой из лучших ходов (случай, когда награды одинаковы)
            if len(a_winner) > 1:
                move = self.get_direction(
                    a_winner[np.random.randint(0, len(a_winner))][0])
            else:
                move = self.get_direction(
                    a_winner[0][0])
        else:
            move = self.get_direction(np.random.randint(0, 4))

        self.last_action = self.get_value(move)

        return move

    # ------ Направления ходов ------
    def get_value(self, direction):
        if direction == Directions.NORTH:
            return 0.
        elif direction == Directions.EAST:
            return 1.
        elif direction == Directions.SOUTH:
            return 2.
        else:
            return 3.

    def get_direction(self, value):
        if value == 0.:
            return Directions.NORTH
        elif value == 1.:
            return Directions.EAST
        elif value == 2.:
            return Directions.SOUTH
        else:
            return Directions.WEST
    # ------------ X ------------

    # Награды/штрафы за ходы
    def observation_step(self, state):
        if self.last_action is not None:
            self.last_state = np.copy(self.current_state)
            self.current_state = self.getStateMatrices(state)
            self.current_score = state.getScore()
            reward = self.current_score - self.last_score
            self.last_score = self.current_score

            if reward > 20: # Поедание агента
                self.last_reward = 50.
            elif reward > 0: # Поедание монеты
                self.last_reward = 10. 
            elif reward < -10: # Проигрыш
                self.last_reward = -500.
                self.won = False
            elif reward < 0: # Безрезультативный ход
                self.last_reward = -1.  

            
            if(self.terminal and self.won):
                self.last_reward = 100.
            self.ep_rew += self.last_reward

            experience = (self.last_state, float(self.last_reward), self.last_action, self.current_state, self.terminal)
            self.replay_mem.append(experience)
            if len(self.replay_mem) > self.params['mem_size']:
                self.replay_mem.popleft()
            # if(params['save_file']):
            #     if self.local_cnt > self.params['train_start'] and self.local_cnt % self.params['save_interval'] == 0:
            #         self.qnet.save_ckpt('saves/model-' + params['save_file'] + "_" + str(self.cnt) + '_' + str(self.numeps))
            #         print('Model saved')
            self.train()
        self.local_cnt += 1
        self.frame += 1
        self.params['eps'] = max(self.params['eps_final'],
                                 1.00 - float(self.cnt)/ float(self.params['eps_step']))


    def observationFunction(self, state):
        self.terminal = False
        self.observation_step(state)

        return state

    # Логирование
    def final(self, state):
        self.ep_rew += self.last_reward
        self.terminal = True
        self.observation_step(state)
        log_file = open('./logs/'+str(self.general_record_time)+'-l-'+str(self.params['width'])+'-m-'+str(self.params['height'])+'-x-'+str(self.params['num_training'])+'.log','a')
        log_file.write("# %4d | steps: %5d | steps_t: %5d | t: %4f | r: %12f | e: %10f " %
                         (self.numeps,self.local_cnt, self.cnt, time.time()-self.s, self.ep_rew, self.params['eps']))
        log_file.write("| Q: %10f | won: %r \n" % ((max(self.Q_global, default=float('nan')), self.won)))
        sys.stdout.write("# %4d steps: %5d steps_t: %5d t: %4f r: %12f e: %10f " %
                         (self.numeps,self.local_cnt, self.cnt, time.time()-self.s, self.ep_rew, self.params['eps']))
        sys.stdout.write("Q: %10f won: %r \n" % ((max(self.Q_global, default=float('nan')), self.won)))
        sys.stdout.flush()

    # Обучение модели
    def train(self):
        if (self.local_cnt > self.params['train_start']):
            # Собираем опыт, который получил агент в процессе обучения
            # Буфер опыта
            buff = random.sample(self.replay_mem, self.params['buff_size'])
            buff_s = []
            buff_r = []
            buff_a = []
            buff_n = []
            buff_t = [] 

            for i in buff:
                buff_s.append(i[0])
                buff_r.append(i[1])
                buff_a.append(i[2])
                buff_n.append(i[3])
                buff_t.append(i[4])
            buff_s = np.array(buff_s) # Свое предыдущее определение
            buff_r = np.array(buff_r) # Свое предыдущее определение
            buff_a = self.get_onehot(np.array(buff_a)) # Свое предыдущее определение

            buff_n = np.array(buff_n) # t - логическое значение, которое позволяет
                                        # агенту узнать, было ли это конечным состоянием эпизода

            buff_t = np.array(buff_t) # Состояние, которое следует за s, когда агент
                                        # предпринял действие a.

            # Запуск обучения модели 
            self.cnt, self.cost_disp = self.qnet.train(buff_s, buff_a, buff_t, buff_n, buff_r)


    def get_onehot(self, actions):
        actions_onehot = np.zeros((self.params['buff_size'], 4))
        for i in range(len(actions)):                                           
            actions_onehot[i][int(actions[i])] = 1      
        return actions_onehot   

    def mergeStateMatrices(self, stateMatrices):
        stateMatrices = np.swapaxes(stateMatrices, 0, 2)
        total = np.zeros((7, 7))
        for i in range(len(stateMatrices)):
            total += (i + 1) * stateMatrices[i] / 6
        return total

    def getStateMatrices(self, state):
        def getWallMatrix(state):
            width, height = state.data.layout.width, state.data.layout.height
            grid = state.data.layout.walls
            matrix = np.zeros((height, width), dtype=np.int8)
            for i in range(grid.height):
                for j in range(grid.width):
                    cell = 1 if grid[j][i] else 0
                    matrix[-1-i][j] = cell
            return matrix

        def getPacmanMatrix(state):
            width, height = state.data.layout.width, state.data.layout.height
            matrix = np.zeros((height, width), dtype=np.int8)

            for agentState in state.data.agentStates:
                if agentState.isPacman:
                    pos = agentState.configuration.getPosition()
                    cell = 1
                    matrix[-1-int(pos[1])][int(pos[0])] = cell

            return matrix

        def getGhostMatrix(state):
            width, height = state.data.layout.width, state.data.layout.height
            matrix = np.zeros((height, width), dtype=np.int8)

            for agentState in state.data.agentStates:
                if not agentState.isPacman:
                    if not agentState.scaredTimer > 0:
                        pos = agentState.configuration.getPosition()
                        cell = 1
                        matrix[-1-int(pos[1])][int(pos[0])] = cell

            return matrix

        def getScaredGhostMatrix(state):
            width, height = state.data.layout.width, state.data.layout.height
            matrix = np.zeros((height, width), dtype=np.int8)

            for agentState in state.data.agentStates:
                if not agentState.isPacman:
                    if agentState.scaredTimer > 0:
                        pos = agentState.configuration.getPosition()
                        cell = 1
                        matrix[-1-int(pos[1])][int(pos[0])] = cell

            return matrix

        def getFoodMatrix(state):
            width, height = state.data.layout.width, state.data.layout.height
            grid = state.data.food
            matrix = np.zeros((height, width), dtype=np.int8)

            for i in range(grid.height):
                for j in range(grid.width):
                    cell = 1 if grid[j][i] else 0
                    matrix[-1-i][j] = cell

            return matrix

        def getCapsulesMatrix(state):
            width, height = state.data.layout.width, state.data.layout.height
            capsules = state.data.layout.capsules
            matrix = np.zeros((height, width), dtype=np.int8)

            for i in capsules:
                matrix[-1-i[1], i[0]] = 1

            return matrix

        width, height = self.params['width'], self.params['height']
        observation = np.zeros((6, height, width))

        observation[0] = getWallMatrix(state)
        observation[1] = getPacmanMatrix(state)
        observation[2] = getGhostMatrix(state)
        observation[3] = getScaredGhostMatrix(state)
        observation[4] = getFoodMatrix(state)
        observation[5] = getCapsulesMatrix(state)

        observation = np.swapaxes(observation, 0, 2)

        return observation

    # Начальное состояние игры
    def registerInitialState(self, state):
        self.last_score = 0
        self.current_score = 0
        self.last_reward = 0.
        self.ep_rew = 0
        self.last_state = None
        self.current_state = self.getStateMatrices(state)
        self.last_action = None
        self.terminal = None
        self.won = True
        self.Q_global = []
        self.delay = 0
        self.frame = 0
        self.numeps += 1

    def getAction(self, state):
        move = self.getMove()
        legal = state.getLegalActions(0)
        if move not in legal:
            move = Directions.STOP

        return move
