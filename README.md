# Security and Privacy Party Tricks for Web Servers and Load Balancers
This is a collection of demos from the TDS workshop for Madhacks 2026.

# Requirements
The following software needs to be installed. Package names are for Ubuntu, but you can figure out what they are for your system:
```python3 + flask
apache2
libapache2-mod-security2
haproxy
```

# Demo 1: Penalty box
## Overview
Load-balancing software can be used to examine traffic patterns and route traffic to backend systems according to configurable rules. This demo runs an haproxy load balancer in front of 2 apps- one that is ordinarily routed to, then if too many requests come in a configured time from the same client IP, haproxy routes the request to a different application.

## Run it
Start app

`PORT=10000 python3 app/app.py`

`PORT=10001 python3 app/app.py`

Start haproxy

`haproxy -f haproxy/demo1.cfg`

## Observations
http://localhost:10000

Refresh the page a bunch, notice no change because you are going directly to the application, which will always serve the request.

http://localhost:8081

Refresh the page a bunch, watch the requests land on the 10001 app because haproxy is noticing your spammy requests and routing you to the penalty box instance of the app

# Demo 2: Web server request inspection
Web servers like Apache and nginx are built to service web requests. They are extensible and highly configurable via modules. One of these modules is called Mod Security, enabling a rule engine for examining web requests, identifying suspicious activity, and stopping it before it ever reaches your application.

## Run it
Start apache

`apache2 -f "$PWD/apache/demo2.conf" -DFOREGROUND`

Start app

`PORT=10000 python3 app/app.py`

## Observations
Visit site

http://localhost:10000/api/preferences?user=alice

http://localhost:10000/api/preferences?user=bob

http://localhost:10000/api/preferences?user=../app.py

Problem: application has a path traversal vulnerability

## Remediate
Solution: Put Apache in front of the application and use Mod Security to remediate
```
Listen 8003
<VirtualHost *:8003>
    ServerName localhost

    # Enable modsec and check the user parameter for path traversal
    SecRuleEngine On
    SecRule ARGS:user "@contains ../" \
        "id:10010,phase:2,deny,status:403,log,t:none,msg:'Path traversal detected'"

    # Proxy requests to the app
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:10000/
    ProxyPassReverse / http://127.0.0.1:10000/

    ErrorLog /var/log/apache2/hackathon_error.log
    CustomLog /var/log/apache2/hackathon_access.log combined
</VirtualHost>
```

The SecRule inspects the `user` GET parameter for `../` to prevent path traversal and automatically returns a 403

Now visit

http://localhost:8003/api/preferences?user=alice

http://localhost:8003/api/preferences?user=bob

http://localhost:8003/api/preferences?user=../app.py

Notice the difference in behavior when path traversal is attempted.

### Bonus
The Mod Security Core Rule Set (CRS) has a bunch of rules for detecting common exploits- path traversal is one of them. This CRS is enabled by default in most distributions, so all you have to do is enable the rule engine (`SecRuleEngine On`) with the appropriate include in order to gain protections from it.

Our example here is path traversal, but modules like Modsec can catch many SQL injection attempts, XSS, PHP injection, protocol violations, scanner detections, and more.

# Demo 3: Manipulating responses
Aside from steering traffic and denying unappetizing requests, load balancers and web servers can manipulate the content of a response. The client respects the response (including headers), so client behavior can be influenced based on this manipulation

## Run it
Start app

`PORT=10000 python3 app.py`

Start haproxy

`haproxy -f haproxy/demo3.cfg`

## Observations
Visit site

http://127.0.0.1:1000/csp-demo (directly via app)

http://127.0.0.1:8081/csp-demo (through haproxy)

Note that the button does not work through haproxy. This is because haproxy is manipulating a response header.  The `Content-Security-Policy` header can be used to control things like this, including controlling where Javascript can be executed from. This page has inline Javascript which cannot run when the `script-src` is set to `self`. Read more about the Content-Security-Policy header here: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/script-src

# Demo 4: Manipulating requests
HTTP requests include headers which tell the server something about the client. Most times this is a useful thing- knowing the browser and OS can allow the server to render a page properly (e.g. mobile vs desktop). An originating IP can be used to keep subsequent stateful requests routed to the same server to improve user experience, and many more.

However this information can introduce privacy concerns as well. Browser fingerprinting collects additional information from the client and sends it to the server to try and track users. This can be accomplished in several ways, including Javascript functions collecting client information and sending it in separate requests back to the server.

## Run it
Start app

`PORT=10000 python3 app.py`

Start haproxy

`haproxy -f haproxy/demo4.cfg`

## Observations
Visit site

http://localhost:10000/inspect (directly through app)

^ Note the output on the app console from a request to /inspect - it's accompanied by a request to /api/browser-info

http://localhost:8081/inspect (through haproxy)

^ Note the lack of console output from the /api/browser-info endpoint

The information seen by the application is radically different. Haproxy is enforcing the same Javascript restrictions from the previous demo, so the Javascript fails to run and can't collect (and send) extra information about the client system to the server. Headers persist but are manipulated by haproxy.

# A note on SSL
Because demos 2-4 rely on reading or writing the request or response, they will only work on unencrypted HTTP traffic, or if Apache/haproxy host the proper SSL certificate for HTTPS connections. 
