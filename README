This is the code I've written for my project while working at the UCSB Seclab. The overall goal is to spot suspicious activity by looking at the connexion data.

networkx is needed to run most of the scripts.
R and rpy2 are needed to plot the graphs.

A quick description of what's in here:

 
Clustering the accounts and building the communities
<ul>
<li>cluster.py contains the ClusterTool that lets us build the graph and find the communities within it</li>
<li>graph.py is a weighted graph, derived from the networkx graph class</li>
<li>community.py is a modified version of the community detection algorithm found here http://perso.crans.org/aynaud/communities/</li>
<li>clustering.py shows how I built my communities useing the parsed output from the connexion data</li>
</ul>

Studying these communities
<ul>
<li>timeseries.py contains the Timeseries class which speaks for itself. It also contains two other classes, IPUsageGraph and AccountUsageGraph that allow us to plot IPs or Accounts activity over time.</li>
<li>profile.py contains the ProfileList class. It's used to create and store users' profiles from the raw output. We can also compute the IP/user-agent correlation with this class.</li>
<li>profiling.py, like clustering.py, shows how I used my code to obtain the results showed in the paper</li>
</ul>
