"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from MyFlask import app



@app.route('/geturl',methods=['GET'])
def getUrl():
    sCorpID = "wxf29b16f0c55ae5f2"
    sToken = "wzgyXSnxoKNDRb5yoJVtLk4XNkXbKRFm"
    sEncodingAESKey = "7fJlKWPElDjOtXbYkpkLAeac6eVAuUrrYM2dBWeHvlt"
    wxcpt = WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
    params = request.args
    sVerMsgSig = params.get('msg_signature')
    sVerMsgTimeStap = params.get('timestamp')
    sVerNonce= params.get('nonce')
    sVerEchoStr = params.get('echostr')
    ret,sEchoStr = wxcpt.VerifyURL(sVerMsgSig,sVerMsgTimeStap,sVerNonce,sVerEchoStr)
    if ret!=0:
        print ret
        return None
    else:
        return sEchoStr


