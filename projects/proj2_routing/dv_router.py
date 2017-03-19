"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    # POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        self.start_timer()  # Starts calling handle_timer() at correct rate

        self.neighborTracker = {}
        self.portDelay = {}
        self.portSwitchTracker = {}
        self.delayDest = {}
        self.routingTable = {}
        self.routingTimers = {}


    def poisonSendPackets(self, port=None, dest=None, delay=None, flood = False):
        if self.POISON_MODE:
            routePacket = basics.RoutePacket(dest, INFINITY)
            self.send(routePacket, port, flood)

    def sendPackets(self, port=None, flood=False):
        for dest in self.routingTable:
            delay = self.delayDest[dest]
            poisonPort = self.routingTable[dest]

            if flood:
                for port in self.portDelay:
                    routePacket = basics.RoutePacket(dest, delay)

                    if port == poisonPort:
                        self.poisonSendPackets(port, dest, delay)
                    else:
                        self.send(routePacket, port, False)

            else:
                if (port == poisonPort):
                    self.poisonSendPackets(port, dest, delay)
                else:
                    routePacket = basics.RoutePacket(dest, delay)
                    self.send(routePacket, port, False)

    def floodPoisonedPort(self, dest=None, port=None):
        routePacket = basics.RoutePacket(dest, INFINITY)
        self.send(routePacket, port, True)

    def compareSwitches(self, dest=None):
        delay = INFINITY
        for portSwitch, switch in self.portSwitchTracker.values():
            if switch == dest:
                if self.portDelay[portSwitch] <= delay:
                    delay = self.portDelay[portSwitch]
                    self.delayDest[dest] = delay
                    self.routingTable[dest] = portSwitch
        if delay == INFINITY:
            if self.routingTable.has_key(dest):
                self.delayDest.pop(dest)
                self.routingTable.pop(dest)

    def removeSelf(self, switch=None, destination=None):
        if switch in self.neighborTracker.keys():
            if destination in self.neighborTracker[switch].keys():
                del self.neighborTracker[switch][destination]
                del self.routingTimers[switch][destination]
        self.bellmanAlgo()

    def updateNeighbor(self , port=None, source=None, dest=None, delay=None):
        if source in self.neighborTracker.keys():
            neighbor = self.neighborTracker[source]
        else:
            neighbor = {}
        neighbor[dest] = self.portDelay[port] + delay
        self.neighborTracker[source] = neighbor

        if source in self.routingTimers.keys():
            neighbor = self.routingTimers[source]
        else:
            neighbor = {}
        if dest in neighbor.keys():
            sourceTimer = neighbor[dest]
            sourceTimer.cancel()

        timer = api.create_timer(self.ROUTE_TIMEOUT, self.removeSelf, False, False, (source, dest))
        neighbor[dest] = timer
        self.routingTimers[source] = neighbor

    def bellmanAlgo(self):
        for destination, latency in self.delayDest.items():
            switchCurrent = None
            out_port = None
            swapped = False
            delay = INFINITY
            delayCurrent = INFINITY

            for switch, latencies in self.neighborTracker.items():
                if destination in latencies.keys():
                    if latencies[destination] < delay:
                        delayCurrent = self.routingTimers[switch][destination].seconds
                        delay = latencies[destination]
                        switchCurrent = switch
                        swapped = True
                    elif latencies[destination] == delay:
                        routingDelay = self.routingTimers[switch][destination].seconds
                        if delayCurrent < routingDelay:
                            delayCurrent = routingDelay
                            delay = latencies[destination]
                            switchCurrent = switch
                            swapped = True

            if swapped:
                for port in self.portSwitchTracker:
                    if self.portSwitchTracker[port] == switchCurrent:
                        out_port = port

                self.routingTable[destination] = out_port
                self.delayDest[destination] = delay

            for port, switch in self.portSwitchTracker.items():
                if switch == destination:
                    if self.portDelay[port] <= delay:
                        delay = self.portDelay[port]
                        self.routingTable[destination] = port
                        self.delayDest[destination] = delay

            if delay >= INFINITY:
                if destination in self.routingTable.keys():
                    self.routingTable.pop(destination)
                    self.delayDest.pop(destination)

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        self.portDelay[port] = latency
        self.sendPackets(port, False)

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        router = self.portSwitchTracker[port]
        if self.portDelay.has_key(port):
            self.portDelay.pop(port)
            self.portSwitchTracker.pop(port)
        if self.neighborTracker.has_key(router):
            self.neighborTracker.pop(router)

        if self.POISON_MODE:
            for dest, routingPort in self.routingTable.items():
                if routingPort == port:
                    self.floodPoisonedPort(dest, port)
                    self.routingTable.pop(dest)
                    self.delayDest.pop(dest)
                    self.compareSwitches(dest)

        self.bellmanAlgo()

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            dest = packet.destination
            source = packet.src.name
            packetLatency = packet.latency

            if self.POISON_MODE:
                if packetLatency >= INFINITY:
                    if self.neighborTracker.has_key(source):
                        if self.neighborTracker[source].has_key(dest):
                            del self.neighborTracker[source][dest]

                            if self.routingTable.has_key(dest):
                                if self.routingTable[dest] == port:
                                    self.compareSwitches(dest)
                                    self.floodPoisonedPort(dest, port)
                                self.bellmanAlgo()
                                return

            self.portSwitchTracker[port] = source
            if not dest in self.routingTable.keys():
                self.routingTable[dest] = port
                self.delayDest[dest] = packetLatency + self.portDelay[port]

            self.updateNeighbor(port, source, dest, packetLatency)
            self.bellmanAlgo()

        elif isinstance(packet, basics.HostDiscoveryPacket):
            delay = self.portDelay[port]
            host = packet.src.name
            self.portSwitchTracker[port] = host

            if not host in self.routingTable.keys():
                self.routingTable[host] = port
                self.delayDest[host] = delay
            else:
                if (self.delayDest[host] >= delay):
                    self.routingTable[host] = port
                    self.delayDest[host] = delay
            self.updateNeighbor(port, self, packet.src.name, delay)


        else:
            # Totally wrong behavior for the sake of demonstration only: send
            # the packet back to where it came from!
            if packet.dst.name in self.routingTable.keys():
                if self.delayDest[packet.dst.name] >= INFINITY:
                    return

                out_port = self.routingTable[packet.dst.name]
                if out_port != port:
                    self.send(packet, out_port, False)

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        self.bellmanAlgo()
        self.sendPackets(None, True)
