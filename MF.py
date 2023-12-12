import numpy as np

from Util import *

class MF:
    def __init__(self, matrix, K, alpha, beta):
        self.matrix = matrix
        self.num_users, self.num_items = matrix.shape
        self. K = K
        self.alpha = alpha
        self.beta = beta
        self.user_matrix = np.random.normal(scale=1./self.K, size=(self.num_users, self.K))
        self.item_matrix = np.random.normal(scale=1./self.K, size=(self.K, self.num_items))
        self.user_bias = np.zeros(self.num_users)
        self.item_bias = np.zeros(self.num_items)
        self.data = [(i, j, self.matrix[i, j]) for i in range(self.num_users)
                     for j in range(self.num_items) if self.matrix[i, j]]
        self.bias = sum(r for _, _, r in self.data)/len(self.data)
        self.train_data, self.val_data = train_test_split(self.data)
    def train(self):
        min_val_error = float('inf')
        epoch = 1
        bar = tqdm(desc=f"Factorizing matrix of size {self.matrix.shape}")
        while True:
            np.random.shuffle(self.train_data)
            for i, j, r in self.train_data:
                error = r - self.get_rating(i, j)
                self.user_bias[i] += self.alpha * (error - self.beta * self.user_bias[i])
                self.item_bias[j] += self.alpha * (error - self.beta * self.item_bias[j])
                self.user_matrix[i, :] += self.alpha * (error * self.item_matrix[:, j].T - self.beta*self.user_matrix[i, :])
                self.item_matrix[:, j] += self.alpha * (error * self.user_matrix[i, :].T - self.beta*self.item_matrix[:, j])
            if epoch % 10 == 0:
                val_error = self.mse(True)
                min_val_error = min(min_val_error, val_error)
                if val_error > min_val_error * 1.05:
                    print(f"Ended training at epoch {epoch} and loss {self.mse()}")
                    break
            epoch += 1
            bar.update()

    def get_rating(self, i, j):
        return (self.bias + self.user_bias[i] + self.item_bias[j] +
                self.user_matrix[i, :].dot(self.item_matrix[:, j]))

    def full_matrix(self):
        return (self.bias + self.user_bias[:,np.newaxis] +
                self.item_bias[np.newaxis:,] + self.user_matrix.dot(self.item_matrix))

    def mse(self, val_only=False):
        data = self.val_data if val_only else self.data
        predictions = self.full_matrix()
        return sum(np.square(r-predictions[i, j]) for i, j, r in data)/len(data)
