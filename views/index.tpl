<html>
    <head>
      <title>Arch Package Feed</title>
    </head>
    <body>
        <h1>Get your personal Arch Package Feed</h1>
        <form action="/feed" method="get">
            <h2>Filter by architecture</h2>
            <input type="checkbox" name="arch" value="i686">i686</br>
            <input type="checkbox" name="arch" checked="yes" value="x86_64">x86_64<br>
            <input type="checkbox" name="arch" checked="yes" value="any">Any</br>

            <h2>Filter by repository</h2>
            <input type="checkbox" name="repos" checked="yes" value="core">Core</br>
            <input type="checkbox" name="repos" checked="yes" value="extra">Extra</br>
            <input type="checkbox" name="repos" checked="yes" value="community">Community<br>
            <input type="checkbox" name="repos" checked="no"  value="testing">Testing</br>
            <input type="checkbox" name="repos" checked="yes" value="aur">AUR</br>

            <h2>Include the following information</h2>
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

            <input type=submit value="Get the feed">
        </form>

        <h2>Thanks</h2>
    </body>
</html>
