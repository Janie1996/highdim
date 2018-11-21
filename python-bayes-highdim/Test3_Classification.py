# -*- coding:utf-8 -*-
import random
import Get_Params
import Evaluation_SVM
import Evaluation_Data;
import numpy
#初始化
file_id =21   #文件名
f=0.2
readlimit = 80000
samplerate = 1  # 采样概率
col_list=[0,1,2,3]
filePath='G:\python-bayes-highdim\output\data'
bayesFile='-testSyn.txt'        #该部分的文件就是实验直接保存的TXT文件
lopubFile='-testLopub.txt'

#真实数据集
att_num, node_num, true_node_num, rowlist, multilist = Get_Params.get_file_info(file_id, readlimit,samplerate)
#加载我们Bayes方法的合成数据集
synthe=Evaluation_Data.readData(filePath+bayesFile,att_num,node_num);
#加载任老师Lopub方法合成的数据集
new_data_list=Evaluation_Data.readData(filePath+lopubFile,att_num,node_num);

'''
   第三部分对比实验
   1. SVM分类
   2. RF分类
'''
n = int(samplerate * node_num)
new_sample_list = []
sample_list = []
our_list=[]
random.seed(5)
sample_order = random.sample(range(node_num), n)
for i in sample_order:
      new_sample_list.append(new_data_list[i])
      sample_list.append(multilist[i])
      our_list.append(synthe[i])


ratio = 0.7
loop_time = 1
m1 = 0.0
m2 = 0.0
m3 = 0.0
leng = len(col_list)
col_all = range(att_num)
for col in col_list:
      train_x, train_y, test_x, test_y, single_err = Evaluation_SVM.Data_construct(sample_list, col,
                                                                                                 ratio)
      train_x2, train_y2, test_x2, test_y2, single_err2 = Evaluation_SVM.Data_construct(new_sample_list,
                                                                                                      col, ratio)
      train_x3, train_y3, test_x3, test_y3, single_err3 = Evaluation_SVM.Data_construct(our_list,
                                                                                                      col, ratio)
      t1 = Evaluation_SVM.SVM_ratio(train_x, train_y, test_x, test_y, loop_time, 'SVM')
      m1 = m1 + t1
      t2 = Evaluation_SVM.SVM_ratio(train_x2, train_y2, test_x, test_y, loop_time, 'SVM')
      m2 = m2 + t2
      t3 = Evaluation_SVM.SVM_ratio(train_x3, train_y3, test_x, test_y, loop_time, 'SVM')
      m3 = m3 + t3
      print (' ')
      print('col:', col, ' ', t1, t2,t3)
svm_ratio1 = m1 / leng
svm_ratio2 = m2 / leng
svm_ratio3 = m3 / leng
print ('file:', file_id, 'f:', f, 'SVM:', svm_ratio1, svm_ratio2, svm_ratio3)
m1 = 0.0
m2 = 0.0
m3 = 0.0
for col in col_all:
     train_x, train_y, test_x, test_y, single_err = Evaluation_SVM.Data_construct(sample_list, col,
                                                                                                 ratio)
     train_x2, train_y2, test_x2, test_y2, single_err2 = Evaluation_SVM.Data_construct(new_sample_list,
                                                                                                      col, ratio)
     train_x3, train_y3, test_x3, test_y3, single_err3 = Evaluation_SVM.Data_construct(our_list,
                                                                                                      col, ratio)
     t1 = Evaluation_SVM.SVM_ratio(train_x, train_y, test_x, test_y, loop_time, 'RF')
     m1 = m1 + t1
     t2 = Evaluation_SVM.SVM_ratio(train_x2, train_y2, test_x, test_y, loop_time, 'RF')
     m2 = m2 + t2
     t3 = Evaluation_SVM.SVM_ratio(train_x3, train_y3, test_x, test_y, loop_time, 'RF')
     m3 = m3 + t3
     print (' ')
     print('col:', col, ' ', t1, t2, t3)

rf_ratio1 = m1 / len(col_all)
rf_ratio2 = m2 / len(col_all)
rf_ratio3 = m3 / len(col_all)
print ('file:', file_id, 'f:', f, 'RF:', rf_ratio1, rf_ratio2, rf_ratio3)




