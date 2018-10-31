import numpy as np
from keras.layers import Dense, BatchNormalization, Dropout
from keras.models import Sequential
from keras.optimizers import Adagrad
from tensorflow import set_random_seed

np.random.seed(1)
set_random_seed(1)


class DemandModel:

    def __init__(self, monthly_trends, prev_months=3, verbose=False):

        self.monthly_trends = monthly_trends
        self.prev_months = prev_months

        training_data = monthly_trends[:int(monthly_trends.shape[0] * 0.8), :]
        test_data = monthly_trends[int(monthly_trends.shape[0] * 0.8):, :]

        trainX = np.zeros((training_data.shape[0] - prev_months, prev_months * training_data.shape[1]))
        trainY = np.zeros((training_data.shape[0] - prev_months, training_data.shape[1]))

        for i in range(prev_months, trainX.shape[0] + prev_months):
            trainX[i - prev_months, :] = training_data[i - prev_months:i, :].reshape(
                (prev_months * training_data.shape[1],))
            trainY[i - prev_months, :] = training_data[i, :].reshape((training_data.shape[1],))

        testX = np.zeros((test_data.shape[0] - prev_months, prev_months * test_data.shape[1]))
        testY = np.zeros((test_data.shape[0] - prev_months, test_data.shape[1]))

        for i in range(prev_months, testX.shape[0] + prev_months):
            testX[i - prev_months, :] = test_data[i - prev_months:i, :].reshape((prev_months * test_data.shape[1],))
            testY[i - prev_months, :] = test_data[i, :].reshape((test_data.shape[1],))

        model = Sequential()
        model.add(Dense(750, activation='tanh', input_shape=(trainX.shape[1],)))
        model.add(BatchNormalization())
        model.add(Dropout(0.4))
        model.add(Dense(1250, activation='tanh'))
        model.add(BatchNormalization())
        model.add(Dropout(0.3))
        model.add(Dense(483, activation='tanh'))
        model.add(Dense(trainY.shape[1], activation=None))

        model.compile(loss='mse', optimizer=Adagrad())

        model.fit(trainX, trainY, epochs=200, batch_size=64, shuffle=True, verbose=(verbose * 1))

        self.model = model

        predictions = np.abs(np.rint(model.predict(trainX)))

        metrics = evaluate_model(trainY, predictions)

        print("-" * 50)
        print("Training Accuracy:", metrics[0] * 100)
        print("Training Optimism:", metrics[1])
        print("-" * 50)

        predictions = np.abs(np.rint(model.predict(testX)))

        metrics = evaluate_model(testY, predictions)

        print("-" * 50)
        print("Testing Accuracy:", metrics[0] * 100)
        print("Testing Optimism:", metrics[1])
        print("-" * 50)

    def predict_demand(self, demand_seen):

        for i in range(demand_seen.shape[0]):
            if np.all(demand_seen[i, :] == 0):
                month = i + 1
                break

        if month <= self.prev_months:
            return self.monthly_trends[month - 1, :]
        else:
            lastkmonths = demand_seen[month - (self.prev_months + 1):month - 1, :].reshape((1, self.prev_months * demand_seen.shape[1]))
            predicted_demand = np.abs(np.rint(self.model.predict(lastkmonths)))
            predicted_demand = predicted_demand[0, :]
            return predicted_demand

    def predict_demand_in_2_months(self, demand_seen):

        temp1 = demand_seen.copy()
        temp2 = np.zeros((6, self.monthly_trends.shape[1]))
        temp = np.concatenate((temp1, temp2), axis=0)

        month = 12

        for i in range(demand_seen.shape[0]):
            if np.all(demand_seen[i, :] == 0):
                month = i
                break

        if month <= self.prev_months or month < 2:
            return self.monthly_trends[month - 1, :]
        else:
            lastkmonths = demand_seen[month - self.prev_months:month, :].reshape(
                (1, self.prev_months * demand_seen.shape[1]))
            predicted_demand = np.abs(np.rint(self.model.predict(lastkmonths)))
            temp[month, :] = predicted_demand[0, :]

            month = month + 1
            lastkmonths = temp[month - self.prev_months:month, :].reshape(
                (1, self.prev_months * temp.shape[1]))
            predicted_demand = np.abs(np.rint(self.model.predict(lastkmonths)))
            predicted_demand = predicted_demand[0, :]
            return predicted_demand


def evaluate_model(testY, predictions):
    metrics = np.zeros((testY.shape[0], 2))
    for i in range(testY.shape[0]):
        pred = predictions[i, :]
        true = testY[i, :]

        diff = true - pred
        diff = diff[diff > 0]
        correct = np.sum(true) - np.sum(diff)

        metrics[i, 0] = correct / np.sum(true)
        metrics[i, 1] = (np.sum(pred) * 100) / np.sum(true)

    metrics = np.mean(metrics, axis=0)

    return metrics
