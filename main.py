from Network import Network
from Spoofer import Spoofer
from App import App

n = Network()
n.ipconfig()
s = Spoofer(n)
a = App(s)
a.create()








