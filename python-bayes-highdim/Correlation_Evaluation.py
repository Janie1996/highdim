import numpy
import graph
import random
import csv
import Get_Params
import Get_Rappor
import Dependency
import os
import time
import pickle
from copy import copy
from Estimate_Joint_Distribution import att_combin, estimate_2d,\
    list_product, rappor_list_paste, true_joint_distribution
from JunctionTree import cliques_to_locs,independe_draw,conditional_draw,independe_draw2,conditional_draw2
from collections import Counter
import Evaluation_SVM
import gc
from numpy import reshape
import Bayes
import Evaluation_Data

##########################################################################################################################################################################################################
##########################################################################################################################################################################################################
##########################################################################################################################################################################################################        
Changeflag=True
ISflag=1

file_id=21
fai_C=0.55   #from 0.2, 0.3, 0.4, 0.5

bloombit=32
hashbit=4
dt=0.01
readlimit=80000
samplerate=1  # from 0.01, 0.05, 0.1, 0.5, 1
sparse_rate=0.0
if sparse_rate==0.0:
    get_rid_flag=False
else:
    get_rid_flag=True
for file_id in [21]:
    if file_id==4:
        fai_list=[0.2]
        col_list=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    if file_id==2:
        bloombit=128
        hashbit=4
        fai_list=[0.3]
        col_list=[9,14]
        #col_list=[0,1,2,3,4,5,6,7,8,10,11,12,13]
    if file_id==3:
        bloombit=32
        hashbit=4
        fai_list=[0.2]
        col_list=[2,9,22,23]
    for fai_C in [0.55]:
        
        for f in [0.2]:
            if Changeflag :

                att_num,node_num,true_node_num,rowlist,multilist=Get_Params.get_file_info(file_id, readlimit, samplerate)
                bit_cand_list, bit_list, bitsum_list=Get_Rappor.rappor_process(bloombit, hashbit, f, att_num, node_num, true_node_num, rowlist, multilist, file_id)

                freqrow1,freqnum1,freqrate1,freqrow2,freqnum2,freqrate2,newlist=Get_Params.get_static_info(att_num, node_num, rowlist, multilist)

                TrueDepG,Truens,True_CorMat,freqrate2,freqrate1=Dependency.True_Dep_Graph(att_num,node_num,true_node_num,rowlist,multilist,freqrow1,freqnum1,freqrate1,freqrow2,freqnum2,freqrate2,newlist,fai_C)
                TrueDG=numpy.array(TrueDepG)

                TrueNS=numpy.array(Truens)
                [True_TrG,True_jtree, True_root, True_cliques, True_B, True_w]=graph.graph_to_jtree(TrueDG,TrueNS)
                True_TrG=numpy.array(True_TrG)

                Corr_Matrix,DepenGraph,ns,att_num,node_num,origin_node_num,row_list,multilist,bit_cand_list, bit_list,bitsum_list,p_comb_list,p_single_list=Dependency.Get_Dep_Graph(att_num,node_num,true_node_num,rowlist,multilist,bloombit, hashbit, f,bit_cand_list,bit_list,bitsum_list,fai_C)
                DG=numpy.array(DepenGraph)
                [TrG,jtree, root, cliques, B, w]=graph.graph_to_jtree(DG,TrueNS)
                model_test = Evaluation_Data.loadModel("G:\Python");
                #model_test = Evaluation_Data.Load_Model('G:\wj');

                BayesGraph = Bayes.getDepenGraph(model_test, att_num);
                BayesDG=numpy.array(BayesGraph)


                #print(DG)
                DGrate=Counter(reshape(DG-TrueDG,att_num*att_num))
                print('True Cliques',True_cliques)
                print('Cliques:',cliques)
                print(DGrate)
                DGrr=DGrate[0]/(1.0*TrueDG.size)
                DGfp=DGrate[1]/(1.0*TrueDG.size)
                DGtn=DGrate[-1]/(1.0*TrueDG.size)
                
                write_list=[[fai_C,f,DGrr,DGfp,DGtn,sparse_rate,samplerate]]
                print(write_list)

                DGrate1=Counter(reshape(BayesDG-TrueDG,att_num*att_num))
                print(DGrate1)
                DGrr1=DGrate1[0]/(1.0*TrueDG.size)
                DGfp1=DGrate1[1]/(1.0*TrueDG.size)
                DGtn1=DGrate1[-1]/(1.0*TrueDG.size)
                print 't'