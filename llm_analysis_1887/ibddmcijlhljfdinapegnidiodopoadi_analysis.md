# CoCo Analysis: ibddmcijlhljfdinapegnidiodopoadi

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 6 (all chrome_storage_local_set_sink)

---

## Sink 1-6: jQuery_get_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ibddmcijlhljfdinapegnidiodopoadi/opgen_generated_files/bg.js
Line 1048: `shops = JSON.parse(res).webshops;`
Line 1087: `blocked = shops.filter(function(x){ return x.extension == 0; })`
Line 1151: `shops = shops.filter(function(x){ return x.extension == 1 && x.extension_auto_redirect == 1; })`

Storage operations:
Line 1159: `chrome.storage.local.set({shops:shops});`
Line 1160: `chrome.storage.local.set({blocked:blocked});`

**Code:**

```javascript
var endpoint = "https://api.sponsorkliks.com/v1.0/";

function getShops(callback){
  // First jQuery.get to hardcoded backend
  $.get(endpoint+"?call=webshops_club&show=json",function(res){
    shops = JSON.parse(res).webshops;

    for(var x of shops){
      x.id = parseInt(x.link.match(/shop_id=\d+/gi)[0].split("=")[1]);
    }

    // Second jQuery.get to hardcoded backend
    $.get(endpoint+"get_shops.php",function(res){
      var s = JSON.parse(res);

      for(var x of shops){
        var u = s.filter(function(y){
          return y.shopnr == x.id;
        })
        if(u.length){
          var url2 = u[0].url;
          if(!url2 || typeof url2 == "undefined"){
            url2 = "";
          }
          url2 = url2.replace(/\http\:\/\/|https\:\/\//gi,"");
          if(url2[url2.length-1]=="/"){
            url2 = url2.substring(0,url2.length-1);
          }
          x.url = url2;
        } else {
          x.url = "";
        }
      }

      // Filter shops based on extension settings
      blocked = shops.filter(function(x){
        return x.extension == 0;
      })

      shops = shops.filter(function(x){
        return x.extension == 1 && x.extension_auto_redirect == 1;
      })

      if(callback){
        callback(shops,blocked);
      }

      // Store in chrome.storage.local
      chrome.storage.local.set({shops:shops});
      chrome.storage.local.set({blocked:blocked});
    })
  })
}

getShops();
setInterval(getShops,1000*60*20);
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows from hardcoded backend URL (api.sponsorkliks.com) to chrome.storage.local. The extension fetches shop/webshop data from its own trusted backend infrastructure and stores it locally for the extension's functionality (auto-redirect and blocking features). There is no external attacker trigger - this is internal extension logic that runs on startup and periodically. The data originates from the extension developer's own backend servers, which are trusted infrastructure. This is not an attacker-controllable flow.
