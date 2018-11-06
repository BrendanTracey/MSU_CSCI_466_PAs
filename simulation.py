'''
Created on Nov 5 2018
@author: btracey
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
    #now supports the topology in part 2 of the project, with 2 clients, 4 routers and 2 servers connected as specified
    client1 = network.Host(1)
    object_L.append(client1)
    client2 = network.Host(2)
    object_L.append(client2)
    router_a = network.Router(name='A', intf_count=2, max_queue_size=router_queue_size ,routing_table=['B','C'])
    object_L.append(router_a)
    router_b = network.Router(name='B', intf_count=2, max_queue_size=router_queue_size, routing_table=['D'])
    object_L.append(router_b)
    router_c = network.Router(name='C', intf_count=2, max_queue_size=router_queue_size, routing_table=['D'])
    object_L.append(router_c)
    router_d = network.Router(name='D', intf_count=2, max_queue_size=router_queue_size, routing_table=['Three','Four'])
    object_L.append(router_d)
    server3 = network.Host(3)
    object_L.append(server3)
    server4 = network.Host(4)
    object_L.append(server4)

    #create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)

    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    #conforms to all the routing interface and link connection
    link_layer.add_link(link.Link(client1, 0, router_a, 0, 50))
    link_layer.add_link(link.Link(client2, 0, router_a, 1, 50))
    link_layer.add_link(link.Link(router_a, 0, router_b, 0, 30))
    link_layer.add_link(link.Link(router_a, 1, router_c, 0, 30))
    link_layer.add_link(link.Link(router_b, 0, router_d, 0, 50))
    link_layer.add_link(link.Link(router_c, 0, router_d, 1, 50))
    link_layer.add_link(link.Link(router_d, 0, server3, 0, 50))
    link_layer.add_link(link.Link(router_d, 1, server4, 0, 50))




    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client1.__str__(), target=client1.run))
    thread_L.append(threading.Thread(name=client2.__str__(), target=client2.run))
    thread_L.append(threading.Thread(name=server3.__str__(), target=server3.run))
    thread_L.append(threading.Thread(name=server4.__str__(), target=server4.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))

    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()

    #Forward this message to at least 3 other routers or you will have bad luck and high latency
    #create some send events
    for i in range(1):
        client1.udt_send(2, 'According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees dont care what humans think is impossible. Yellow, black. Yellow, black.Yellow, black. Yellow, black. Ooh, black and yellow! Lets shake it up a little. Barry! Breakfast is ready! Coming! Hang on a second. Hello? Barry? Adam? Can you believe this is happening? I cant. Ill pick you up. %d' % i, 0, 0, 0)


    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")



# writes to host periodically
