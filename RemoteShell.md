# Instructions #

For using the remote shell over WiFi, download and install [remoteshell.sis](http://wordmobi.googlecode.com/files/remoteshell.sis). Do not forget to install the python interpreter before installing remote shell.

After, type the following in any Linux console:

```
stty raw -echo ; nc -l -p 1025 ; stty sane
```

Run remote shell in your phone and use your Linux machine IP in the config dialog. Your phone will show the connect dialog. After connecting you should see the Python console running in your Linux console.

If your mobile phone does not have WiFi, try some bluetooth console.

If you like to build your own remote console or run it inside another script, use the following code excerpt (use your Linux box IP):

```
import btconsole
from socket import *

sock = socket(AF_INET,SOCK_STREAM)
sock.connect(("10.0.0.10",1025))
btconsole.run_with_redirected_io(sock,btconsole.interact, None, None, locals())
```