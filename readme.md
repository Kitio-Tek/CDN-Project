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

## Surrogate routes

```
GET http://1.1.1.1:5000/<filename>
```
```
DELETE http://1.1.1.1:5000/<filename>
Authorization: Bearer admin
```


# Suite
Initalement, l'origin possède TOUS les fichiers
on lance origin => il envoie des GET a tous les surrogate pr être surs qu'ils sont en vie
on lance les surrogate (ils vident leur dossier files pr laisser l'origin redistribuer) => tous les GET se valident => tous les surrogate sont enregistré dans le digest de l'origin
l'origin distribue les fichiers EQUITABLEMENT et enregistre dans son digest le mapping fichier <=> surrogate unicast address
(distribuer => transmettre aux surrogate ET supprimer dans son stockage local)

Requete client vers un surrogate:
- si fichier dans cache => reception par le client
- sinon cache MISS => GET vers 

