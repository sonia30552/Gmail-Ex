

function getConfig() {
  return JSON.parse(ScriptProperties.getProperty('config')) ||
    { numDays: 7, markUnread: false, addUnsnoozed: false };
}

function setConfig(config) {
  ScriptProperties.setProperty('config', JSON.stringify(config));
}

function isInstalled() {
  return ScriptApp.getProjectTriggers().length != 0;
}

function install(config) {
  if (!isInstalled()) {
    ScriptApp.newTrigger('moveSnoozes').timeBased().atHour(0).nearMinute(0).everyDays(1).create();
  }
  createOrGetLabels(config);
  setConfig(config);
}

function uninstall() {
  ScriptApp.getProjectTriggers().map(function(trigger) {
    ScriptApp.deleteTrigger(trigger);
  });
}

function doGet() {
  var t = HtmlService.createTemplateFromFile('ui');
  var config = getConfig();
  for (var key in config) t[key] = config[key];
  t.installed = isInstalled();
  return t.evaluate().setSandboxMode(HtmlService.SandboxMode.NATIVE);
}

function createOrGetLabels(config) {
  var existingLabels = {};
  GmailApp.getUserLabels().map(function(label) {
    existingLabels[label.getName()] = label;
  });  
  function getLabel(name) {
    return existingLabels[name] || GmailApp.createLabel(name);
  };
  var labels = {
    Snooze: getLabel('Snooze'),
    Unsnoozed: config.addUnsnoozed ? getLabel('Unsnoozed') : undefined,    
  };
  for (var i = 1; i <= config.numDays; ++i) {    
    labels[i] = getLabel('Snooze/Snooze ' + i + ' days');
  }
  return labels;
}

function moveSnoozes() { 
  var config = getConfig();
  var labels = createOrGetLabels(config);
  var oldLabel, newLabel, page;
  for (var i = 1; i <= config.numDays; ++i) {
    page = null;
    // Get threads in 'pages' of 100 at a time
    while(!page || page.length == 100) {
      page = labels[i].getThreads(0, 100);
      if (page.length > 0) {
        if (i > 1) {
          // Move the threads into 'today’s' label
          labels[i - 1].addToThreads(page);
        } else {
          // Unless it’s time to unsnooze it
          GmailApp.moveThreadsToInbox(page);
          if (config.markUnread) {
            GmailApp.markThreadsUnread(page);
          }
          if (config.addUnsnoozed) {
            labels.Unsnoozed.addToThreads(page);
          }          
        }     
        // Move the threads out of 'yesterday’s' label
        labels[i].removeFromThreads(page);
      }  
    }
  }
}
© 2020 GitHub, Inc.
Terms
Privacy
Security
Status
Help
Contact GitHub
Pricing
API
Training
Blog
About
