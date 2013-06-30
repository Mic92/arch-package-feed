<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>{{ d['title'] }}</title>
    <subtitle>{{ d['subtitle'] }}</subtitle>
    <link rel="alternate" type="text/html" href="{{ d['site_url'] }}" />
    <link rel="self" type="application/atom+xml" href="{{ d['feed_url'] }}" />
    <id>{{ d['feed_url'] }}</id>
    <updated>{{ d['date_updated'] }}</updated>

    %for entry in entries:
    <entry>
        <title>{{! entry.name }}</title>
        <link rel="alternate" type="text/html" href="{{entry.url if feed_link == "project_url" else entry.arch_url() }}" />
        <id>{{ entry.atom_id() }}</id>
        <published>{{ entry.last_update }}</published>
        <updated>{{ entry.last_update }}</updated>
        <author>
            <name>{{ entry.maintainers }}</name>
            <uri>{{ entry.url }}</uri>
        </author>
        <content type="html" xml:base="{{d['site_url']}}" xml:lang="en">
          <![CDATA[
          %for key, value in entry.to_feed_item(includes):
            %if key == "Url" or key == "Package Url":
            <b>{{ key }}:</b> <a href={{ value }}>{{ value }}</a><br/>
            %else:
            <b>{{ key }}:</b> {{ value }}<br/>
            %end
          %end
          ]]>
        </content>
    </entry>
    %end
</feed>
