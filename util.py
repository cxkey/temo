

def permutation(array):
    perm_list = []
    for i in range(0, len(array)):
        for j in range(i+1, len(array)):
            perm_list.append([array[i],array[j]])
    print perm_list                
    return perm_list                
 
if __name__ == '__main__':
     permutation([1,2,3,4])

