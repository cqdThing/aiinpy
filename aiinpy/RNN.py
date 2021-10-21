import numpy as np
from .Activation import ApplyActivation, ActivationDerivative

class RNN:
  def __init__(self, InputSize, OutputSize, HidSize=64, LearningRate=0.05):
    self.LearningRate, self.HidSize = LearningRate, HidSize

    self.WeightsHidToHid = np.random.uniform(-0.005, 0.005, (HidSize, HidSize))
    self.WeightsInputToHid = np.random.uniform(-0.005, 0.005, (HidSize, InputSize))
    self.WeightsHidToOut = np.random.uniform(-0.005, 0.005, (OutputSize, HidSize))

    self.HiddenBiases = np.zeros(HidSize)
    self.OutputBiases = np.zeros(OutputSize)

  def ForwardProp(self, InputLayer):
    self.InputLayer = InputLayer
    self.Hidden = np.zeros((len(self.InputLayer) + 1, self.HidSize))

    for i in range(len(InputLayer)):
      self.Hidden[i + 1, :] = ApplyActivation(self.WeightsInputToHid @ InputLayer[i] + self.WeightsHidToHid @ self.Hidden[i, :] + self.HiddenBiases, 'Tanh')
    
    self.Out = ApplyActivation(self.WeightsHidToOut @ self.Hidden[len(InputLayer), :] + self.OutputBiases, 'StableSoftmax')
    return self.Out

  def BackProp(self, OutputError):
    OutputGradient = np.multiply(ActivationDerivative(self.Out, 'StableSoftmax'), OutputError)
    
    self.WeightsHidToOutDeltas = np.outer(OutputGradient, self.Hidden[len(self.InputLayer)].T)
    self.OutputBiasesDeltas = OutputGradient

    self.WeightsHidToHidDeltas = np.zeros(self.WeightsHidToHid.shape)
    self.WeightsInputToHidDeltas = np.zeros(self.WeightsInputToHid.shape)
    self.HiddenBiasesDeltas = np.zeros(self.HiddenBiases.shape)

    self.HiddenError = self.WeightsHidToOut.T @ OutputError

    for i in reversed(range(len(self.InputLayer))):
      self.HiddenGradient = np.multiply(ActivationDerivative(self.Hidden[i + 1], 'Tanh'), self.HiddenError)

      self.HiddenBiasesDeltas += self.HiddenGradient
      self.WeightsHidToHidDeltas += np.outer(self.HiddenGradient, self.Hidden[i].T)
      self.WeightsInputToHidDeltas += np.outer(self.HiddenGradient, self.InputLayer[i].T)

      self.HiddenError = self.WeightsHidToHid.T @ self.HiddenGradient

    self.WeightsHidToHid += self.LearningRate * np.clip(self.WeightsHidToHidDeltas, -1, 1)
    self.WeightsInputToHid += self.LearningRate * np.clip(self.WeightsInputToHidDeltas, -1, 1)
    self.WeightsHidToOut += self.LearningRate * np.clip(self.WeightsHidToOutDeltas, -1, 1)
    self.HiddenBiases += self.LearningRate * np.clip(self.HiddenBiasesDeltas, -1, 1)
    self.OutputBiases += self.LearningRate * np.clip(self.OutputBiasesDeltas, -1, 1)