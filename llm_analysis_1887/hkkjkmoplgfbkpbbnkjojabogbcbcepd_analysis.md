# CoCo Analysis: hkkjkmoplgfbkpbbnkjojabogbcbcepd

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink: XMLHttpRequest_responseText_source → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkkjkmoplgfbkpbbnkjojabogbcbcepd/opgen_generated_files/bg.js
Line 332     XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
    XMLHttpRequest.prototype.responseText = 'sensitive_responseText'
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkkjkmoplgfbkpbbnkjojabogbcbcepd/opgen_generated_files/bg.js
Line 1059                    var $result = JSON.parse(xmlhttp.responseText);
    JSON.parse(xmlhttp.responseText)
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkkjkmoplgfbkpbbnkjojabogbcbcepd/opgen_generated_files/bg.js
Line 1304                        return shops[i];
    shops[i]
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkkjkmoplgfbkpbbnkjojabogbcbcepd/opgen_generated_files/bg.js
Line 1268             var $cookieFlag = self.cookie.isActivated($shop.id);
    $shop.id
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkkjkmoplgfbkpbbnkjojabogbcbcepd/opgen_generated_files/bg.js
Line 1228             var $html = '<img id="shlogo" data-time="' + $seconds + '" data-shopid="' + $shop.id + '" src="' + logo + '" />' +
                '<a href="' + $shop.url + '?dest=' + $tabUrl + '" class="' + $classColor + '">' + $msg + '</a>' +
                '<img id="shShlogo" src="' + $shop.logo.url + '" />' +
                '<span class="nomore"><input type="checkbox" id="nomore" value="1" style="visibility: visible;">' +
                'Ocultar este aviso en esta web</span>' +
                '<span class="shpClose"><a href="#" id="closeBadge">x</a></span>';
    $html = '...'
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkkjkmoplgfbkpbbnkjojabogbcbcepd/opgen_generated_files/bg.js
Line 1241             $code += 'element.innerHTML=\'' + DOMPurify.sanitize($html) + '\';document.body.insertAdjacentElement("beforeend", element);}';
    DOMPurify.sanitize($html)
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hkkjkmoplgfbkpbbnkjojabogbcbcepd/opgen_generated_files/bg.js
Line 1241             $code += 'element.innerHTML=\'' + DOMPurify.sanitize($html) + '\';document.body.insertAdjacentElement("beforeend", element);}';
    $code += 'element.innerHTML=\'' + DOMPurify.sanitize($html) + '\';document.body.insertAdjacentElement("beforeend", element);}'
```

**Code:**

```javascript
// Background script - Hardcoded Shoppiday backend URL (line 1025)
this.baseUrl = 'https://www.shoppiday.es/toolbar/';

// Fetches shop list from hardcoded backend (lines 1051-1072)
this.getShopsFromApi = function (callBack) {
    var $url = self.baseUrl + 'stores.json';  // ← Hardcoded backend URL
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.withCredentials = true;
    xmlhttp.open('GET', $url, true);
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            try {
                var $result = JSON.parse(xmlhttp.responseText);  // Parse response
                if ($result) {
                    self.api_data_cache['shops'] = $result;  // Store shops from backend
                    self.api_data_cache["expire"] = Date.now() + 3600000;
                    if (callBack) {
                        callBack();
                    }
                }
            } catch (exception) {}
        }
    };
    xmlhttp.send();
};

// Gets shop data from cache for current tab URL (lines 1296-1310)
function getShopForURL(link) {
    var shops = self.api.getValue("shops");  // Get cached shops from backend
    if (shops) {
        var tld = getDomain(link);
        var subdomain = getSubDomain(link);
        if (tld != null || subdomain != null) {
            for (var i in shops) {
                if (shops[i].domain == tld || shops[i].domain == subdomain) {
                    return shops[i];  // Returns shop from backend data
                }
            }
        }
    }
    return null;
}

// Uses shop data to inject badge into page (lines 1220-1246)
function setBadgeOnWeb($shop, $tabId, $tabUrl, $cookieFlag) {
    if (self.cookie.isShowed($shop.id) == false) {
        var $msg = chrome.i18n.getMessage($cookieFlag && self.api.getUserId() > 0 ? 'btnBadgeOn' : 'btnBadgeOff', [$shop.reward]);
        var $classColor = $cookieFlag ? "on" : "off";
        var $seconds = $cookieFlag ? 10 : 30;
        var logo = 'https://images.shoppiday.es/assets/logo-32.png';

        // Constructs HTML using shop data from backend
        var $html = '<img id="shlogo" data-time="' + $seconds + '" data-shopid="' + $shop.id + '" src="' + logo + '" />' +
            '<a href="' + $shop.url + '?dest=' + $tabUrl + '" class="' + $classColor + '">' + $msg + '</a>' +
            '<img id="shShlogo" src="' + $shop.logo.url + '" />' +
            '<span class="nomore"><input type="checkbox" id="nomore" value="1" style="visibility: visible;">' +
            'Ocultar este aviso en esta web</span>' +
            '<span class="shpClose"><a href="#" id="closeBadge">x</a></span>';

        // Constructs code to execute
        var $code = 'if(null == document.getElementById("shpBtn")){' +
            'var element = document.createElement(\'div\');' +
            'element.id="shpBtn";'+
            'element.className +="noshow";';
        if (self.api.getUserId() <= 0) {
            $code += 'element.className += " dologin";';
        }

        // HTML is sanitized with DOMPurify before injection
        $code += 'element.innerHTML=\'' + DOMPurify.sanitize($html) + '\';document.body.insertAdjacentElement("beforeend", element);}';

        chrome.tabs.insertCSS($tabId, {file: 'libs/badge.css'});
        chrome.tabs.executeScript($tabId, {code: $code});  // Executes code with backend data
        chrome.tabs.executeScript($tabId, {file: 'libs/badge.js'});
        self.cookie.setShowed($shop.id);
    }
}
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (trusted infrastructure). The extension fetches a shop list from its own hardcoded backend server (https://www.shoppiday.es/toolbar/stores.json) and uses the shop data (including shop.url and shop.logo.url) to construct HTML that is injected via chrome.tabs.executeScript. Although the HTML is properly sanitized with DOMPurify before injection, the core issue is that the data comes FROM a hardcoded backend URL. According to the methodology, data FROM hardcoded backend URLs is considered trusted infrastructure - compromising Shoppiday's backend server is an infrastructure security issue, not an extension vulnerability. There is no external attacker control over the XHR request URL or the shop data being used in executeScript.
