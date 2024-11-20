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

**- Cache size:** 3MB in each surrogate server  

**- File size:** 1MB

## Run servers
### Surrogates
`cd surrogate`  
`docker build -t cdn-surrogate:latest .`  
`docker run -d --name cdn-surrogate -p 5000:5000 cdn-surrogate`
### Origin
TO DO