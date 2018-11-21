# -*- coding:utf-8 -*-
import random;
import JunctionTree;
import Dependency;
import Evaluation_Data;

'''
  保存属性及其对应的父属性集合
  x:表示当前属性
  y:表示对应的父节点属性集
'''
class Dependence:
    def __init__(self,x,y):
        self.x=x;
        self.y=y;
    def get1(self):
        return self.x;
    def get2(self):
        return self.y;

'''
    保存最终的贝叶斯网络结构
'''
class DAG:
    def __init__(self):
        self.dag=[];
    def put1(self,x,y):
        self.dag.append(Dependence(x,y));
    def put2(self,dep):
        self.dag.append(dep);
    def get(self,i):
        return self.dag[i];

'''
    保存贝叶斯网络及对应的联合概率分布
'''
class DAG_pro:
    def __init__(self):
        self.dagPro=[];
    def put(self,set,pro):
        self.dagPro.append(Dependence(set,pro));
    def get(self,i):
        return self.dagPro[i];

'''
    将贝叶斯网络转换为相关性矩阵
    为了方便与任老师的Lopub第二个相关性识别进行对比实验
'''
def getDepenGraph(model,att_num):
    BayesGraph=[[0 for i in range(att_num)]for i in range(att_num)];
    for i in range(att_num):
        new=model.get(i);
        now=new.get1();
        set=new.get2();
        for j in set:
            BayesGraph[now][j]=1;
            BayesGraph[j][now]=1;
    return BayesGraph

'''
    训练贝叶斯网络
'''
def Model_Greedy(bit_cand_list, bit_list, bitsum_list,f, att_num,k,rowlist,dt):
    # 初始化
    model=DAG();
    model_pro=DAG_pro();
    S=[];     #已经找到父节点的属性结合
    V=[i for i in range(att_num)];    #待找父节点的属性结合
    init=random.randint(0,att_num-1);
    S.append(init);
    V.remove(init);
    model.put1(init,[]);
    #计算init的边缘分布，加入model_pro
    prob, proe = JunctionTree.getProb([init,init], bit_list, bit_cand_list, rowlist, bitsum_list, f, dt);
    p_single1 = [sum(eachlist) for eachlist in proe]
    model_pro.put([init],[[i for i in range(len(p_single1))],p_single1]);

    #构建贝叶斯网络
    for i in range(att_num-1):
        deps={};            #保存所有的互信息值
        ALLpro={};          #保存所有的联合概率分布
        tempSet=S2V(S,V,k);   #待选AP对
        for dep in tempSet:
            x1 = [dep.get1()];
            y1 = dep.get2();
            z1 = x1 + y1;
            #计算联合分布概率和边缘概率
            prob,proe=JunctionTree.getProb(z1,bit_list, bit_cand_list, rowlist, bitsum_list, f, dt);
            p_single1 = [sum(eachlist) for eachlist in proe]
            p_comb_T = map(list, zip(*proe))
            p_single2 = [sum(eachlist) for eachlist in p_comb_T]

            print z1
            #print ('pro:',proe)
            #print('p single1:', p_single1)
            #print('p single2:', p_single2)

            #计算互信息
            Mi = Dependency.Get_MI(p_single1, p_single2, proe)
            #print Mi
            deps[dep]=Mi;
            ALLpro[Mi]=prob;
        #选择互信息最大的候选属性
        m = max(deps.values());
        picked = list(deps.keys())[list(deps.values()).index(m)]
        model.put2(picked);
        #保存联合概率
        x1 = [picked.get1()];
        y1 = picked.get2();
        z1 = x1 + y1;
        model_pro.put(z1,ALLpro[m]);
        S.append(picked.get1());
        V.remove(picked.get1());
        print ("i:",i);
    return model,model_pro


#生成S集合的所有K维子集
def kSub(S,k):
    ans=[];
    if(k==0):
        ans.append([]);
        return ans;
    subS=[i for i in S];
    for i in S:
        subS.remove(i);
        for sub in kSub(subS,k-1):
            full=sub;
            full.append(i);
            ans.append(full);
    return ans;

#所有未选择父节点属性的候选对
def S2V(S,V,k):
    ans=[];
    kS=kSub(S,k);
    if (len(kS)==0):
        kS.append([i for i in S]);
    for source in kS:
        for target in V:
            ans.append(Dependence(target,source));
    return ans;

'''
   合成数据集
'''
def Sampling(num_att,model_pro,num_node,model,bit_cand_list):
    iniSyn=[[0 for i in range(num_att)] for j in range(num_node) ];
    #print iniSyn
    for i in range(num_node):
        for j in range(num_att):
            dep=model.get(j);  #依赖关系
            pre=[0 for l in range(len(model_pro.get(j).get1()))]   #保存已经赋过值的属性的当前取值
            k=1;
            for p in dep.get2():   #dep.get2()是已经赋过值的属性集
                pre[k]=iniSyn[i][p];
                k=k+1;
            iniSyn[i][dep.get1()]=conditional(dep,pre,model_pro,bit_cand_list,j);
    return iniSyn;

'''
    根据贝叶斯网络的依赖关系，合成数据
'''
def conditional(dep,pre,model_pro,bit_cand_list,index):

    att=model_pro.get(index).get1();
    ALLpro = model_pro.get(index).get2();
    sum=0.0;
    new_att = dep.get1();
    d = len(bit_cand_list[new_att]);
    temp=[0 for i in range(len(ALLpro[0]))]
    if(len(att)==1):
        sum=1.0;
    else:
        for i in range(len(ALLpro[0])):
            temp[i]=list(map(int, ALLpro[0][i]));
        for i in range(d):
            pre[0]=i;
            sum = sum + ALLpro[1][temp.index(pre)];
    if(sum==0.0):
        return random.randint(0,d-1);

    pick=sum*random.uniform(0,1);
    cum=0.0;
    if(len(att)==1):
        for val in range(d):
            cum+=ALLpro[1][val];
            if(cum>pick):
                return val;
    else:
        for i in range(d):
             pre[0] = i;
             cum = cum + ALLpro[1][temp.index(pre)];
             if(cum>pick):
                return i;
