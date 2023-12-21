"""For eRPC; uses Ubuntu22"""


# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Describe the parameter(s) this profile script can accept.
portal.context.defineParameter("c", "Number of clients", portal.ParameterType.INTEGER, 1)
portal.context.defineParameter("s", "Number of servers", portal.ParameterType.INTEGER, 1)

# Retrieve the values the user specifies during instantiation.
params = portal.context.bindParameters()

nclients = params.c
nservers = params.s

# Create a portal object,
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

servers = ["server-%d" % x for x in range(nservers)]
clients = ["client-%d" % x for x in range(nclients)]
nodes = [request.RawPC(node) for node in servers + clients]

for i, node in enumerate (nodes): 
    node.hardware_type = 'c6525-100g'
    node.disk_image = 'urn:publicid:IDN+utah.cloudlab.us+image+lrbplus-PG0:ubuntu22-py'
    bs = node.Blockstore("bs"+str(i), "/nfs")
    bs.size = "200GB"

#node.addService(emulab.ProgramAgent('node_startcmd_%d' % i, 'cd /proj/sequencer/seq_theano/sequencer; echo \'alias cd2drat="cd /proj/sequencer/tsch/mininetpipe; source export_rtesdk.sh"\' >> ~/.bash_aliases', None, True))

ifaces1 = [node.addInterface('eth1', pg.IPv4Address('10.1.1.%d' % (i + 1),'255.255.255.0'))
            for i, node in enumerate(nodes)]
ifaces2 = [node.addInterface('eth2', pg.IPv4Address('10.1.2.%d' % (i + 1),'255.255.255.0'))
            for i, node in enumerate(nodes)]

# Link tblink-l3
for i, ifaces in enumerate([ifaces1, ifaces2]):
    link_tblink_l3 = request.Link('tblink-l3-%d' % i)
    link_tblink_l3.setNoBandwidthShaping()
    link_tblink_l3.trivial_ok = True
    link_tblink_l3.setProperties(bandwidth=10000000)
    
    # Add nodes to link
    for iface in ifaces:
        link_tblink_l3.addInterface(iface)

request.setRoutingStyle('static')

# Print the generated rspec
pc.printRequestRSpec(request)
