'''
Created on Oct 12, 2016
@author: mwittie
'''
import network
import link
import threading
from time import sleep

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 10 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads

    #create network nodes
    client = network.Host(1)
    object_L.append(client)
    server = network.Host(2)
    object_L.append(server)
    router_a = network.Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)

    #create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)

    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    link_layer.add_link(link.Link(client, 0, router_a, 0, 50))
    link_layer.add_link(link.Link(router_a, 0, server, 0, 30))


    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client.__str__(), target=client.run))
    thread_L.append(threading.Thread(name=server.__str__(), target=server.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))

    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()

    #Forward this message to at least 3 other routers or you will have bad luck and high latency
    #create some send events
    for i in range(1):
        client.udt_send(2, 'According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees dont care what humans think is impossible. Yellow, black. Yellow, black.Yellow, black. Yellow, black. Ooh, black and yellow! Lets shake it up a little. Barry! Breakfast is ready! Coming! Hang on a second. Hello? Barry? Adam? Can you believe this is happening? I cant. Ill pick you up. %d' % i, 0, 0, 0)


    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")



# writes to host periodically
