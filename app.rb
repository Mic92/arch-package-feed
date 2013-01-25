require 'rss'
require 'open-uri'
require 'json'
require 'sinatra'
require 'slim'

def get_feed
  feed_url = "https://aur.archlinux.org/rss/"
  aur_url = "https://aur.archlinux.org/rpc.php?type=multiinfo"

  open(feed_url) do |rss|
    feed = RSS::Parser.parse(rss)
    queries = feed.items.map { |i| "&arg[]=#{i.title}" }
    open("#{aur_url}#{queries.join}") do |json|
      pkgs = JSON.load(json)["results"]
      pkgs_by_name = Hash[pkgs.map { |p| [p["Name"], p] }]

      feed.channel.generator = "AUR-Feed-Enhancer"

      feed.items.each do |item|
        pkg = pkgs_by_name[item.title]
        item.description += "\n version: #{pkg["Version"]}"
        item.description += "\n maintainer: #{pkg["Maintainer"]}"
        item.description += "\n votes: #{pkg["NumVotes"]}"
        item.description += "\n license: #{pkg["License"]}"
        item.description += "\n aur: #{item.link}"
        item.link = pkg["URL"]
      end
      return feed.to_s
    end
  end
end

get '/rss.xml' do
  return get_feed
end

get "/" do
  slim :index
end

__END__

@@layout
doctype html
html
  head
    meta charset="utf-8"
    title Just Do It
    link rel="stylesheet" media="screen,  projection" href="/styles.css"
    /[if lt IE 9]
      script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"
  body
    == yield


@@index
h1 Enhanced AUR Package feed
a href="/rss.xml" Get it here
h2 Additions to the origin feed:
ul
  li default link is the project url instead of the AUR url
  li add version number, package maintainer, category, license, votes
