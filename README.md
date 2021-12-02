# Gefyra
Gefyra gives Kubernetes-("cloud-native")-developers a completely new way of writing and testing their applications. 
Over are the times of custom Docker-compose setups, Vagrants, custom scrips or other scenarios in order to develop (micro-)services
for Kubernetes.  

Gefyra offers you to:
- run services locally on a developer machine
- operate feature-branches in production-like Kubernetes environment with all adjacent services
- write code in the IDE you already love, be fast, be confident
- leverage all the neat development features, such as debugger, code-hot-reloading, override environment variables
- run high-level integration tests against all dependant services
- keep peace-of-mind when pushing new code to the integration environment 

Gefyra was architected to be fast and robust on an average developer machine including most platforms.

## What is Gefyra?
Gefyra is a toolkit written in Python to arrange a local development setup in order to produce software for and with 
Kubernetes while having fun. It is installed on any development computer and starts its work if it is asked. Gefyra runs
as user-space application and controls the local Docker host and Kubernetes via _Kubernetes Python Client_. 

<p align="center">
  <img src="docs/static/img/gefyra-intro.png" alt="Gefyra controls docker and kubeapi"/>
</p>

(_Kubectl_ is not really required but makes kinda sense to be in this picture)

In order for this to work, a few requirements have to be satisfied:
- a Docker host must be available for the user on the development machine
- there are a few container capabilities required on both sides, within the Kubernetes cluster and on the local computer
- a node port must be opened up on the development cluster for the duration of the development work 

Gefyra intercepts the target application running in the cluster and tunnels all traffic hitting said container to the one running 
locally. Now, developers can add new code, fix bugs or simply introspect the traffic and run it right away in the Kubernetes cluster. 
Gefyra proves the entire infrastructure to do so and provides a high level of developer convenience. 


## Did I hear developer convenience?
The idea is to relieve developers from the stress with containers to go back and forth to the integration system. Instead, take
the integration system closer to the developer and make the development cycles as short as possible. No more waiting for the CI to complete
just to see the service failing on the first request. Cloud-native (or Kubernetes-native) technologies have completely changed the 
developer experience: Infrastructure is increasingly becoming part of developer's business with all the barriers and obstacles.  
Gefyra is here to provide a development workflow with the highest convenience possible. It brings low setup times, rapid development, 
high release cadence and super-satisfied managers.

## Installation
Todo


## How does it work?
In order to write software for and with Kubernetes, obviously a Kubernetes cluster is required. There are already a number of Kubernetes 
distribution available to run everything locally. A cloud-based Kubernetes cluster can be connected as well in order to spare the development
computer from blasting off.
A working _KUBECONFIG_ connection is required with appropriate permissions which should always be the case for local clusters. Gefyra installs the required 
cluster-side components by itself once a development setup is about to be established.

<p align="center">
  <img src="docs/static/img/gefyra-overview.png" alt="Gefyra connects to a Kubernetes cluster"/>
</p>

With these component, Gefyra is able to control a local development machine, and the development cluster, too. Both sides are now in the hand of 
Gefyra.  
Once the developer's work is done, Gefyra well and truly removes all components from the cluster without leaving a trace.  

A few things are required in order to achieve this:
- a _tunnel_ between the local development machine and the Kubernetes cluster
- a local end of that tunnel to steer the traffic, DNS, and encrypt everything passing over the line
- a cluster end of the tunnel, forwarding traffic, taking care of the encryption
- a local DNS resolver that behaves like the cluster DNS
- sophisticated IP routing mechanisms
- a traffic interceptor for containers already running withing the Kubernetes cluster

Gefyra builds on top of the following popular open-source technologies:

### Docker
[*Docker*](https://docker.io) is currently used in order to manage to local container-based development setup, including the
host, networking and container management procedures.

### Wireguard
[*Wireguard*](https://wireguard.com)  is used to establish the connection tunnel between the two ends. It securely encrypts the UDP-bases traffic
and allows to create a _site-to-site_ network for Gefyra. That way, the development setup becomes part of the cluster and locally running containers 
are actually able to reach cluster-based resources, such as databases, other microservices and so on.

### CoreDNS
[*CoreDNS*](https://coredns.io) provides local DNS functionality. It allows resolving resources running within the Kubernetes cluster.

### Nginx
[*Nginx*](https://www.nginx.com/) is used for all kinds of proxying and reverse-proxying traffic, including the interceptions of already running conatiners
in the cluster.

## Architecture of the entire development system

### Local development setup
The local development happens with a running container instance of the application in question on the developer machine.
Gefyra takes care of the local Docker host setup, and hence needs access to it. It creates a dedicated Docker network 
which the container is deployed to. Next to the developed application, Gefyra places a _sidecar_ container. This container,
as a component of Gefyra, is called _Cargo_.  
Cargo acts as a network gateway for the app container and, as such, takes care of the IP routing into and from the cluster.
In addition, Cargo provides a CoreDNS server which forwards all request to the cluster. That way, the app container will be
able to resolve cluster resources and may not resolve domain names that are not supposed to be resolved (think of 
isolated application scenarios).
Cargo encrypts all the passing traffic with Wireguard using ad-hoc connection secrets. 

<p align="center">
  <img src="docs/static/img/gefyra-development.png" alt="Gefyra local development"/>
</p>

This local setup allows developers to use their existing tooling, including their favorite code editor and debuggers. The
application, when it is supported, can perform code-hot-reloading upon changes and pipe logging output to a local shell 
(or other systems).  
Of course, developers are able to mount local storage volumes into the container, override environment variables and modify
everything as they'd like to.  
In Gefyra this action is called _bridge_: from an architectural perspective the application is _bridged_ into the cluster.
If the container is already running within a Kubernetes Pod, it gets replaced and all traffic to the originally running 
container is proxies to the one on the developer machine.  
During the container startup of the application, Gefyre modifies the container's networking from the outside and sets the 
_default gateway_ to Cargo. That way, all container's traffic is passed to the cluster via Cargo's encrypted tunnel. The
same procedure can be applied for multiple app containers at the same time.  

The neat part is that with a debugger and two or more _bridged_ containers, developers can introspect requests from the source
to the target and back around while being attached to both ends.

### The _bridge_ operation in action 
This chapter covers the important _bridge_ operation by following an example.

#### Before the bridge operation
Think of a provisioned Kubernetes cluster running some workload. There is an Ingress, Kubernetes Services and Pods running
containers. Some of them use the "sidecar" pattern.

<p align="center">
  <img src="docs/static/img/gefyra-process-step-1.png" alt="Gefyra development workflow_step1"/>
</p>

#### Preparing the bridge operation
Before the _brigde_ can happen, Gefyra installs all required components to the cluster. A valid and privileged connection
must be available on the developer machine to do so.  
The main component is the cluster agend called _Stowaway_. The Stowaway controls the cluster side of the tunnel connection.
It is operated by [Gefyra's Operator application](operator).

<p align="center">
  <img src="docs/static/img/gefyra-process-step-2.png" alt="Gefyra development workflow step 2"/>
</p>

Stowaway boots up and dynamically creates Wireguard connection secrets (private/public key-pair) for itself and Cargo.
Gefyra copies these secrets to Cargo for it to establish a connection. This is a UDP connection. It requires a Kubernetes
Service of kind _nodeport_ to allow the traffic to pass through *for the time of an active _bridge_ operation*. Gefyra's 
operator installs these componentens with the requested parameters and removes it after the session terminates.  
By the way: the Gefyra's operator removes all components and itself from the cluster in case the connection was disrupted 
for some time, too.  
Once a connection could be establised from Cargo to Stowaway, Gefyra spins up the app container on the local side for the
developer to start working.  
Another job of Gefyra's operator is to rewrite the target Pods, i.e. exchange the running container through Gefyras proxy,
called _Carrier_.  
For that, it creates a temporary Kubernetes Service that channels the Ingress traffic (or any other kind of cluster internal
traffic) to the container through Stowaway and Cargo to the locally running app container. 


#### During the bridge operation
A bridge can robustly run as long as it is required to (give the connection does not drop in the meanwhile).
Looking at the example, Carrier was installed in Pod &lt;C&gt; on port _XY_. That port was previously occupied by the container
running originally here. In most cases, the local app container represents the development version of that originally
provisioned container. Traffic coming from the Ingress, passing on to the Service &lt;C&gt; hits Carrier (the proxy). Carrier
bends the request to flow through Gefyras Service to the local app container via Stowaway' and Cargo's tunnel. This works
since the app container's IP is routable from within the cluster.  
The local app container does not simply return a response, but fires up another subsequent request by itself to 
Service &lt;A&gt;. The request roams from the local app container back into the cluster and hits Pod &lt;A&gt;'s container via 
Service &lt;A&gt;. The response is awaited.  
Once the local app container is done with constructing it's initial answer the response gets back to Carrier and afterwards
to the Ingress and back to the client.

<p align="center">
  <img src="docs/static/img/gefyra-process-step-3.png" alt="Gefyra development workflow step 3"/>
</p>

With that, the local development container is reachable exactly the same way another container from within the cluster 
would be. That fact is a major advantage, especially for frontend applications or domain-sensitive services.  
Developers now can run local integration tests with new software while having access to all interdependent services.  
Once the development job is done, Gefyra properly removes everything, resets Pod &lt;C&gt; to its original configuration,
and tears the local environment down (as nothing ever happened).

Doge is excited about that.

<p align="center">
  <img src="docs/static/img/doge.jpg" alt="Doge is excited"/>
</p>


## Credits
Todo





