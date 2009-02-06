import s60twitter

api = s60twitter.TwitterApi("marcelobarros",
                            "xxx",
                            "http://barros:yyy@192.168.1.40:8080")

ftl = api.get_friends_timeline()

for f in ftl:
    txt = f[u'text']
    usr = f[u'user'][u'name']
    msg = u"Mensagem de " + usr + u". " + txt
    print msg

    
    




