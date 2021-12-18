import numpy as np
import tensorflow.compat.v1 as tf

tf.disable_eager_execution()

class DQN:
    def __init__(self, params):
        # Подготовка сессии к использованию DQN
        self.parameters = params
        self.network_name = 'qnet'
        self.session = tf.Session()
        self.x = tf.placeholder('float', [None, params['width'], params['height'], 6],name = self.network_name + '_x')
        self.q_t = tf.placeholder('float', [None], name = self.network_name + '_q_t')
        self.actions = tf.placeholder("float", [None, 4], name = self.network_name + '_actions')
        self.rewards = tf.placeholder("float", [None], name = self.network_name + '_rewards')
        self.terminals = tf.placeholder("float", [None], name = self.network_name + '_terminals')

        # Первый convolutional layer
        layer = 'conv1' 
        size = 3 
        channels = 6 
        filters = 16 
        stride = 1
        self.w1 = tf.Variable(tf.random_normal([size, size, channels, filters], stddev = 0.01),name=self.network_name + '_' + layer + '_weights')
        self.b1 = tf.Variable(tf.constant(0.1, shape=[filters]),name=self.network_name + '_' + layer + '_biases')
        self.c1 = tf.nn.conv2d(self.x, self.w1, strides=[1, stride, stride, 1], padding='SAME',name = self.network_name + '_' + layer + '_convs')
        self.o1 = tf.nn.relu(tf.add(self.c1,self.b1),name=self.network_name + '_' + layer + '_activations')

        # Второй convolutional layer
        layer = 'conv2' 
        size = 3
        channels = 16 
        filters = 32
        stride = 1
        self.w2 = tf.Variable(tf.random_normal([size, size, channels, filters], stddev = 0.01), name = self.network_name + '_' + layer + '_weights')
        self.b2 = tf.Variable(tf.constant(0.1, shape=[filters]), name=self.network_name + '_' + layer + '_biases')
        self.c2 = tf.nn.conv2d(self.o1, self.w2, strides=[1, stride, stride, 1], padding = 'SAME', name = self.network_name + '_' + layer + '_convs')
        self.o2 = tf.nn.relu(tf.add(self.c2,self.b2), name = self.network_name + '_' + layer+ '_activations')
        
        o2_shape = self.o2.get_shape().as_list()        

        # Первый fully connected output layer
        layer = 'fc3'
        hiddens = 256
        dim = o2_shape[1]*o2_shape[2]*o2_shape[3]
        self.o2_flat = tf.reshape(self.o2, [-1,dim], name = self.network_name + '_' + layer + '_input_flat')
        self.w3 = tf.Variable(tf.random_normal([dim,hiddens], stddev = 0.01),name = self.network_name + '_' + layer + '_weights')
        self.b3 = tf.Variable(tf.constant(0.1, shape = [hiddens]), name = self.network_name + '_' + layer + '_biases')
        self.ip3 = tf.add(tf.matmul(self.o2_flat, self.w3),self.b3, name = self.network_name + '_' + layer + '_ips')
        self.o3 = tf.nn.relu(self.ip3, name = self.network_name + '_' + layer + '_activations')

        # Второй fully connected output layer
        layer = 'fc4'
        hiddens = 4 
        dim = 256
        self.w4 = tf.Variable(tf.random_normal([dim,hiddens], stddev = 0.01),name = self.network_name + '_' + layer + '_weights')
        self.b4 = tf.Variable(tf.constant(0.1, shape=[hiddens]),name = self.network_name + '_' + layer + '_biases')
        self.y = tf.add(tf.matmul(self.o3, self.w4), self.b4, name = self.network_name + '_' + layer + '_outputs')

        # Гамма коэффициент discount (насколько далеко в будущем агент, как ожидается, будет планировать)
        self.discount = tf.constant(self.parameters['discount'])
        self.yj = tf.add(self.rewards, tf.multiply(1.0-self.terminals, tf.multiply(self.discount, self.q_t)))
        self.Q_pred = tf.reduce_sum(tf.multiply(self.y,self.actions), reduction_indices = 1)
        self.cost = tf.reduce_sum(tf.pow(tf.subtract(self.yj, self.Q_pred), 2))
        
        if self.parameters['load_file'] is not None:
            self.global_step = tf.Variable(int(self.parameters['load_file'].split('_')[-1]), name = 'global_step', trainable = False)
        else:
            self.global_step = tf.Variable(0, name='global_step', trainable = False)
        
        self.optim = tf.train.AdamOptimizer(self.parameters['lr']).minimize(self.cost, global_step=self.global_step)
        self.saver = tf.train.Saver(max_to_keep = 0)

        self.session.run(tf.global_variables_initializer())

        if self.parameters['load_file'] is not None:
            self.saver.restore(self.session, self.parameters['load_file'])

    # Обучение модели
    def train(self, buff_s, buff_a, buff_t, buff_n, buff_r):
        feed_dict={self.x: buff_n, self.q_t: np.zeros(buff_n.shape[0]), self.actions: buff_a, self.terminals:buff_t, self.rewards: buff_r}
        q_t = self.session.run(self.y, feed_dict=feed_dict)
        q_t = np.amax(q_t, axis = 1)
        feed_dict={self.x: buff_s, self.q_t: q_t, self.actions: buff_a, self.terminals:buff_t, self.rewards: buff_r}
        _,cnt,cost = self.session.run([self.optim, self.global_step,self.cost],feed_dict=feed_dict)
        return cnt, cost

    # Сохранение модели
    def save_ckpt(self,filename):
        self.saver.save(self.session, filename)
