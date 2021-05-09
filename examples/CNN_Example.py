import numpy as np
from emnist import extract_training_samples, extract_test_samples
from aiinpy.CONV import CONV
from aiinpy.NN import NN
from aiinpy.POOL import POOL
from alive_progress import alive_bar

InputImageToConv1 = CONV((4, 3, 3), LearningRate=0.005)
Conv1ToPool1 = POOL(2)
InputToHid1 = NN((4 * 13 * 13), 10, "StableSoftMax", LearningRate=0.1, WeightsInit=(0, 0))

def TestNetwork():
  NumberCorrect = 0
  for Generation in range(TestImageLoaded):
    InputImage = (TestImages[Generation] / 255) - 0.5
    ConvolutionLayer1 = InputImageToConv1.ForwardProp(InputImage)
    MaxPooling1 = Conv1ToPool1.ForwardProp(ConvolutionLayer1)
    Input = MaxPooling1.flatten()
    Output = InputToHid1.ForwardProp(Input)
    
    NumberCorrect += 1 if np.argmax(Output) == TestLabels[Generation] else 0
    bar()

  return NumberCorrect / Generation

# Load EMNIST Training And Testing Images
TrainingImageLoaded = 1000
TestImageLoaded = 1000
TrainingImages, TrainingLabels = extract_training_samples('digits')
TestImages, TestLabels = extract_test_samples('digits')[0 : TestImageLoaded]

with alive_bar(1000 + TestImageLoaded) as bar:
  for Generation in range(1000):
    # Set Input
    Random = np.random.randint(0, len(TrainingLabels))
    InputImage = (TrainingImages[Random] / 255) - 0.5
    RealOutput = np.zeros(10)
    RealOutput[TrainingLabels[Random]] = 1
    
    # Forward Propagation
    ConvolutionLayer1 = InputImageToConv1.ForwardProp(InputImage)
    MaxPooling1 = Conv1ToPool1.ForwardProp(ConvolutionLayer1)
    Input = MaxPooling1.flatten()
    Output = InputToHid1.ForwardProp(Input)

    # Back Propagation
    OutputError = RealOutput - Output
    InputError = InputToHid1.BackProp(OutputError) 
    MaxPooling1Error = InputError.reshape(MaxPooling1.shape)
    
    ConvolutionalError = Conv1ToPool1.BackProp(MaxPooling1Error)
    InputImageToConv1.BackProp(ConvolutionalError)
    
    bar()
  
  print(TestNetwork())