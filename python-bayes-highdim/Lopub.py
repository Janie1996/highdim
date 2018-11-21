# -*- coding:utf-8 -*-
import numpy
import graph
import random

import Get_Params
import Get_Rappor
import Dependency

from copy import copy

from JunctionTree import cliques_to_locs, independe_draw, conditional_draw, independe_draw2, conditional_draw2
from collections import Counter
import Evaluation_SVM

from numpy import reshape

import Bayes;

import Evaluation_Data;

Changeflag = True
ISflag = 1

file_id =21
fai_C = 0.25  # from 0.2, 0.3, 0.4, 0.5
f=0.2
bloombit = 128
hashbit = 4
dt = 0.01
readlimit = 80000
samplerate = 1  # from 0.01, 0.05, 0.1, 0.5, 1
sparse_rate = 0.0
col_list=[0,1,2,3]

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


# 将合成数据集保存到本地，便于后续对比实验使用
filePath='G:\python-bayes-highdim\output\data'
Evaluation_Data.saveData(filePath+"-testLopub.txt",new_data_list);

# 将训练的模型保存到本地，便于后续对比实验使用，可以只保存model、也可以保存model_pro
modelPath='G:\python-bayes-highdim\output\model'
Evaluation_Data.SaveModel(DG,modelPath+"-testLopub");




