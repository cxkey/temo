import json

f=open('./qq','r')
d = {}
while True:
    line = f.readline().strip()
    if line:
        print line
        symbol = line.split('\t')[0]
        min_trade_size = line.split('\t')[1]
        precision = line.split('\t')[2]
        #print symbol,min_trade_size,precision
        d[symbol] = {'min_trade_size':min_trade_size,'precision':precision}
    else:
        break
fw = open('./11.txt','w')
fw.write(json.dumps(d))



