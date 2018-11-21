# -*- coding:utf-8 -*-
import pickle

#保存数据
def saveData(filename,data):
    file = open(filename, 'w');
    for i in data:
        for j in i:
            file.write(j);
            file.write(',');
        file.write('\n');
    file.close();

#读取数据
def readData(filename,num_att,num_node):
    file = open(filename);
    sys = [[0 for i in range(num_att)] for j in range(num_node)]
    i = 0
    while 1:
        line = file.readline()[:-2]  # read a line in datafile
        lineData = line.strip().split(',');
        if not line:
            break
        sys[i] = lineData;
        i = i + 1;
    file.close();
    return sys;


def SaveModel(model, modelPath):
    """
    使用pickle保存训练好的模型
    """
    with open(modelPath, "wb") as f:
        pickle.dump(model, f)
    return model

def loadModel(modelPath):
    """
    使用pickle读取已有的模型
    """
    model = pickle.load(open(modelPath, "rb"))
    return model
