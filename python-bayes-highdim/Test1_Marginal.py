# -*- coding:utf-8 -*-
import Get_Params
import Get_Rappor
import numpy
import itertools
import random
from JunctionTree import independent_marginal2, independent_marginal, independent_marginal3
from Estimate_Joint_Distribution import true_joint_distribution, unfold_pro_list


#获得w-way边缘组合情况
def get_clique(range_size, clique_size, sample_size):
    ini_list2 = list(itertools.combinations(range(range_size), clique_size))
    zzz = [list(eachtuple) for eachtuple in ini_list2]
    random.seed(15)
    zlist = random.sample(zzz, sample_size)
    return zlist

#L2距离
def l2_err(pro, true_pro):
    leng = len(pro)
    delta_pro = numpy.array(pro) - numpy.array(true_pro)
    return 1.0 * numpy.sqrt(numpy.sum(numpy.power(delta_pro, 2)) / (1.0))


# 均方差距离AVD，真实联合概率估计与实验测量概率估计间的误差
def get_avd(pro, true_pro):
    leng = len(pro)
    delta_pro = numpy.array(pro) - numpy.array(true_pro)
    #     max_delta=max(numpy.abs(delta_pro))
    #     return max_delta
    abs_delta = numpy.abs(delta_pro)
    return numpy.sum(abs_delta) / 2.0


def cos(vector1, vector2):
    dot_product = 0.0;
    normA = 0.0;
    normB = 0.0;
    for a, b in zip(vector1, vector2):
        dot_product += a * b
        normA += a ** 2
        normB += b ** 2
    if normA == 0.0 or normB == 0.0:
        return None
    else:
        return dot_product / ((normA * normB) ** 0.5)

def get_max(pro, true_pro):
    max1 = max(pro)
    max2 = max(true_pro)

    return abs(max1 - max2)

def get_var(pro, true_pro):
    return numpy.var(numpy.array(pro) - numpy.array(true_pro))

f = 0.2  # from 0.1, 0.2, 0.3, 0.4, 0.5  *********
bloombit = 32
hashbit = 16
dt = 0.01
readlimit = 60000
samplerate = 1
sparse_rate = 0.0
listtt = [10];
file_id1 = 100;
file_id2=101;

#当前代码只写了AVD的对比实验，没有L2距离的，只需要修改调用函数
'''
      第一部分对比实验
      比较真实的a-way边缘分布与合成数据集的边缘分布之间的差异
      注意：该部分的数据类型为dat
'''
for file_id in listtt:

    if samplerate != 2:
        att_num2, node_num2, true_node_num2, rowlist2, multilist2 = Get_Params.get_file_info(file_id, readlimit,
                                                                                             samplerate)

        att_num1, node_num1, true_node_num1, rowlist1, multilist1 = Get_Params.get_file_info(file_id1, readlimit,
                                                                                             samplerate)

        att_num3, node_num3, true_node_num3, rowlist3, multilist3 = Get_Params.get_file_info(file_id2, readlimit,
                                                                                             samplerate)
        att1_clique = get_clique(att_num2, 2, 5)
        att2_clique = get_clique(att_num2, 3, 3)

        if file_id == 4:
            bloombit = 32
            hashbit = 4
            samplerate = 0.1
            # cluster_list=[att2_clique,att5_clique]
            cluster_list = [att1_clique, att2_clique]
        else:
            bloombit = 128
            hashbit = 4
            samplerate = 0.02
            # cluster_list=[att2_clique,att3_clique]
            cluster_list = [att1_clique, att2_clique]
        for f in [0.2]:

            att_num2, node_num2, true_node_num2, rowlist_sparse, multilist_sparse, bit_cand_list3, bit_list3, bitsum_list3 = Get_Rappor.Get_rid_sparse(
                file_id, readlimit, samplerate, bloombit, hashbit, f, sparse_rate)

            freqrow1, freqnum1, freqrate1, freqrow2, freqnum2, freqrate2, newlist = Get_Params.get_static_info(att_num2,
                                                                                                               node_num2,
                                                                                                               rowlist_sparse,
                                                                                                               multilist_sparse)

            if file_id != 5:

                for each_k in cluster_list:
                    lenk = len(each_k[0])
                    sum_err1 = 0.0
                    sum_err2 = 0.0
                    sum_err3 = 0.0

                    i = 0

                    err_list1 = []
                    err_list2 = []
                    err_list3 = []

                    for eachclique in each_k:
                        #真实数据分布情况
                        true_list, true_pro = true_joint_distribution(multilist2, rowlist2, eachclique)
                        print('true:', true_pro)
                        #bayes方法合成数据集的分布情况
                        synthe_list, synthe_pro = true_joint_distribution(multilist1, rowlist1, eachclique)
                        #Lopub方法合成数据集的分布情况
                        em_list, em_pro = true_joint_distribution(multilist3, rowlist3, eachclique)
                        #直接根据随机化翻转后数据估计得到
                        some_list, pro1 = independent_marginal(eachclique, bit_list3, bit_cand_list3, rowlist2,
                                                               bitsum_list3, f, dt)

                        print ('synthe:', synthe_pro)
                        print('esti1:', pro1)

                        i += 1

                        err1 = get_avd(pro1, true_pro)
                        err2 = get_avd(synthe_pro, true_pro)
                        err3 = get_avd(em_pro,true_pro)

                        sum_err1 += err1
                        sum_err2 += err2
                        sum_err3 += err3

                        print(i, err1, err2, err3,eachclique)
                        # print(err_list1)

                    mean_err1 = 1.0 * sum_err1 / len(each_k)
                    mean_err2 = 1.0 * sum_err2 / len(each_k)
                    mean_err3 = 1.0 * sum_err3 / len(each_k)
                    print(lenk, mean_err1, mean_err2,mean_err3)
                    write_list = [[f, samplerate, lenk, mean_err1, mean_err2, sparse_rate, bloombit, hashbit]]
                    print(write_list)















