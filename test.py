import random
import matplotlib.pyplot as plt

rawData={}

def generateRawData():
    From = 0
    To = 100000
    gap = 900
    for time in range(From, To + 1, gap):
       rawData[time] = round(random.uniform(0, 3),2)
    print("raw data points for user from:", From, " to:", To, "is:")
    print (sorted(rawData))
    print(rawData)
    y=[]
    x = sorted(rawData)
    for time in x:
        y.append(rawData[time])
    print(x)
    print(y)
    plt.plot(x, y, label="line 1")
    # naming the x axis
    plt.xlabel('x - axis')
    # naming the y axis
    plt.ylabel('y - axis')
    # giving a title to my graph
    plt.title('Two lines on same graph!')

    # show a legend on the plot
    plt.legend()

    # function to show the plot
    plt.show()

if __name__=='__main__':
    generateRawData()