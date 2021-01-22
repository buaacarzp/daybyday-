import argparse
parser = argparse.ArgumentParser(description="Websockets start ")
parser.add_argument('-ip','-i',type=str,help="input the ip address!")#,action="store_false")
parser.add_argument('-port','-p',type=str,help="inputs the ip port!")#,action="store_false")
args = parser.parse_args()
assert (args.ip is not None and args.port is not None) , "please input the ip and port"
