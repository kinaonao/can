for i in range(10):
    for j in range(10):
        print("\r i = %d \n j = %d  \033[1A " %(i,j) ,end=" ") #\033[2A
print("\033[1B")