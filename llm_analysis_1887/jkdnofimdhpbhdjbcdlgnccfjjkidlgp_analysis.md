# CoCo Analysis: jkdnofimdhpbhdjbcdlgnccfjjkidlgp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal -> chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jkdnofimdhpbhdjbcdlgnccfjjkidlgp/opgen_generated_files/bg.js
Line 1026	    const token = request.token;

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener((request, sender) => {
  // Validation check (but we ignore per methodology)
  if (!sender.url.includes('holodex.net')) {
    return;
  }

  if (request.message === MESSAGE.TOKEN) {
    const token = request.token; // <- attacker-controlled from external message
    chrome.storage.local.set({ token }, async () => {
      if (!token) {
        return;
      }
      await cacheFavorites(token);
      await updateBadge(token);
    });
  }
});

// Token usage - sends to hardcoded backend
const cacheFavorites = async (token) => {
  const response = await fetch(`${apiUrl}/users/favorites`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  // ... (apiUrl = 'https://holodex.net/api/v2')
};

const updateBadge = async (token) => {
  const response = await fetch(`${apiUrl}/users/live?channels=${favorites.join(',')}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  // ... (apiUrl = 'https://holodex.net/api/v2')
};
```

**Classification:** FALSE POSITIVE

**Reason:** While an external attacker (from holodex.net domains) can inject an arbitrary token into storage, the stored token is only used to make authenticated requests to the developer's hardcoded backend URL (https://holodex.net/api/v2). According to the methodology, data TO hardcoded backend URLs is trusted infrastructure. The attacker can send their own token to the developer's backend, but compromising the developer's infrastructure is an infrastructure issue, not an extension vulnerability.
