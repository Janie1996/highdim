# -*- coding:utf-8 -*-
import Get_Params
import numpy
import scipy
import copy
import os
import time
import pickle
import csv
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.linear_model.bayes import BayesianRidge
import random
import math

def rand_pick(seq , probabilities):
    x = random.uniform(0 ,1)
    cumprob = 0.0
    for item , item_pro in zip(seq , probabilities):
        cumprob += item_pro
        if x < cumprob:
            break
    return item

#使用属性值个二进制位进行表示，随机化应答保护隐私预算
def RR_process(epsilon,num_att,num_node,list_att,list_data):

    f = math.exp(epsilon) / (math.exp(epsilon) + 1);
    # 各个属性值的二进制串
    bit_cand_list=[0 for k in range(num_att)];
    for i in range(num_att):
        x=[[0 for k in range(len(list_att[i]))] for j in range(len(list_att[i]))];
        for j in range(len(list_att[i])):
            y=[0 for k in range(len(list_att[i]))]
            y[j]=1;
            x[j]=y;
        #print x
        bit_cand_list[i]=x;

    bitsum_list=[0 for i in range(num_att)];
    for i in range(num_att):
        x=[0 for k in range(len(list_att[i]))];
        #print x
        bitsum_list[i]=x;


    bit_list=[0 for i in range(num_node)];

    #每个用户数据二进制表示
    for i in range(num_node):
        x=[0 for j in range(num_att)];
        for j in range(num_att):
            y=bit_cand_list[j][int(list_data[i][j])];   #真实值二进制表示
            z=[0 for k in range(len(y))]
            for k in range(len(y)):               #随机化应答后
                #z[k]=rand_pick([y[k],1-y[k]],[f,1-f]);
                z[k]=rand_pick([y[k],1-y[k]],[1-epsilon/2,epsilon/2]);
            #x[j]=y;
            x[j]=z;
        bit_list[i]=x;

    for i in range(num_node):
        for j in range(num_att):
            bitsum_list[j]=list(map(lambda x: x[0]+x[1], zip(bitsum_list[j], bit_list[i][j])))

    bit_list = map(list, zip(*bit_list))
    #真实sum值
    #随机化应答epsilon
    '''
    for i in range(len(bitsum_list)):
        x=[0.0 for j in range(len(bitsum_list[i]))]
        for j in range(len(bitsum_list[i])):
            x[j] = float(bitsum_list[i][j]) / num_node;
            x[j] = ((math.exp(epsilon)+1)/(math.exp(epsilon)-1)*x[j]-1.0/(math.exp(epsilon)-1));
        y=numpy.array(x);
        y[y<0]=0;
        for j in range(len(y)):
            x[j]=float(y[j])/numpy.sum(y);
            x[j]=int(x[j]*num_node);
        bitsum_list[i] = x;
    '''
    #rappor翻转f
    #tempbitsum_list=(numpy.array(bitsum_list)-(0.5*epsilon)*num_node)/(1.0-epsilon)   # through the formula to get the real sum
    #bitsum_list=tempbitsum_list.tolist()
    for i in range(len(bitsum_list)):
        x=[0.0 for j in range(len(bitsum_list[i]))]
        for j in range(len(bitsum_list[i])):
            x[j]=(bitsum_list[i][j]-(epsilon*0.5*num_node))/(1-epsilon);
        bitsum_list[i]=x;

    return bit_cand_list,bit_list,bitsum_list


def rappor_process(num_bloombits,num_hash,f,num_att,num_node,origin_node_num,list_att,list_data,file_id=1):

    #freqrow1,freqnum1,freqrate1,freqrow2,freqnum2,freqrate2,newlist=Get_Params.get_static_info(num_att, num_node, list_att, list_data)
    print('Generating RAPPOR.')
    # init
    bit_list=[[[0 for i in range(num_bloombits)]for j in range(num_att)] for k in range(num_node)]   #N users blooms
    #print bit_list.__len__()
    bit_cand_list=[[[0 for i in range(num_bloombits)]for j in range(len(list_att[k]))]for k in range(num_att)]  #all attributes blooms
    #print bit_cand_list.__len__()
    bitsum_list=[[0 for i in range(num_bloombits)]for j in range(num_att)]
    #print bitsum_list

####N users blooms after rappor
    for i in range(num_node):
        for j in range(num_att):
            e=Get_Params.set_rappor_params(num_bloombits, num_hash,num_att,f)  #init the rappor
            bit_list[i][j]=Get_Params.get_B(list_data[i][j], e)
            #print(bit_list[i][j])
    curr_timeb=time.time()
    #print bit_list
####sum blooms each bit
    for i in range(num_node):
        for j in range(num_att):
            bitsum_list[j]=list(map(lambda x: x[0]+x[1], zip(bitsum_list[j], bit_list[i][j])))
    #print bitsum_list
    curr_timee=time.time()
    last_time=curr_timee-curr_timeb
    bit_list=map(list, zip(*bit_list))   # trans everynode into att
    #print('count time:',last_time)
    #os.chdir('G:\python_highdim\output')
    #with open('file-'+str(file_id)+'-marginal.csv','a') as fid:
     #               fid_csv = csv.writer(fid)
      #              fid_csv.writerows([[last_time]])
    #print('origin:',bitsum_list)
            
    for i in range(num_att):
        for j in range(len(list_att[i])):
            e=Get_Params.set_rappor_params(num_bloombits, num_hash,num_att,f)
            bit_cand_list[i][j]=Get_Params.get_S(list_att[i][j],e)

    tempbitsum_list=(numpy.array(bitsum_list)-(0.5*f)*num_node)/(1.0-f)   # through the formula to get the real sum
    #print(tempbitsum_list[1])
    bitsum_list=tempbitsum_list.tolist()
    #print(bitsum_list)      
    return bit_cand_list, bit_list, bitsum_list

#######################################################################################################################################################################################


#att_num, node_num, true_node_num, rowlist, multilist = Get_Params.get_file_info(5, 3000, 1)
#print rowlist
#print multilist
#bit_cand_list, bit_list, bitsum_list =rappor_process(10, 2,0.1,  att_num, node_num, true_node_num, rowlist, multilist, 4)


#######################################################################################################################################################################################
def lasso_regression2(bit_cand_list,bitsum_list):
    #################
    ################### this function is used for all the data, no
    len_att=len(bit_cand_list)
    lasso_cf=[] 
    
    
    #nz_sum_list=[]
    
    for i in range(len_att):
        #print(bit_cand_list[i],bitsum_list[i])
        
        x=map(list, zip(*bit_cand_list[i]))
        y=bitsum_list[i]
        
        
        #print(x,y)
        #clf=LinearRegression(fit_intercept=False,copy_X=True,normalize=True)
        clf = Lasso(alpha=0.5)
        m=clf.fit(x, y)
        coef=clf.coef_
        #print(coef)
        len_cand=len(coef)
        cf=[0.0 for k in range(len_cand)]
        nz_loc=[]
        nz_cand_list=[]
        for j in range(len_cand):
            if coef[j]>=10:    ##############################################  attentiion!!
                nz_loc.append(j)
                nz_cand_list.append(bit_cand_list[i][j])
                #nz_sum_list.append(bitsum_list[i][j])
        #clf2=LinearRegression(fit_intercept=False,copy_X=True,normalize=True)
        clf2=Lasso(alpha=0.5)
        
        #clf2=Lasso(alpha=1.0)
        #print(nz_cand_list,y)
        x2=map(list,zip(*nz_cand_list))
        n=clf2.fit(x2,y)
        coef2=clf2.coef_
        #print('coef2',coef2)
        
        for j in range(len(coef2)):
            #print('loc',nz_loc[j],coef2[j])
            cf[nz_loc[j]]=coef2[j]
            
    
        #print(coef)
        #index=coef.nonzero()
        ratio=cf/(sum(cf))
        lasso_cf.append(ratio.tolist())
        #print(clf.coef_)
         
    return lasso_cf
def lasso_regression(bit_cand_list,bitsum_list):
    #################
    ################### this function is used for all the data, no
    #print(bitsum_list[0])
    #print(bitsum_list[0:32])
    lasso_cf=[] 
    for i in range(len(bit_cand_list)):
        #print(bit_cand_list[i],bitsum_list[i])
        x=map(list, zip(*bit_cand_list[i]))
        y=bitsum_list[i]
        #clf=LinearRegression(fit_intercept=False,copy_X=True)
        clf = Lasso(alpha=0.5)
        #clf=BayesianRidge()
        #clf=ElasticNet(alpha=0.1, l1_ratio=2.0)
        m=clf.fit(x, y)
        coef=clf.coef_
        ratio=coef/(sum(coef))
        lasso_cf.append(ratio.tolist())
        #print(clf.coef_)
         
    return lasso_cf

def Get_rid_sparse2(file_id,readlimit,samplerate,bloombit,hashbit,f,sparse_rate,get_rid_flag=True): 
#def Get_rid_sparse(bit_cand_list,bitsum_list,att_num,node_num,true_node_num,rowlist,multilist,sparse_rate): 
    
    att_num,node_num,true_node_num,rowlist,multilist=Get_Params.get_file_info(file_id,readlimit,samplerate)
    bit_cand_list,bit_list,bitsum_list=rappor_process(bloombit, hashbit, f,att_num,node_num,true_node_num,rowlist,multilist,file_id)
    
    #print(rowlist)
            
    if get_rid_flag==True :  
        p_single=lasso_regression(bit_cand_list, bitsum_list)
        #print(p_single)
        for i in range(att_num):
            lengi=len(p_single[i])
            rowcopy=copy.copy(rowlist[i])
            for j in range(lengi):
                if p_single[i][j]<sparse_rate:
                    rowcopy.remove(rowlist[i][j])
                    for k in range(node_num):
                        if multilist[k][i]==rowlist[i][j]:
                            multilist[k][i]='a'
            rowlist[i]=rowcopy
            if len(rowlist[i])<lengi:
                rowlist[i].append('a')
        #print(multilist)
        #print(rowlist)
        bit_cand_list3,bit_list3,bitsum_list3=rappor_process(bloombit, hashbit, f,att_num,node_num,true_node_num,rowlist,multilist,file_id)
    else:
        bit_cand_list3=bit_cand_list
        bit_list3=bit_list
        bitsum_list3=bitsum_list
        
    #print(rowlist)
    return att_num,node_num,true_node_num,rowlist,multilist,bit_cand_list3,bit_list3,bitsum_list3

def Get_rid_sparse(file_id,readlimit,samplerate,bloombit,hashbit,f,sparse_rate,get_rid_flag=False):   ##filtering sparse items with true probability
#def Get_rid_sparse(bit_cand_list,bitsum_list,att_num,node_num,true_node_num,rowlist,multilist,sparse_rate): 
    
    att_num,node_num,true_node_num,rowlist,multilist=Get_Params.get_file_info(file_id,readlimit,samplerate)
    #bit_cand_list,bit_list,bitsum_list=rappor_process(bloombit, hashbit, f,att_num,node_num,true_node_num,rowlist,multilist)
    
    #print(rowlist)
            
    if get_rid_flag==True :  
        print('filter the sparse items')
        #p_single=lasso_regression(bit_cand_list, bitsum_list)
        freqrow1,freqnum1,freqrate1,freqrow2,freqnum2,freqrate2,newlist=Get_Params.get_static_info(att_num,node_num,rowlist,multilist)
        p_single=freqrate1
        print(p_single)
        for i in range(att_num):
            lengi=len(p_single[i])
            rowcopy=copy.copy(rowlist[i])
            for j in range(lengi):
                if p_single[i][j]<sparse_rate:
                    rowcopy.remove(rowlist[i][j])
                    for k in range(node_num):
                        if multilist[k][i]==rowlist[i][j]:
                            multilist[k][i]='a'
            rowlist[i]=rowcopy
            if len(rowlist[i])<lengi:
                rowlist[i].append('a')
        #print(multilist)
        #print(rowlist)
    bit_cand_list3,bit_list3,bitsum_list3=rappor_process(bloombit, hashbit, f,att_num,node_num,true_node_num,rowlist,multilist,file_id)
#     else:
#         bit_cand_list3=bit_cand_list
#         bit_list3=bit_list
#         bitsum_list3=bitsum_list
        
    #print(rowlist)
    return att_num,node_num,true_node_num,rowlist,multilist,bit_cand_list3,bit_list3,bitsum_list3
                      
########################################################################################################################################################################################    









