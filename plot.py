#from pylab import *
#
#t = arange(0.0, 20.0, 1)
#s = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
#plot(t, s)
#
#xlabel('Item (s)')
#ylabel('Value')
#title('Python Line Chart: Plotting numbers')
#grid(True)
#show()



from matplotlib.pyplot import figure, show
import numpy as npy
from numpy.random import rand


if 1: # picking on a scatter plot (matplotlib.collections.RegularPolyCollection)

    x, y, c, s = rand(4, 100)
    def onpick3(event):
        ind = event.ind
        print 'onpick3 scatter:', ind, npy.take(x, ind), npy.take(y, ind)

    fig = figure()
    ax1 = fig.add_subplot(111)
    col = ax1.scatter(x, y, 100*s, c, picker=True)
    #fig.savefig('pscoll.eps')
    fig.canvas.mpl_connect('pick_event', onpick3)

show()
