import xlrd
synthe=[['1','0','2'],['1','1','0'],['1','0','2']];

file=open('test.txt');
sys=[[0 for i in range(3)]for j in range(3) ]
i=0
while 1:
    line = file.readline()[:-2]    #read a line in datafile
    lineData=line.strip().split(',');
    if not line:
        break
    sys[i]=lineData;
    i=i+1;
file.close();

'''

'''

'''
file=open('test.txt','w');
for i in synthe:
    for j in i:
        file.write(j);
        file.write(',');
    file.write('\n');
file.close();

'''