# -*- coding:utf-8 -*-
import numpy
import graph
import random
import csv
import Get_Params
import Get_Rappor
import Dependency
import os
# import copy
import time
import pickle
from copy import copy
from Estimate_Joint_Distribution import att_combin, estimate_2d, \
    list_product, rappor_list_paste, true_joint_distribution
from JunctionTree import cliques_to_locs, independe_draw, conditional_draw, independe_draw2, conditional_draw2
# from matplotlib.font_manager import pickle_dump
from collections import Counter
import Evaluation_SVM
import gc
from numpy import reshape
import JunctionTree;
import Bayes;
import RandomResponse;

Changeflag = True
ISflag = 1

file_id =7
fai_C = 0.25  # from 0.2, 0.3, 0.4, 0.5
f=0.2
bloombit = 128
hashbit = 4
dt = 0.01
readlimit = 80000
samplerate = 1  # from 0.01, 0.05, 0.1, 0.5, 1
sparse_rate = 0.0
col_list=[0,1,2,3]
if sparse_rate == 0.0:

    get_rid_flag = False
else:
    get_rid_flag = True
'''
                att_num,: attr number
                node_num: user number
                true_node_num: user number after sampling
                rowlist: attr & attr value list after 0,1,2,3...
                multilist: every user value list after 0,1,2,3..
'''
att_num, node_num, true_node_num, rowlist, multilist = Get_Params.get_file_info(file_id, readlimit,samplerate)

'''
               bit_cand_list:all attributes blooms : att1(vl...vs),att2(v1..vs),..
               bit_list: N users blooms after Rappor : att1(1..N),att2(1...N),...attrs
               bitsum_list: N users blooms real sum after formular computing  att1,att2...
              '''


bit_cand_list,bit_list,bitsum_list=Get_Rappor.RR_process(f,att_num,node_num, rowlist,multilist)
k=2;
model,model_pro=Bayes.Model_Greedy(bit_cand_list, bit_list, bitsum_list, f, att_num, k, rowlist, dt);

synthe=Bayes.Sampling(att_num,model_pro,node_num,model,bit_cand_list);

for i in range(len(synthe)):
    synthe[i] = list(map(str, synthe[i]));

file=open('test.txt','w');
for i in synthe:
    for j in i:
        file.write(j);
        file.write(',');
    file.write('\n');
file.close();


'''
Bayes.Conditionals(k,att_num,model_pro);
p_single=Get_Rappor.lasso_regression(bit_cand_list, bitsum_list)
clique=[0,2];
#prob=JunctionTree.independent_marginal(clique, bit_list, bit_cand_list, rowlist, bitsum_list, f, dt)
pro,proe=JunctionTree.getProb(clique, bit_list, bit_cand_list, rowlist, bitsum_list, f, dt)

p_single1 = [sum(eachlist) for eachlist in proe]
p_comb_T = map(list, zip(*proe))
p_single2 = [sum(eachlist) for eachlist in p_comb_T]

print('p single1:',p_single1)
print('p single2:', p_single2)

Mi = Dependency.Get_MI(p_single1, p_single2, proe)
print Mi
#print bit_cand_list
'''

bit_cand_list, bit_list, bitsum_list = Get_Rappor.rappor_process(bloombit, hashbit, f, att_num,
                                                                                 node_num, true_node_num, rowlist,
                                                                                 multilist, file_id)
'''
freqrow1:
freqnum1: every att value count
freqrate1:every att value pro
freqrow2,freqnum2,freqrate2: 2-way marginal
newlist: similar with the multilist just different in expression  att1(1..N),att2(1...N),...attrs  vs.  u1(att1,att2)...uN()
'''
freqrow1, freqnum1, freqrate1, freqrow2, freqnum2, freqrate2, newlist = Get_Params.get_static_info(
                    att_num, node_num, rowlist, multilist)
'''
TrueDepG:depdence matrix G
Truens: attr dimension
True_CorMat:mutual information matrix
'''
TrueDepG, Truens, True_CorMat, freqrate2, freqrate1 = Dependency.True_Dep_Graph(att_num, node_num,
                                                                                                true_node_num, rowlist,
                                                                                                multilist, freqrow1,
                                                                                                freqnum1, freqrate1,
                                                                                                freqrow2, freqnum2,
                                                                                                freqrate2, newlist,
                                                                                                fai_C)

TrueDG = numpy.array(TrueDepG)
# print(True_CorMat)
print(TrueDG)
TrueNS = numpy.array(Truens)
"""
True_TrG: A matrix reprsenting the TrueDG after triangulate
jtree: Numpy ndarray
    A matrix reprsenting the edges in the junction tree. jtree(i,j)=1 iff there is an edge between clique i and clique j.
root: Int
    The index of the root clique.
cliques: List   cu
    A list of lists of the indices of each clique. cliques[i] = the indices of the nodes in clique i.
B: Numpy ndarray
    A map of which clique each node appears in, B[i,j] = 1 iff node j occurs in clique i.
w: List
    The weights of the cliques, w[i] = weight of clique i.
"""
[True_TrG, True_jtree, True_root, True_cliques, True_B, True_w] = graph.graph_to_jtree(TrueDG, TrueNS)
True_TrG = numpy.array(True_TrG)
print(True_cliques)
# print(True_jtree)
print('true prob:', freqrate1)

Corr_Matrix, DepenGraph, ns, att_num, node_num, origin_node_num, row_list, multilist, bit_cand_list, bit_list, bitsum_list, p_comb_list, p_single_list = Dependency.Get_Dep_Graph(
                    att_num, node_num, true_node_num, rowlist, multilist, bloombit, hashbit, f, bit_cand_list, bit_list,
                    bitsum_list, fai_C)
DG = numpy.array(DepenGraph)
# print(DG)
DGrate = Counter(reshape(DG - TrueDG, att_num * att_num))
print(DGrate)
DGrr = DGrate[0] / (1.0 * TrueDG.size)
DGfp = DGrate[1] / (1.0 * TrueDG.size)
DGtn = DGrate[-1] / (1.0 * TrueDG.size)

NS = numpy.array(ns)
[Trigraph, jtree, root, cliques, B, w] = graph.graph_to_jtree(DG, NS)
print(cliques)
TrG = numpy.array(Trigraph)
TrGrate = Counter(reshape(TrG - True_TrG, att_num * att_num))
print(TrGrate)

p_comb_len = len(p_comb_list)
pp = [[] for i in range(p_comb_len)]
for i in range(p_comb_len):
     for p_sub in p_comb_list[i]:
         pp[i].extend(p_sub)

del freqrow1, freqrow2, TrueDepG, Truens, True_CorMat, True_jtree, True_root, True_cliques, True_B, True_w, newlist
new_data_list = [['0' for i in range(att_num)] for j in range(origin_node_num)]

cliques_list = cliques_to_locs(cliques)
print "test"
print(cliques_list)
sampled_set = set()
unsampl_list = copy(cliques_list)
while len(unsampl_list) > 0:
    get_one = unsampl_list.pop()
    print('computer new', get_one)
    new_data_list = independe_draw(ISflag, new_data_list, origin_node_num, get_one, bit_list,
                                                   bitsum_list, bit_cand_list, row_list, p_single_list, p_comb_list, f,
                                                   dt)
    sampled_set = sampled_set | set(get_one)
    visited_list = []
    while 1:
          for clique in unsampl_list:
              condition_set = set(clique) & set(sampled_set)
              visited_list.append(clique)
              if len(condition_set) > 0:
                  if set(clique).issubset(sampled_set):
                        unsampl_list.remove(clique)
                        visited_list = []
                  else:
                        unsampl_list.remove(clique)
                        visited_list = []
                        condition_list = list(condition_set)
                        condition_list.sort()
                        print('computer condition', condition_list, clique)
                        new_data_list = conditional_draw(ISflag, new_data_list, origin_node_num,
                                                                     condition_list, clique, bit_list, bitsum_list,
                                                                     bit_cand_list, row_list, p_single_list,
                                                                     p_comb_list, f, dt)
                        sampled_set = sampled_set | set(clique)
              visit = visited_list
              unsample = unsampl_list
              if visit == unsample:
                break
          visit = visited_list
          unsample = unsampl_list
          if visit == unsample:
             break

print('synthe:', new_data_list[1])
print new_data_list.__len__()




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
m3=0.0
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
m3=0.0
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

os.chdir('C:\Users\weijie\Desktop');
sys=open('sys.xlsx');
print sys;
sys.close();


