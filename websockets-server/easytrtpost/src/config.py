_WEB_SOCKET_PROTOCOL ={
    "PROTOCOL1":{
        "receive":{},
        "send1":{
            "description":"流媒体描述信令协议数据包",
            "id":0,
            "information":"当客户端刚刚连接到服务器后，服务器发送这个协议数据包来通知客户端关于流媒体服务器的一些信息。（保留）",
            "JSON":{},
            "other":""
            },
        "send2":{
            
        }
    },
    "PROTOCOL2":{
        "receive":{
            "description":"人脸识别准备信令协议数据包(1001)",
            "id":1001,
            "information":"客户端向服务端发送",
            "JSON":{"Task":"FaceDetection","op":"prepare","CaptureID":"0101","CapturePath":"","ModelPath":"","SourceFile":""},
            "other":"Task 任务类型人脸检测 ,op为当前执行的动作，CaptureID为采集设备ID，CapturePath:设备IP，modelPath:模型地址，sourcefile:存储的人脸文件"
        },
        "send1":{
            "description":"流媒体描述信令协议数据包",
            "id":1001,
            "information":"服务端到客户端发送",
            "JSON":{"Task":"FaceDetection","CaptureID":"0101","op":"start","result":"ok" ,"error":"question"},
            "other":""

        }, #初始化模型
        "send2":{

        }
    },
     "PROTOCOL3":{
        "receive":{
            "description":"人脸识别开始信令协议数据包(1002)",
            "id":1002,
            "information":"客户端向服务端发送",
            "JSON":{"Task":"FaceDetection","op":"start","CaptureID":"0101","duration":""},
            "other":"Task 任务类型人脸检测/姿态估计 ,op为当前执行的动作，CaptureID为采集设备ID，\
                    CapturePath:设备IP，duration:检测的时间（帧率25fps,40ms一帧）。"
        },   
        "send1":{
            "description":"人脸识别开始信令协议数据包(1002)",
            "id":1002,
            "information":"服务端到客户端发送",
            "JSON":{"Task":"FaceDetection","CaptureID":"0101","op":"start","result":"ok" ,"error":"question"},
            "other":"响应"

        },#执行算法
        "send2":{

        }
    },
        
    "PROTOCOL4":{
        "receive":{
            "description":"人脸识别停止信令协议数据包(1003)",
            "id":1003,
            "information":"客户端向服务端发送",
            "JSON":{"Task":"FaceDetection","CaptureID":"0101","op":"stop","CaptureID":"0101"},
            "other":"Task 任务类型人脸检测/姿态估计 ,op为当前执行的动作，CaptureID为采集设备ID，CapturePath:设备IP"
        },
        "send1":{
            "description":"人脸识别停止信令协议数据包(1003)",
            "id":1003,
            "information":"服务端到客户端发送",
            "JSON":{"Task":"FaceDetection","CaptureID":"0101","op":"stop","result":"ok","error":"question" },
            "other":"响应"
        },#明白 销毁模型对象，完成或者取消
        "send2":{

        }
    },
    "PROTOCOL5":{
        "receive":{
            "description":"人脸识别停止信令协议数据包(1004)",
            "id":1004,
            "information":"客户端向服务端发送",
            "JSON":{"Task":"FaceDetection","CaptureID":"0101","op":"stop","CaptureID":"0101"},
            "other":"Task 任务类型人脸检测/姿态估计 ,op为当前执行的动作，CaptureID为采集设备ID，CapturePath:设备IP"
        },
        "send1":{

        },##明白 销毁模型对象
        "send2":{

        }

    },
    "PROTOCOL6":{
        "receive":{
            "description":"考核（姿态估计）准备信令协议数据包(2001)",
            "id":2001,
            "information":"客户端向服务端发送",
            "JSON":{"Task":"examine1","op":"prepare","CaptureID":"0101","CapturePath":"","ModelPath":"","duration":"","level":""},
            "other":"Task 考核任务名 ,op为当前执行的动作，CaptureID为采集设备ID，CapturePath:设备IP，modelPath:模型地址,duration:检测的时间（帧率25fps,40ms一帧）,检测等级1-5默认是5"
        },
        "send1":{
            "description":"考核（姿态估计）准备信令协议数据包(2001)",
            "id":2001,
            "information":"服务端到客户端发送",
            "JSON":{"task":"examine1","CaptureID":"0101","op":"start","result":"ok","error":"question" },
            "other":"响应"
        },#建立连接，加载模型
        "send2":{

        }
    },
    "PROTOCOL7":{
        "receive":{
            "description":"考核（姿态估计）开始信令协议数据包(2002)",
            "id":2002,
            "information":"客户端向服务端发送",
            "JSON":{"Task":"examine1","op":"start","CaptureID":"0101"},
            "other":"Task 任务类型人脸检测/姿态估计 ,op为当前执行的动作，CaptureID为采集设备ID"
        },
        "send1":{
            "description":"考核（姿态估计）开始信令协议数据包(2002)",
            "id":2002,
            "information":"服务端到客户端发送",
            "JSON":{"task":"examine1","CaptureID":"0101","op":"start","result":"ok","error":"question" },
            "other":"响应"
        },
        "send2":{
            "description":"考核（姿态估计）开始信令协议数据包(2002)",
            "id":2222,
            "information":"服务端到客户端发送",
            "JSON":{"task":"examine1","CaptureID":"0101","op":"start","result":"ok","error":"question" },
            "other":"检测结果,status ：  状态   0 正确动作，  -1 为终止，曲臂悬垂 出现错误停止,其他为具体的错误编码。\
                    total ：累计动作数，或者曲臂悬垂的总毫秒数。 \
                    time  ：从开始到消息时刻的时长，单位为毫秒。  用于回看录像用。"
        } #直接发送结果，和人脸识别不一样
    },
    "PROTOCOL8":{
        "receive":{
            "description":"考核（姿态估计）停止信令协议数据包(2003)",
            "id":2003,
            "information":"客户端向服务端发送",
            "JSON":{"Task":"examine1","op":"stop","CaptureID":"0101"},
            "other":"Task 任务类型人脸检测/姿态估计 ,op为当前执行的动作，CaptureID为采集设备ID，CapturePath:设备IP，"
        },
        "send1":{
            "description":"考核（姿态估计）准备信令协议数据包(2001)",
            "id":2003,
            "information":"服务端到客户端发送",
            "JSON":{"Task":"examine1","op":"stop","result":"ok","error":"question" },
            "other":"响应"
        },
        "send2":{
        } #模型销毁
    },
    "PROTOCOL9":{
        "receive":{
            "description":"考核（姿态估计）关闭信令协议数据包(2004)",
            "id":2004,
            "information":"客户端向服务端发送",
            "JSON":{"Task":"FaceDetection","CaptureID":"0101","op":"stop","CaptureID":"0101"},
            "other":"Task 任务类型人脸检测/姿态估计 ,op为当前执行的动作，CaptureID为采集设备ID，CapturePath:设备IP"
        },#python对象销毁掉
        "send1":{
        },
        "send2":{
        }
    },
    "PROTOCOL10":{
        "receive":{},
        "send1":{
            "description":"服务器异常错误(401)",
            "id":401,
            "information":"客户端向服务端发送",
            "JSON":{},
            "other":"载荷文本，不用解析，用于出问题，找原因。"
        },
        "send2":{
        }
    },         

}