# CDN project


## Presentation


## Diagram
![Diagram](diagram.png)
## Choices
**- User/CDN communication:** BGP Anycast

**- File retrieving strategy:**  
	1. Intra-cluster caching (cache miss => query to origin)   
	2. Digest-based (cache miss => check digest => query to file owner)

**- Cache management strategy:** The Least Recently Used (LRU)  

**- Cache size:** 5kB in each surrogate server  

**- File size:** 1kB

## GNS3 environment
Build images with :
- `docker build -t cdn-surrogate:latest surrogate`
- `docker build -t cdn-origin:latest origin`  
- `docker build -t cdn-client:latest client`  

Get inside the surrogate containers and run :  
`python surrogate.py <surrogate_unicast_address>`