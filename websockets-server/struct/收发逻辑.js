    send(id,asStr) {
            let lMySelf = this;
            let  bytes = Utils.encodeUtf8(asStr);
            let buffer = new ArrayBuffer(bytes.length + 8);
            let view   = new DataView(buffer);
            view.setUint32(0,id);
            view.setUint32(4, bytes.length);
            for (let  i = 0; i < bytes.length; i++) {
                view.setUint8(i + 8, bytes[i]);
            }
            if(this.websocket.readyState === 1) {
                this.websocket.send(view);
            }else if(this.websocket.readyState ===0){
                Utils.notify("正在连接媒体服务器稍后再试");
                // triggerError();

            }else {
                this.connect();
                Utils.notify("正在连接媒体服务器稍后再试");
                // triggerError();
            }
            console.log("send:=> "  + id +"  " + asStr);
            // function triggerError() {
            //      if(lMySelf.fOnError) {
            //          setTimeout(()=>{
            //              lMySelf.fOnError();
            //          },100);
            //      }
            // }
        }
        doReceive(buffer) {
            let  receive =[];
            receive = receive.concat(Array.from(new Uint8Array(buffer)));
            if (receive.length < 8) {
                return;
            }
            let ldview =new DataView(new Uint8Array(receive).buffer);
            let lCommandID = ldview.getUint32(0);
            let length = ldview.getUint32(4);
            if (receive.length < length + 8) {
                return;
            }
            let  bytes = receive.slice(8, length + 8);
            let lsStr = Utils.decodeUtf8(bytes);
            console.log("receive--->"+ lCommandID+"  "+lsStr);
            if(Utils.isEmpty(lsStr)) {
                console.log("no data received");
                return;
            }
            let lResult = new ObjResult(lCommandID,lsStr);

            if(this.fOnResult) {
                this.fOnResult(lResult);
            }
        }