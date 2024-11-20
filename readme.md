# CDN project


## Presentation


## Diagram
![Diagram](diagram.png)  
For routers, each color corresponds to an AS.  
- blue = 64001
- yellow = 64002
- red = 64003
## Choices
**- User/CDN communication:** BGP Anycast

**- File retrieving strategy:**  
	1. Intra-cluster caching (cache miss => query to origin)   
	2. Digest-based (cache miss => check digest => query to file owner)

**- Cache management strategy:** The Least Recently Used (LRU)  

**- Cache size:** 3MB in each surrogate server  

**- File size:** 1MB