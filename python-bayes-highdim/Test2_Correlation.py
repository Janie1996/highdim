# -*- coding:utf-8 -*-
import numpy
import graph
import Get_Params
import Get_Rappor
import Dependency
from collections import Counter
from numpy import reshape
import Bayes
import Evaluation_Data

file_id=21
fai_C=0.55   #from 0.2, 0.3, 0.4, 0.5
f=0.2
bloombit=32
hashbit=4
dt=0.01
readlimit=80000
samplerate=1  # from 0.01, 0.05, 0.1, 0.5, 1

att_num ,node_num ,true_node_num ,rowlist , multilist =Get_Params.get_file_info(file_id, readlimit, samplerate)

'''
    获取数据属性真实的相关性
'''
freqrow1, freqnum1, freqrate1, freqrow2, freqnum2, freqrate2, newlist = Get_Params.get_static_info(att_num, node_num,
                                                                                                   rowlist, multilist)
TrueDepG, Truens, True_CorMat, freqrate2, freqrate1 = Dependency.True_Dep_Graph(att_num, node_num, true_node_num,
                                                                                rowlist, multilist, freqrow1, freqnum1,
                                                                                freqrate1, freqrow2, freqnum2,
                                                                                freqrate2, newlist, fai_C)
TrueDG = numpy.array(TrueDepG)
TrueNS = numpy.array(Truens)
[True_TrG, True_jtree, True_root, True_cliques, True_B, True_w] = graph.graph_to_jtree(TrueDG, TrueNS)
True_TrG = numpy.array(True_TrG)

'''
    任老师方法获取的属性间相关性
    建议：该部分的依赖关系也可以在之前的实验中DG保存下来，这里直接加载，不用重新跑一遍实验
'''
bit_cand_list, bit_list, bitsum_list= Get_Rappor.rappor_process(bloombit, hashbit, f, att_num, node_num, true_node_num,
                                                                 rowlist, multilist, file_id)

Corr_Matrix, DepenGraph, ns, att_num, node_num, origin_node_num, row_list, multilist, bit_cand_list, bit_list, bitsum_list, p_comb_list, p_single_list = Dependency.Get_Dep_Graph(
    att_num, node_num, true_node_num, rowlist, multilist, bloombit, hashbit, f, bit_cand_list, bit_list, bitsum_list,
    fai_C)
DG = numpy.array(DepenGraph)
[TrG, jtree, root, cliques, B, w] = graph.graph_to_jtree(DG, TrueNS)

#通过读取
modelPath='G:\python-bayes-highdim\output\model'
DG1=Evaluation_Data.loadModel(modelPath+"-testLopub");

'''
    我们bayes方法得到的属性间相关性
'''
modelPath='G:\python-bayes-highdim\output\model'
model_test = Evaluation_Data.loadModel(modelPath+"-testSyn");
BayesGraph = Bayes.getDepenGraph(model_test, att_num);
BayesDG = numpy.array(BayesGraph)


DGrate = Counter(reshape(DG - TrueDG, att_num * att_num))
#print('True Cliques', True_cliques)
#print('Cliques:', cliques)
#print(DGrate)
DGrr = DGrate[0] / (1.0 * TrueDG.size)
DGfp = DGrate[1] / (1.0 * TrueDG.size)  #false positive
DGtn = DGrate[-1] / (1.0 * TrueDG.size) #true negative


DGrate1 = Counter(reshape(BayesDG - TrueDG, att_num * att_num))
print(DGrate1)
DGrr1 = DGrate1[0] / (1.0 * TrueDG.size)
DGfp1 = DGrate1[1] / (1.0 * TrueDG.size)
DGtn1 = DGrate1[-1] / (1.0 * TrueDG.size)

print "t"