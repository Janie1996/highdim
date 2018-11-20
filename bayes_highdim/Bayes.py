# -*- coding:utf-8 -*-
import random;
import JunctionTree;
import Dependency;

class Dependence:
    def __init__(self,x,y):
        self.x=x;
        self.y=y;
    def get1(self):
        return self.x;
    def get2(self):
        return self.y;


class DAG:
    dag=[];
    def __init__(self):
        self
    def put1(self,x,y):
        self.dag.append(Dependence(x,y));
    def put2(self,dep):
        self.dag.append(dep);
    def get(self,i):
        return self.dag[i];

class DAG_pro:
    dagPro=[];
    def __init__(self):
        self
    def put(self,set,pro):
        self.dagPro.append(Dependence(set,pro));
    def get(self,i):
        return self.dagPro[i];

def Model_Greedy(bit_cand_list, bit_list, bitsum_list,f, att_num,k,rowlist,dt):
    model=DAG();
    model_pro=DAG_pro();
    #model_pro={};
    #初始化
    S=[];
    V=[i for i in range(att_num)];
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
        deps={};
        ALLpro={};
        tempSet=S2V(S,V,k);
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


#对应候选对
def S2V(S,V,k):
    ans=[];
    kS=kSub(S,k);
    if (len(kS)==0):
        kS.append([i for i in S]);

    for source in kS:
        for target in V:
            ans.append(Dependence(target,source));

    return ans;


#计算条件概率
def Conditionals(k,att_num,model):
    for i in range(k,att_num):
        mrg=model.get(i).get1();  #属性集


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
    bit_list = [0 for i in range(num_node)];
    #每个用户数据二进制表示
    for i in range(num_node):
        x=[0 for j in range(num_att)];
        for j in range(num_att):
            y=bit_cand_list[j][0];   #真实值二进制表示
            z=[0 for k in range(len(y))]
            x[j]=z;
        bit_list[i]=x;

    print bit_list

    for i in range(num_node):
        for j in range(num_att):
            dep=model.get(j);  #依赖关系
            pre={}   #保存已经赋过值的属性的当前取值
            for p in dep.get2():   #dep.get2()是已经赋过值的属性集
                pre[p]=bit_list[i][p];
            bit_list[i][dep.get1()]=conditional(dep,pre,model_pro,bit_cand_list,j);
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
            #ALLpro[0][i] = list(map(int, ALLpro[0][i]));
        for i in range(d):
            pre[0]=i;
            #sum=sum+ALLpro[1][ALLpro[0].index(pre)];
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