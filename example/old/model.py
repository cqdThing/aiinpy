import numpy as np
import sys, os, time, json, random, datetime
import wandb

class model:
  def __init__(self, inshape, outshape, model, wandbproject=None, usecache=False, cacheexpire=10):
    self.inshape = inshape = inshape if isinstance(inshape, tuple) else tuple([inshape])
    self.outshape = outshape if isinstance(outshape, tuple) else tuple([outshape])
    self.model = model
    self.wandbproject = wandbproject

    for i in self.model:
      inshape = i.modelinit(inshape)
    
    if wandbproject is not None:
      wandb.init(project=wandbproject)

    if usecache and os.path.isdir('aiinpy'):
      pass # add code for retreiving cache
      
    runname = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))
    if not os.path.isdir('aiinpy'):
      os.mkdir('aiinpy')
    os.mkdir('aiinpy/' + runname)
    printmodel = [p.__repr__() for p in self.model]
    json.dump({'name' : runname, 'time' : str(datetime.datetime.now()), 'model' : printmodel}, open('aiinpy/' + runname + '/metadata.json', 'w'), indent=2)

  def forward(self, input):
    for i in range(len(self.model)):
      input = self.model[i].forward(input)
    return input

  def backward(self, outError):
    for i in reversed(range(len(self.model))):
      outError = self.model[i].backward(outError)
    return outError

  def train(self, data, numofgen):
    # data preprocessing: tuple of (indata, outdata) with indata and outdata as numpy array
    data = list(data) if type(data) == tuple else data
    data[0] = np.reshape(data[0], (data[0].shape[0], 1)) if len(data[0].shape) == 1 else data[0]
    data[1] = np.reshape(data[1], (data[1].shape[0], 1)) if len(data[1].shape) == 1 else data[1]

    NumOfData = (set(self.inshape) ^ set(data[0].shape)).pop()
    if data[0].shape.index(NumOfData) != 0:
      x = list(range(0, len(data[0].shape)))
      x.pop(data[0].shape.index(NumOfData))
      data[0] = np.transpose(data[0], tuple([data[0].shape.index(NumOfData)]) + tuple(x))
    if data[1].shape.index(NumOfData) != 0:
      x = list(range(0, len(data[1].shape)))
      x.pop(data[1].shape.index(NumOfData))
      data[1] = np.transpose(data[1], tuple([data[1].shape.index(NumOfData)]) + tuple(x))

    trainerror = []

    # Training, with wandb
    if self.wandbproject is not None:
      for gen in range(numofgen):
        random = np.random.randint(0, NumOfData)
        input = data[0][random]
        for i in range(len(self.model)):
          input = self.model[i].forward(input)

        outerror = data[1][random] - input
        wandb.log({'train error': np.sum(abs(outerror))})
        for i in reversed(range(len(self.model))):
          outerror = self.model[i].backward(outerror)
        sys.stdout.write('\r' + 'training: ' + str(gen + 1) + '/' + str(numofgen))
    else:
      # Training, without wandb
      for gen in range(numofgen):
        random = np.random.randint(0, NumOfData)
        input = data[0][random]
        for i in range(len(self.model)):
          input = self.model[i].forward(input)

        outerror = data[1][random] - input
        trainerror.append(np.sum(abs(outerror)))
        for i in reversed(range(len(self.model))):
          outerror = self.model[i].backward(outerror)
        sys.stdout.write('\r' + 'training: ' + str(gen + 1) + '/' + str(numofgen))
    
    print('')

    return trainerror

  def test(self, data):
    # data preprocessing: tuple of (indata, outdata) with indata and outdata as numpy array
    data = list(data) if type(data) == tuple else data
    data[0] = np.reshape(data[0], (data[0].shape[0], 1)) if len(data[0].shape) == 1 else data[0]
    data[1] = np.reshape(data[1], (data[1].shape[0], 1)) if len(data[1].shape) == 1 else data[1]

    NumOfData = (set(self.inshape) ^ set(data[0].shape)).pop()
    if data[0].shape.index(NumOfData) != 0:
      x = list(range(0, len(data[0].shape)))
      x.pop(data[0].shape.index(NumOfData))
      data[0] = np.transpose(data[0], tuple([data[0].shape.index(NumOfData)]) + tuple(x))
    if data[1].shape.index(NumOfData) != 0:
      x = list(range(0, len(data[1].shape)))
      x.pop(data[1].shape.index(NumOfData))
      data[1] = np.transpose(data[1], tuple([data[1].shape.index(NumOfData)]) + tuple(x))

    # Testing
    testcorrect = 0
    for gen in range(NumOfData):
      input = data[0][gen]
      for i in range(len(self.model)):
        input = self.model[i].forward(input)

      testcorrect += 1 if np.argmax(input) == np.argmax(data[1][gen]) else 0
      sys.stdout.write('\r' + 'testing: ' + str(gen + 1) + '/' + str(NumOfData))

    print('')
    
    self.testaccuracy = testcorrect / NumOfData
    if self.wandbproject is not None:
      wandb.log({'test accuracy': self.testaccuracy})
    return self.testaccuracy

  def use(self, indata):
    indata = np.reshape(indata, (indata.shape[0], 1)) if len(indata.shape) == 1 else indata
    NumOfData = (set(self.inshape) ^ set(indata.shape)).pop()
    if indata.shape.index(NumOfData) != 0:
      x = list(range(0, len(indata.shape)))
      x.pop(indata.shape.index(NumOfData))
      indata = np.transpose(indata, tuple([indata.shape.index(NumOfData)]) + tuple(x))

    outdata = np.zeros(indata.shape)
    for gen in range (NumOfData):
      input = indata[gen]
      for i in range(len(self.model)):
        input = self.model[i].forward(input)
      outdata[gen] = input
    return outdata