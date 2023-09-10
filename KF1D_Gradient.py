import numpy as np

# Kalman Filter Functions


def systemDynamics(x_nn, p_nn, q=0.0001):
    x_pred = x_nn
    p_pred = p_nn + q

    return x_pred, p_pred


def k_update(p_nn_1, r):
    k = p_nn_1/(p_nn_1 + r)

    return k


def stateEstimation(x_nn_1, p_nn_1, gain, z_n):
    x_nn = x_nn_1 + gain*(z_n - x_nn_1)
    p_nn = (1 - gain)*p_nn_1

    return x_nn, p_nn


def statePrediction(x_nn, p_nn, q):
    x_pred, p_pred = systemDynamics(x_nn, p_nn, q)

    return x_pred, p_pred

# Gradient Calculation Functions


def gradEstimation(ay, by):
    '''
    Calculates gradient between two samples
    Returns Magnitud and Phase
    '''
    # Due to the sampling interval is constant
    # Then ax = 0 & bx = 1
    magnitud = np.sqrt(1 + (by - ay)**2)
    phase = np.arctan((by - ay))
    angle = np.rad2deg(phase)

    return magnitud, phase, angle


class AutoRegressor:

    def __init__(self, measError, procError, start) -> None:
        self._Q = procError
        self._R = measError**2
        self._K = 0
        self._P = 0
        self._S = 0
        self._y = 0
        self._yn = 0
        self.start = start
        self._iteration = 0
        self.gain = []
        self._rollback = []
        self._grad = {"mag": 0, "ang": 0, "arc": 0}

    def estimate(self, zn):

        # Initial Estimation
        if self._iteration == 0:
            self._S = zn
            self._y = zn
            self._yn = zn
            self._iteration += 1
        # Optimal Estimation
        else:
            self._yn = self._y
            # Kalman Gain update
            self._K = k_update(self._P, self._R)
            self._set_gain(self._K)
            # State Estimation
            self._S, self._P = stateEstimation(self._S, self._P, self._K, zn)
            self._y = self._S
            # State Prediction
            self._S, self._P = statePrediction(self._S, self._P, self._Q)
            # increment iteration
            self._iteration += 1

        return self._y

    def _set_gain(self, value):
        # check maximum alocation in gain array
        if len(self.gain) > 80:
            pass
        else:
            self.gain.append(value)

    def gradient(self):
        if self._iteration <= self.start:
            return None
        else:
            magnitud, phase, angle = gradEstimation(self._yn, self._y)
            self._grad['mag'] = magnitud
            self._grad['ang'] = angle
            self._grad['arc'] = phase

            return self._grad
