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

## Test servers in development environment
Run origin & surrogate servers with `docker compose up -d`  
- You can try surrogates servers with a GET request at `localhost:5000/download/<filename>` 

- You can try surrogates servers with a GET request at `localhost:5001/<filename>`

## Production environment
Build images with :
- `docker build -t cdn-surrogate:latest surrogate`
- `docker build -t cdn-origin:latest origin`