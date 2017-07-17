Roll Your Own CDN : 

The purpose of this assignment is to implement basic functionalities in different areas that make up a CDN. The EC2 sites serve as replica servers, one of them being the origin. The ultimate goal is to redirect clients to the replica server (unless the content is present in the cache) as fast as possible. 

Way to run the program :

Our program can be run the following order,

./[deploy|run|stop]CDN -p <port> -o <origin> -n <name> -u <username> -i <keyfile>

where port is the port number that httpserver is binded to (should be a high numbered port between 40000 - 65535) , origin is the name of the origin server for the given CDN, name is the CDN-specific name that the server translates to an IP. (cs5700cdn.example.com, in this case) username is the account name that is used for logging in, and finally, keyfile is the path to the private key that is used for logging into nodes.

The purpose of the deployCDN script is to deploy the dnsserver on cs5700cdnproject.ccs.neu.edu. Also deploy the httpserver on all the given EC2 servers in ec2-hosts.txt. The purpose of runCDN shell scrpt is to the run the dnsserver and httpserver that were deployed from the previous script. Finally, the last script - stopCDN kills all the running servers.

High level description:

HTTP server : 

It is imperative and of utmost importance to implement a well performing cache management technique within the HTTP Server. And as each replica can only have 10 MB of disk space, an optimized approach should be chosen.

In our case, we make use of sqlite3 to implement a database within the server so as to store and retrieve cached content. Also, we have used zlib to compress and decompress data which helps performance. Storing the content as a binary large objecct (blob) only enhances the performance. This technique of caching significantly decreases the latency incurred.

The written program (httpserver) is a multi-threaded program, which means that it can cater to several requests simulataneously. The database created helps us to track the total number of hits for a page. The technique followed in this case is the LRU (Least Recently Used) technique.

DNS Server:

As given in the problem, there were several ways to tackle the complication of arriving at the best time-to-completion for downloading a webpage.

Geolocation is the strategy that we have decided to follow. The combination of factors of the perfectness required for an implementation of active measurement, together with the simplicity and the fact that this strategy enables us to achieve geographically accurate information made it easy for us to go with this approach.

The API used here is from http://ipinfo.io, which helps us to retrieve latitude and the longitude of the given IP address in JSON format. This response after being parsed to get the coorinates can be used to find the distnce between them and the client's coordinates. Also, we have preserved a dictionary to keep track of the mapping between client's IP and the replica server. This results in greater performance when retrieved from the dictionary. 

Challenges faced : 

We initially tried following the active measurement strategy. This was particularly challenging as this required the correct and efficient estimation of RTT. The implementation of active measurement by pinging from all replicas was also quite complex. Thus we decided to go for the geolocation approach.

It was also absolutely necessary to ensure that the DNS packet was created perfectly to ensure that the client was redirected to the best server and that the server contained the required data.

Performance enhancing technques  :

We have used sqlite3, which is a fast, efficient database to store data.

Both dnserver and httpserver are multithreaded which makes both ideal to serve multiple requests simulataneously.

Using a dictionary within dnsserver enables us to get the ip address of the replica in a faster way, in the event when an identical client made a new request.

Future enchancements :

Distributed Hash Tables (DHTS) could be used to store the contents for more efficient access.

Although active measurements seemed difficult to implement, technically and ideally, it seems the best approach for determing the 'best' server for a given client, by estimating RTT and probing the network.


