import imaplib
import email 
def decode_receiver(str_in):
    print(str_in)
    str_in = str_in.split()
    lens = len(str_in)
    print(str_in,lens)
    for k in range(lens):
        value,charset= email.header.decode_header(str_in[k])[0]
        print(value)
        if not charset:
    #         print(value,charset)
            value = value.decode(charset)
        
        # return value
    return      


    #[(b'\xe5\x85\xa8\xe4\xbd\x93\xe8\x80\x81\xe5\xb8\x88', 'utf-8'),
    #(b' <teacher_all@buaa.edu.cn>, ', None), 
    #(b'\xe5\x85\xa8\xe4\xbd\x93\xe5\xad\xa6\xe7\x94\x9f', 'utf-8'), 
    #(b' <student_all@buaa.edu.cn>', None)]

def decode_str(str_in):
    '''
    [(b'\xe3\x80\x90\xe5\x9b\xbe\xe4\xb9\xa6\
    xe9\xa6\x86\xe3\x80\x91\xe5\x9b\xbe\xe4\
    xb9\xa6\xe9\xa6\x86\xe5\x85\xb3\xe4\xba\
    x8e\xe5\x8f\x82\xe5\x8a\xa0\xe7\xac\xac25\
    xe5\xb1\x8a\xe5\x9b\xbd\xe9\x99\x85\xe5\x9b\
    xbe\xe4\xb9\xa6\xe5\x8d\x9a\xe8\xa7\x88\xe4\xbc\
    x9a\xe9\x80\x9a\xe7\x9f\xa5', 'utf-8')]
    '''
    print(email.header.decode_header(str_in))
    # value,charset= email.header.decode_header(str_in)[0]
    # if charset:
    #     print("charset:",charset)
    #     value = value.decode(charset)
    #     print('value:',value)
    # else:
    #     print(f"!!!!key={str_in}不需要解析")
    # return value
conn = imaplib.IMAP4_SSL(port = '993',host = "imap.buaa.edu.cn")
print("server")
conn.login('zpselfcontro1@buaa.edu.cn','zhou59467')
print("login")
conn.select()
_type,data = conn.search(None,'ALL')
newlist = data[0].split()
# print(newlist)
#第一封邮件
_type ,data = conn.fetch(newlist[2],'(RFC822)')
msg = email.message_from_string(data[0][1].decode("utf-8"))
# print(msg)
#用get()获取标题并进行初步的解码。
sub = msg.get('subject')
sender = msg.get('From')
receiver = msg.get('To')
copy = msg.get('Cc')
# alls = [sub,sender,receiver,copy]
alls = [receiver]

for key in alls:
    # print('key:',key)
    decodeing = decode_receiver(key)
    
#     #打印标题
#     # print(decodeing.decode('utf-8'))
# for part in msg.walk():
#     # print("--->hei")
#     # 如果ture的话内容是没用的
#     if not part.is_multipart():            
#         htmlMsg = part.get_payload(decode=True)
#         # print(htmlMsg)
#         result = htmlMsg.decode('utf-8')
#         print(result)
#         # 解码出文本内容，直接输出来就可以了
# conn.close()
# conn.logout()
# print("over")