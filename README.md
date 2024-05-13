# bgpconnectiontracker

The connectionTracker.py was created for the IX community to address a specific problem, which are peering members who illegaly send traffic to other members wihout an agreement for peering. 
If a peering member is sending traffic e.g. via a static route to another member wihtout having a peering agreement this could cause issues as there will be a need for bandwidth which might have not been planned for.

We have created a script which runs locally on a switch to analyze BGP sessions and check for keepalive messages between two peers. If detected we create traffic-policies to allow the traffic between those members.
BGP traffic is allowed generally. 

** This script is a PoC and should be used with caution **
** As a PoC this script has not been fully tested for production use **
