<!DOCTYPE html>
<html>
    <head>
      <title>Arch Package Feed</title>

      <meta charset="utf-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
      <meta name="description" content="">
      <meta name="viewport" content="width=device-width">

      <!--[if lt IE 9]>
        <script src="//html5shiv.googlecode.com/svn/trunk/html5.js"></script>
        <script>window.html5 || document.write('<script src="static/html5shiv.js"><\/script>')</script>
      <![endif]-->
      <link href="/static/styles.css" media="screen, projection" rel="stylesheet"/>
      <link rel="stylesheet" href="/static/gh-fork-ribbon.css" media="screen, projection"/>
    </head>
    <body>
       <div class="github-fork-ribbon-wrapper right">
        <div class="github-fork-ribbon">
          <a href="https://github.com/Mic92/arch-package-feed">Fork me on GitHub</a>
        </div>
       </div>
        <div id="content">
            <div class="header">
              <a href="/"><img alt="logo" width="100pt" height="100pt" src="/static/archlogo.png"/></a>
              <h1>Arch Package Feed</h1>
              <h2>Get your customized feed</h2>
            </div>
            <form action="/feed" method="get">
              <fieldset>
                <h3>Filter by architecture</h3>
                <input type="checkbox" name="arch" value="i686">i686</br>
                <input type="checkbox" name="arch" checked="yes" value="x86_64">x86_64<br>
                <input type="checkbox" name="arch" checked="yes" value="any">Any</br>
              </fieldset>

              <fieldset>
                <h3>Filter by repository</h3>
                <input type="checkbox" name="repos" checked="yes" value="core">Core</br>
                <input type="checkbox" name="repos" checked="yes" value="extra">Extra</br>
                <input type="checkbox" name="repos" checked="yes" value="community">Community<br>
                <input type="checkbox" name="repos" checked="no"  value="testing">Testing</br>
                <input type="checkbox" name="repos" checked="yes" value="aur">AUR</br>
              </fieldset>

              <fieldset>
                <h3>Include the following information</h3>
                <input type="checkbox" name="includes" checked="yes" value="name">Name</br>
                <input type="checkbox" name="includes" checked="yes" value="version">Version</br>
                <input type="checkbox" name="includes" checked="yes" value="description">Description</br>
                <input type="checkbox" name="includes" value="arch">Arch</br>
                <input type="checkbox" name="includes" checked="yes" value="repo">Repository</br>
                <input type="checkbox" name="includes" checked="yes" value="arch_url">Arch Repository Url</br>
                <input type="checkbox" name="includes" checked="yes" value="url">Project Url</br>
                <input type="checkbox" name="includes" value="last_update">Last Update</br>
                <input type="checkbox" name="includes" value="compressed_size">Compressed Size</br>
                <input type="checkbox" name="includes" value="installed_size">Installed Size<br>
                <input type="checkbox" name="includes" value="depends">Depends</br>
                <input type="checkbox" name="includes" checked="yes" value="license">License</br>
                <input type="checkbox" name="includes" value="maintainers">Maintainers</br>
              </fieldset>

              <input type=submit value="Get the feed">
            </form>

            <h3>Thanks</h3>
            <script id='flattrbtn' defer>
            (function(i){var f,s=document.getElementById(i);f=document.createElement('iframe');f.src='//api.flattr.com/button/view/?uid=Mic92&button=compact&url='+encodeURIComponent(document.URL);f.title='Flattr';f.height=20;f.width=110;f.style.borderWidth=0;s.parentNode.insertBefore(f,s);})('flattrbtn');
            </script>
        </div>

        <script type="text/javascript">
          var pkBaseURL = (("https:" == document.location.protocol) ? "https://piwik.higgsboson.tk/" : "http://piwik.higgsboson.tk/");
          document.write(unescape("%3Cscript src='" + pkBaseURL + "piwik.js' type='text/javascript'%3E%3C/script%3E"));
        </script>
        <script type="text/javascript">
        try {
          var piwikTracker = Piwik.getTracker(pkBaseURL + "piwik.php", 1);
          piwikTracker.trackPageView();
          piwikTracker.enableLinkTracking();
        } catch( err ) {}
        </script>
        <noscript>
          <img src="http://piwik.higgsboson.tk/piwik.php?idsite=1" style="border:0" alt=""></img>
        </noscript>
    </body>
</html>
