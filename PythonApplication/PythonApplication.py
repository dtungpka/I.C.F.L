from fbchat import Client
from fbchat.models import *
import json
cookies = {"sb":"JzeGYzeAAzOJrysk6iSAJq4b","dpr":"1.25","datr":"JzeGYzmTTFTP8LzJwr55vJky","locale":"vi_VN","wd":"1536x746","c_user":"100049863371978","xs":"20%3AbGj5Vl32g-2-Iw%3A2%3A1669740403%3A-1%3A9629","fr":"0zjTOwiCrDF4rfMCA.AWVPwEcHGvH8Xva1dXjqQjOk0_I.Bjhjcn.B_.AAA.0.0.BjhjmI.AWUQtdm0Xb8","presence":"C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1669740939193%2C%22v%22%3A1%7D"}

useragent =  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62"
client = Client("duongdoantung2k3@gmail.com", "@TUNG003",user_agent=useragent)
print("Own id: {}".format(client.uid))

client.send(Message(text="Hi me!"), thread_id=client.uid, thread_type=ThreadType.USER)

client.logout()