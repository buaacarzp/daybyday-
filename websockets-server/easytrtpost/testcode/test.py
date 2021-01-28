import argparse

def pre_parsers(parser):
    parser.add_argument('-ip','--ip',type=str,help="input the ip address!")#,action="store_false")
    parser.add_argument('-port','--port',type=str,help="inputs the ip port!")#,action="store_false")
    parser.add_argument('-debug','--debug',help="choose debug or release",action="store_true")
    args = parser.parse_args()
    assert (args.ip is not None and args.port is not None) , "\nError:Please input the ip and port!"
    return args

parser = argparse.ArgumentParser(description="Websockets start ")
args = pre_parsers(parser)
IP,PORT,DEBUG = args.ip,args.port,args.debug
print(IP,PORT,DEBUG)