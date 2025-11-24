# CoCo Analysis: cebahajfamifimbgfnilhcdlgicajmln

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (all variants of same flow)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cebahajfamifimbgfnilhcdlgicajmln/opgen_generated_files/cs_0.js
Line 809	window.addEventListener('message', function(event)
Line 811	let data = event.data;
Line 818	case 'iframe.close'    : close(data.settings); break;

**Code:**

```javascript
// Content script - postMessage listener
window.addEventListener('message', function(event)
{
    let data = event.data; // Line 811 - attacker-controlled data

    if(!shop || !(data && data.message) || data.shopId !== shop.id){ return; }

    switch(data.message)
    {
        case 'iframe.resize'   : resize(data.size); break;
        case 'iframe.close'    : close(data.settings); break; // Line 818
        case 'iframe.settings' : replace_settings(data.settings); break;
    }
});

function close(settings)
{
    shopSettings = settings; // Attacker-controlled data assigned to shopSettings
    chrome.storage.local.get([shop_key], function(storage)
    {
        if(storage[shop_key])
        {
            storage[shop_key] = shopSettings; // Poisoned data stored
            chrome.storage.local.set(storage, function()
            {
                $container.removeClass('preview-normal preview-mini view-compact view-normal').addClass('view-mini');
                $view_count.text(shopSettings.showOnlyPinned ? shopSettings.pinned.length : shop.coupons.length);
            });
        }
    });
}

function replace_settings(settings)
{
    shopSettings = settings; // Attacker-controlled data
    chrome.storage.local.get([shop_key], function(storage)
    {
        if(storage[shop_key])
        {
            storage[shop_key] = shopSettings; // Poisoned data stored
            chrome.storage.local.set(storage, function(){ set_top_position(); });
        }
    });
}

// Data retrieval - but NOT sent back to attacker
function init()
{
    // ... create iframe pointing to extension page
    $iframe = $('<iframe class="coupons-container-iframe" src="' + appUrl + '"></iframe>').appendTo($container);
    // appUrl = chrome.runtime.getURL('html/app/iframe/index.html') - extension page, not attacker page
    iframe = $iframe.get(0);
    // ...
}

function show(view_type, initIframe)
{
    // ...
    change_view_type(view_type, () =>
    {
        // shopSettings sent to extension's own iframe, NOT to attacker
        iframe.contentWindow.postMessage({
            message : 'coupons-extension-content-show-iframe',
            settings : shopSettings, // Retrieved from storage
            shop : shop,
            init : initIframe
        }, '*');
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation chain. While an attacker can poison chrome.storage.local via window.postMessage (lines 809-820), the stored shopSettings is never sent back to the attacker. The data is only retrieved and sent to the extension's own iframe (chrome.runtime.getURL('html/app/iframe/index.html')) via postMessage on line 700, not to an attacker-controlled page. The extension checks if data.shopId matches shop.id, but even bypassing this, there is no path for the attacker to retrieve the poisoned data. Storage poisoning alone without a retrieval path back to the attacker is not exploitable.
