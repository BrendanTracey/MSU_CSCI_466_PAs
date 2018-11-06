'''
Created on Nov 5 2018
@author: btracey
'''
import queue
import threading


## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
        self.mtu = None

    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None

    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)


## Implements a network layer packet (different from the RDT packet
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths
    dst_addr_S_length = 5

    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S, id, flag, offset):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.id = id
        self.flag = flag
        self.offset = offset


    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()

    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return byte_S

    ## extract a packet object from a byte string
    # modified to properly extract all the segmented related fields
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length : ]
        id = byte_S[NetworkPacket.dst_addr_S_length - 2]
        flag = byte_S[NetworkPacket.dst_addr_S_length - 1]
        offset = byte_S[NetworkPacket.dst_addr_S_length]
        return self(dst_addr, data_S, id, flag, offset)




## Implements a network host for receiving and transmitting data
class Host:

    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False #for thread termination

    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)

    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    # @param id for the fragmented packets original data
    # @param flag for the type of flag it has
    # @param offset for what chunk of the data it is
    #udt send now has 6 parameters, to send along the variables necessary for fragmentation. If the message length is higher than the MTU,
    #then it will break it into an array of the information and then go through the array and create a new packet that will fit
    #underneath the MTU
    def udt_send(self, dst_addr, data_S, id, flag, offset):
        p = NetworkPacket(dst_addr, data_S, id, flag, offset)
        #fragment the packet if it is smaller than mtu
        if len(p.data_S) > self.out_intf_L[0].mtu:
            print('Fragmenting packet')
            #break message into fragments
            chunks = [data_S[i:i+self.out_intf_L[0].mtu] for i in range(0, len(data_S), self.out_intf_L[0].mtu)]
            #print for testing purposes
            for i in range(len(chunks)):
                print('Chunk %d has the message: %s' % (i, chunks[i]))
            #for loop that sends each appropriately sized packet. No need to recurse, since we already know the MTU so each smaller packet is perfectly sized
            #Greedy approach of breaking everything down into chunks the exact size of the MTU is optimal
            for i in range(len(chunks) - 1):
                #All the chunks from the same original packet have the same id, so they can be reconstructed
                #All chunks but the last one will have flag 1 to demonstrate there are more packets
                g = NetworkPacket(dst_addr,chunks[i], id, 1, i)
                self.out_intf_L[0].put(g.to_byte_S())
            #last chunk, flag identification 0, receiver knows the chunk is over
            h = NetworkPacket(dst_addr,chunks[0], id, 0, len(chunks))
            self.out_intf_L[0].put(h.to_byte_S())
        else:
            self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
            print('%s: Sending whole packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None:
            print('%s: received packet "%s" on the in interface' % (self, pkt_S))

    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return



## Implements a multi-interface router described in class
class Router:

    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces
    # @param max_queue_size: max queue length (passed to Interface)
    # @param Routing table added manually in the simulation class, but since we know the all the
    # setup of our network and links we can just manually add all the routing tables. Since we know the name of the destination
    # we can just use a one dimensional array and traverse by number
    def __init__(self, name, intf_count, max_queue_size, routing_table):
        self.stop = False #for thread termination
        self.name = name
        self.routing_table = routing_table
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                    #check the slot in the table to see if the next destination is server 3, from client 1
                    #then redirect the packet based on the routing table
                    if self.routing_table[0] == 'Three':
                        self.out_intf_L[i].put(p.to_byte_S(), True)
                        print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                            % (self, p, i, 0, self.out_intf_L[i].mtu))
                    #check the slot in the table to see if the next destination is server 4, from client 2
                    #then redirect the packet based on the routing table
                    elif self.routing_table[0] == 'Four':
                        self.out_intf_L[i].put(p.to_byte_S(), True)
                        print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                            % (self, p, i, 1, self.out_intf_L[i].mtu))
                    else:
                        self.out_intf_L[i].put(p.to_byte_S(), True)
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass

    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return
