# -*- coding:utf-8 -*-
import random
import math

import Get_Rappor
import JunctionTree
import Estimate_Joint_Distribution
import numpy
import Dependency
'''

def rand_pick(seq , probabilities):
    x = random.uniform(0 ,1)
    cumprob = 0.0
    for item , item_pro in zip(seq , probabilities):
        cumprob += item_pro
        if x < cumprob:
            break
    return item
value_list = [0 , 1]
probabilities = [0.3 , 0.7]

x=[0 for i in range(1000)]
y=[0 for i in range(1000)]

epsilon=1;
f=math.exp(epsilon)/(math.exp(epsilon)+1)
print f

for i in range(1000):
    x[i]=rand_pick(value_list, probabilities);
    y[i]=rand_pick([x[i],1-x[i]],[f,1-f]);
x1=sum(x)
print x1
x2=sum(y)/1000.0
print (math.exp(epsilon)+1)/(math.exp(epsilon)-1)*x2-1.0/(math.exp(epsilon)-1)

f=0.03;
for i in range(1000):
    y[i]=rand_pick([x[i],1-x[i]],[1-f/2,f/2]);

tempbitsum_list = (x1- (0.5 * f) * 1000) / (1.0 - f)  # through the formula to get the real sum
print tempbitsum_list

a=[[1,2,3],[1,1,2],[1,3]];
print type(a)

for i in range(len(a)):
    for j in range(len(a[i])):
        x=float(a[i][j])/10;
        a[i][j]=x;
print a

print int(0.99)


a=[0.1,0.9,-0.2,0.2];
b=numpy.array(a)
b[b<0]=0;
for i in range(len(b)):
    a[i]=float(b[i])/numpy.sum(b);
a=a*1000;
print a
#a=b.tolist()
print sum(a)
'''

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
        print "succes";
    def put1(self,x,y):
        self.dag.append(Dependence(x,y));
    def put2(self,dep):
        self.dag.append(dep);
    def get(self,i):
        return self.dag[i];

#def Model_Greedy(bit_cand_list, bit_list, bitsum_list,f, att_num,k,rowlist,dt):

def Model_Greedy( att_num,k):
    model=DAG();

    #初始化
    S1=[];
    V1=[i for i in range(att_num)];
    init=random.randint(0,att_num-1);
    S1.append(init);
    V1.remove(init);
    model.put1(init,[]);

    #构建贝叶斯网络
    for i in range(att_num-1):
        deps={};
        tempSet=S2V(S1,V1,k);
        j=0;
        for dep in tempSet:
            #x = [dep.get1()];
            #y = dep.get2();
            #z = x + y;
            #prob,proe=JunctionTree.getProb(z,bit_list, bit_cand_list, rowlist, bitsum_list, f, dt);
            #p_single1 = [sum(eachlist) for eachlist in proe]
            #p_comb_T = map(list, zip(*proe))
            #p_single2 = [sum(eachlist) for eachlist in p_comb_T]

            #print('p single1:', p_single1)
            #print('p single2:', p_single2)

            #Mi = Dependency.Get_MI(p_single1, p_single2, proe)
            #print Mi
            deps[dep]=j;
        m = max(deps.values());
        picked = list(deps.keys())[list(deps.values()).index(m)]
        a=picked.get1();
        end=Dependence(picked.get1(),picked.get2());
        S1.append(a);
        #y.remove(picked.get1());
        V1.remove(picked.get1());
        model.put2(end);
    return model

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


model=Model_Greedy(4,3);
print model
'''
p_single=Get_Rappor.lasso_regression(bit_cand_list, bitsum_list)
Dependency.True_MI();


bit_cand_list=[[[1,0],[0,1]],[[1,0],[0,1]],[[1,0,0],[0,1,0],[0,0,1]]];
bit_list=[[[1,0],[1,0],[1,0,0]],[[1,0],[0,1],[1,0,0]],[[0,1],[1,0],[0,1,0]],[[0,1],[1,0],[0,1,0]]];
clique=[0,1,2];
row_list=[['0','1'],['0','1'],['0','1','2']];
bitsum_list=[[2,2],[3,1],[2,2,0]];
f=0;
dt= 0.01;


ans=S2V([1,2],[3,4],0);
for dep in ans:
    x=[dep.get1()];
    y=dep.get2();
    z=x+y;
    print z

m=Model_Greedy(12,12,12,12,12,12);
'''
'''
a={12:0};
print a[12]
m=DAG();
x=12;
y=[];
m.put1(x,y);
y=[1,2,3,4,5]
m.put1(x,y);

z=m.get(0);
print type(z)
print m

'''
'''

def rappor_process(num_bloombits ,num_hash ,f ,num_att ,num_node ,origin_node_num ,list_att ,list_data ,file_id=1):

    # freqrow1,freqnum1,freqrate1,freqrow2,freqnum2,freqrate2,newlist=Get_Params.get_static_info(num_att, num_node, list_att, list_data)
    print('Generating RAPPOR.')
    # init bit_list=[[[0 for i in range(num_bloombits)]for j in range(num_att)] for k in range(num_node)]  # N users blooms
    # print bit_list.__len__()
    bit_cand_list=[[[0 for i in range(num_bloombits)]for j in range(len(list_att[k]))]for k in range(num_att)]  # all attributes blooms
    # print bit_cand_list.__len__()
    bitsum_list=[[0 for i in range(num_bloombits)]for j in range(num_att)]
    # print bitsum_list

    ####N users blooms after rappor
    for i in range(num_node):
        for j in range(num_att):
            e= Get_Params .set_rappor_params(num_bloombits, num_hash,num_att,f) # init the rappor
            bit_list[i][j]=Get_Params. get_B(list_data[i][j], e)
            # print(bit_list[i][j])
    curr_timeb=time.time()
    # print bit_list
    ####sum blooms each bit
    for i in range(num_node):
        for j in range(num_att):
            bitsum_list[j]=list(map( lambda x: x[0]+x[1], zip( bitsum_list[j], bit_list[i][j])))
    # print bitsum_list
    curr_timee=time.time()
    last_time=curr_timee- curr_timeb bit_list=map(list, zip(* bit_list))  # trans everynode into att
    # print('count time:',last_time)
    # os.chdir('G:\python_highdim\output')
    # with open('file-'+str(file_id)+'-marginal.csv','a') as fid:
    #               fid_csv = csv.writer(fid)
    #              fid_csv.writerows([[last_time]])
    # print('origin:',bitsum_list)

    for i in range(num_att):
        for j in range(len(list_att[i])):
            e=Get_Params. set_rappor_params(num_bloombits, num_hash,num_att,f) bit_cand_list[i][j]= Get_Params.get_S(list_att[i][j],e)

    tempbitsum_list=(numpy.array( bitsum_list)-(0.5*f)* num_node)/(1.0-f)
    # through the formula to get the real sum  # print(tempbitsum_list[1])
    bitsum_list=tempbitsum_list.tolist() # print(bitsum_list)
    return bit_cand_list, bit_list, bitsum_list
'''