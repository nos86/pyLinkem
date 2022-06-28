from imp import reload
import sys
sys.path.append('../') 

import router
obj = reload(router).LinkemRouter("192.168.102.1", "guest", "linkem123")
l = obj.login()
pass
