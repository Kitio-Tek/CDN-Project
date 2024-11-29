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

This project implements a simple Content Delivery Network (CDN) using Python and Flask. It consists of:

**Origin Server**: Stores original content and manages distribution using a Distributed Hash Table (DHT).

**Surrogate Servers**: Cache content from the Origin Server and serve it to clients using an LRU Cache for efficient storage management.

**Client Application:** Requests content from Surrogate Servers and plays it using VLC.

**Tests:** Validates the LRU Cache functionality.

## Getting Started
To build Docker images for each component, run the following commands from the root directory of the project:

	`cd origin_server
         docker build -t cdn-origin:latest .`  
	`cd ../surrogate_servers
        docker build -t cdn-surrogate:latest .`  
	`cd ../client_app
        docker build -t cdn-client:latest .`

### Create Docker Network
	`docker network create cdn-network` 
 
### Run the Origin Server container connected to cdn-network:
  
  	`docker run -d \
	  --name cdn-origin \
	  --network cdn-network \
	  -p 5000:5000 \
	  -p 8468:8468 \
	  cdn-origin:latest`

### Run the Surrogate Server container connected to cdn-network:  
  	`docker run -d \
	  --name cdn-surrogate \
	  --network cdn-network \
	  -p 5001:5001 \
	  -p 8469:8469 \
	  cdn-surrogate:latest`

### Uploading Content to the Origin Server
	`ffmpeg -f lavfi -i testsrc=duration=10:size=640x360:rate=30 sample_video.mp4`  

Upload the File Using curl:

	`curl -X POST \
	  -F "content_id=sample_video.mp4" \
	  -F "file=@sample_video.mp4" \
	  http://localhost:5000/upload`  
   
### Run the Client Application container connected to cdn-network:

	`docker run -it \
	  --name cdn-client \
	  --network cdn-network \
	  cdn-client:latest`
