import json 
import struct #https://docs.python.org/3/library/struct.html#format-characters
import sys 
def pack(ID,DATA):
    '''
    input: int,dict
    return: bytes
    '''
    DATA_JSON = json.dumps(DATA)
    BYTE_DATA_JSON = bytes(DATA_JSON,encoding='utf8') 
    BYTE_LEN_DATA_json = len(DATA_JSON)
    _PACK_DATA = struct.pack(f"ii{BYTE_LEN_DATA_json}s",ID,BYTE_LEN_DATA_json,BYTE_DATA_JSON) #return bytes
    return _PACK_DATA

def unpack(_PACK_DATA):
    '''
    input: bytes
    return bytes
    '''
    _ID,LENDATA = struct.unpack('ii',_PACK_DATA[:8])
    _BYTE_DATA_JSON = struct.unpack(f'{LENDATA}s',_PACK_DATA[8:8+LENDATA])[0]
    return _ID,LENDATA,_BYTE_DATA_JSON

def decode_uppack(_PACK_DATA):
    '''
    input: struct bytes
    output: dict
    '''
    _ID, _LENDATA, BYTE_DATA_JSON = unpack(_PACK_DATA)
    Str_DATA = BYTE_DATA_JSON.decode(encoding='utf8')
    _DICT_Str = json.loads(Str_DATA)
    return _ID, _LENDATA, _DICT_Str
if __name__ =="__main__":
    ID = 1001
    DATA ={"Task":"FaceDetection",
            "Op":"prepare",
            "CaptureID":10,
            "CapturePath":"/usr/local/tnkhxt/tmp/tmp5447557840596578523.jpg",
            "ModelPath":"/usr/local/tnkhxt/res/unit_8_8/rm_10/blb/8_10_15348_1/data.npy",
            "PicturePath":"",
            "SourceFile":"",
            "Task2":"FaceDetection",
            "Op2":"prepare",
            "CaptureID2":10,
            "CapturePath2":"/usr/local/tnkhxt/tmp/tmp5447557840596578523.jpg",
            "ModelPath2":"/usr/local/tnkhxt/res/unit_8_8/rm_10/blb/8_10_15348_1/data.npy",
            "PicturePath2":"",
            "SourceFile2":""}
    _data = pack(ID,DATA)
    res = decode_uppack(_data)
    print(res)


