CKEDITOR.plugins.add("addTestButton", {
  icons:
    "https://w7.pngwing.com/pngs/308/74/png-transparent-computer-icons-setting-icon-cdr-svg-setting-icon.png", // The icon for the button. It must be placed in the "icons" folder in the plugin folder.
  init: function (editor) {
    editor.addCommand("addTestButton", {
      exec: function (editor) {
        var now = new Date();
        editor.insertHtml("[KEEN_ANSWER/]");
      },
    });
    editor.ui.addButton("addTestButton", {
      icon: "https://w7.pngwing.com/pngs/308/74/png-transparent-computer-icons-setting-icon-cdr-svg-setting-icon.png",
      label: "Insert Timestamp",
      command: "addTestButton",
      toolbar: "insert",
    });
  },
});
