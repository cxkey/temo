

def load_symbol(self):
    symbols= []
    f = open('./33','r')
    while True:
        line = f.readline()
        if line:
            symbols.append(line.strip())
        else:
            break
    return symbols            
    

def scanHistory(self):
    symbols = self.load_symbols()
    for symbol in symbols:
