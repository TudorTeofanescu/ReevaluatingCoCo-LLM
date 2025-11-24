# CoCo Analysis: cbnplpkljokdodpligcaolkmodfondhl

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (both identical flows)

---

## Sink: cs_window_eventListener_submit-action → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cbnplpkljokdodpligcaolkmodfondhl/opgen_generated_files/cs_1.js
Line 537	window.addEventListener("submit-action", function(evt) {
Line 538	    if (gitdDebugMode) console.log("content-script","submit-action", evt.detail)
Line 539	    chrome.runtime.sendMessage(JSON.parse(evt.detail), function(response) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cbnplpkljokdodpligcaolkmodfondhl/opgen_generated_files/bg.js
Line 1041	fetch(_findUrlFromManifest(request.url), {
Line 1065	url = (manifestData.permissions[0]).replace("/*", request_url)
Line 1067	url = (manifestData.host_permissions[0]).replace("/*", request_url)

**Code:**

```javascript
// Content script - cs_1.js (lines 537-550)
window.addEventListener("submit-action", function(evt) {
    if (gitdDebugMode) console.log("content-script","submit-action", evt.detail)
    chrome.runtime.sendMessage(JSON.parse(evt.detail), function(response) { // ← evt.detail attacker-controlled
        if (gitdDebugMode) console.log("bg-response", response);
        window.dispatchEvent(new CustomEvent(
            'submit-action-response',
            {
              bubbles: true,
              detail: JSON.stringify(response)
            }
        ))
    });
}, false);

// Background script - bg.js (lines 1036-1071)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.name === "gitd-api") {
        fetch(_findUrlFromManifest(request.url), { // request.url from attacker
            method: "POST",
            body: JSON.stringify(request.body), // request.body from attacker
            headers: {
              "content-type": "application/json",
            },
          })
          .then(resp => resp.json())
          .then(response => sendResponse(response))
          .catch(e => {
            sendResponse({status: false, message: "internal server error. something wrong!"})
        })
    }
    return true
})

function _findUrlFromManifest(request_url) {
    let version = manifestData.manifest_version
    let url = ""
    if (version === 2) {
        url = (manifestData.permissions[0]).replace("/*", request_url)
    } else if (version === 3) {
        url = (manifestData.host_permissions[0]).replace("/*", request_url)
        // manifestData.host_permissions[0] = "https://api.gitdownloadmanager.com/*"
        // Result: "https://api.gitdownloadmanager.com" + request_url
    }
    return url
}
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (Trusted Infrastructure). While an attacker can trigger the window event listener and control the request data (including request.url and request.body), the fetch destination is hardcoded to the developer's backend domain. The `_findUrlFromManifest` function constructs the URL by replacing "/*" in the manifest's host_permissions ("https://api.gitdownloadmanager.com/*") with the attacker's request.url. This means the attacker can only control the PATH (/endpoint) on the trusted backend, not redirect the request to an attacker-controlled domain. According to the methodology, "Data TO hardcoded backend: fetch('https://api.myextension.com', {body: attackerData})" is a FALSE POSITIVE (Pattern X). The extension is sending data to its own trusted infrastructure at api.gitdownloadmanager.com, which falls under trusted infrastructure communication.
