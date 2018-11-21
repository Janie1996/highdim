# -*- coding:utf-8 -*-

import Get_Params
import Get_Rappor
import Bayes;
import Evaluation_Data;

'''
    该文件是local_bayes的整个算法流程
    主要包含四个部分：
    1. 原始数据二进制处理，随机化翻转保护隐私
    2. 建立贝叶斯网络
    3. 计算条件分布
    4. 合成数据集发布
'''

#初始化
file_id =21   #文件名
f=0.2        #翻转概率
k=2          #贝叶斯网络最大父节点个数
dt=0.01
readlimit = 80000
samplerate = 1  # 采样概率

'''
                att_num,: attr number
                node_num: user number
                true_node_num: user number after sampling
                rowlist: attr & attr value list after 0,1,2,3...
                multilist: every user value list after 0,1,2,3..
                读取原始数据信息，将数据属性值转换为0、1、2等表示
'''
att_num, node_num, true_node_num, rowlist, multilist = Get_Params.get_file_info(file_id, readlimit,samplerate)

'''
               bit_cand_list:all attributes blooms : att1(vl...vs),att2(v1..vs),..
               bit_list: N users blooms after Rappor : att1(1..N),att2(1...N),...attrs
               bitsum_list: N users blooms real sum after formular computing  att1,att2...
               1. 将数据表示为二进制形式
               2. 进行随机化应答，实现本地隐私保护
'''

bit_cand_list,bit_list,bitsum_list=Get_Rappor.RR_process(f,att_num,node_num, rowlist,multilist)

'''
             model:每一个属性节点与其父节点对应关系，即AP对
             model_pro:model+对应的联合概率分布值
             建立贝叶斯网络
'''
model,model_pro=Bayes.Model_Greedy(bit_cand_list, bit_list, bitsum_list, f, att_num, k, rowlist, dt);

'''
            synthe:最终合成的数据集
            根据属性间依赖关系，产生最终的合成数据集发布
            
'''
synthe=Bayes.Sampling(att_num,model_pro,node_num,model,bit_cand_list);


for i in range(len(synthe)):
    synthe[i] = list(map(str, synthe[i]));

# 将合成数据集保存到本地，便于后续对比实验使用
filePath='G:\python-bayes-highdim\output\data'
Evaluation_Data.saveData(filePath+"-testSyn.txt",synthe);

# 将训练的模型保存到本地，便于后续对比实验使用，可以只保存model、也可以保存model_pro
modelPath='G:\python-bayes-highdim\output\model'
Evaluation_Data.SaveModel(model,modelPath+"-testSyn");

print "test"