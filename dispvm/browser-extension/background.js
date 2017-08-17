browser.contextMenus.create({
  id: "open-in-new-vm",
  title: "Open Link in New VM",
  contexts: ["link"]
});

browser.contextMenus.onClicked.addListener(function(info, tab) {
  console.log("onClicked");
  switch (info.menuItemId) {
    case "open-in-new-vm":
      console.log(info.linkUrl);
      browser.runtime.sendNativeMessage(
        "quboid_native_messaging_host",
        info.linkUrl);
      break;
  }
})
