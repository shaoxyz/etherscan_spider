# -*- coding:utf-8 -*-
# Python3
# File    : new_app.py
# Time    : 2018/7/8 19:35
# Author  : Shaweb

import json, sys
from flask import Flask, request, Response

from etherscan import txHash, balance, tokenBasicInfo, tokenHolders, tokenTransaction, tokenTransactionForAccount, gasPrice

app = Flask(__name__)

def returnjsonresp(respbody):
    resp = Response(json.dumps(respbody))
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route("/txHash", methods=['POST'])
def query_txHash():
    try:
        if request.headers['Content-Type'] == 'application/json':
            post_data = json.loads(request.data.decode())
        else:
            post_data = request.form.to_dict(flat=True)
    except:
        return returnjsonresp({'code': -200, 'reason': 'unmarshall request body failed'})

    net = post_data.get("net")
    if net == "mainnet":
        net = ""
    else:
        net = net+"."
    txHashCode = post_data.get("txHash")
    result = txHash(net, txHashCode)

    return returnjsonresp({"code": 200, "result": result})

@app.route("/balance", methods=['POST'])
def query_balance():
    try:
        if request.headers['Content-Type'] == 'application/json':
            post_data = json.loads(request.data.decode())
        else:
            post_data = request.form.to_dict(flat=True)
    except:
        return returnjsonresp({'code': -200, 'reason': 'unmarshall request body failed'})

    net = post_data.get("net")
    if net == "mainnet":
        net = ""
    else:
        net = net+"."
    address = post_data.get("address")

    result = balance(net, address)

    return returnjsonresp({"code": 200, "result": result})

@app.route("/tokenBasicInfo", methods=['POST'])
def query_tokenBasicInfo():
    try:
        if request.headers['Content-Type'] == 'application/json':
            post_data = json.loads(request.data.decode())
        else:
            post_data = request.form.to_dict(flat=True)
    except:
        return returnjsonresp({'code': -200, 'reason': 'unmarshall request body failed'})

    net = post_data.get("net")
    if net == "mainnet":
        net = ""
    else:
        net = net+"."

    address = post_data.get("token_address")

    result = tokenBasicInfo(net, address)

    return returnjsonresp({"code": 200, "result": result})

@app.route("/tokenHolders", methods=['POST'])
def query_tokenHolders():
    try:
        if request.headers['Content-Type'] == 'application/json':
            post_data = json.loads(request.data.decode())
        else:
            post_data = request.form.to_dict(flat=True)
    except:
        return returnjsonresp({'code': -200, 'reason': 'unmarshall request body failed'})

    net = post_data.get("net")
    if net == "mainnet":
        net = ""
    else:
        net = net+"."

    address = request.json.get("token_address")
    supply = request.json.get("supply")
    decimals = request.json.get("decimals")
    # return json(request.json)
    try:
        result = tokenHolders(net, address,supply,decimals)
        # return json({"code": 500, "Error": "Yep, Our server catch a strange error"})
        return returnjsonresp({"code": 200, "result": result})
    except:
        return returnjsonresp({"code": 200, "result": None})

@app.route("/tokenTrans", methods=['POST'])
def query_tokenTrans():
    try:
        if request.headers['Content-Type'] == 'application/json':
            post_data = json.loads(request.data.decode())
        else:
            post_data = request.form.to_dict(flat=True)
    except:
        return returnjsonresp({'code': -200, 'reason': 'unmarshall request body failed'})

    net = post_data.get("net")
    if net == "mainnet":
        net = ""
    else:
        net = net+"."

    address = post_data.get("token_address")
    # return json(request.json)
    try:
        result = tokenTransaction(net, address)
        return returnjsonresp({"code": 200, "result": result})
    except:
        return returnjsonresp({"code": 200, "result": None})

@app.route("/tokenTransForAcc", methods=['POST'])
def query_tokenTransForAcc():
    try:
        if request.headers['Content-Type'] == 'application/json':
            post_data = json.loads(request.data.decode())
        else:
            post_data = request.form.to_dict(flat=True)
    except:
        return returnjsonresp({'code': -200, 'reason': 'unmarshall request body failed'})

    net = post_data.get("net")
    if net == "mainnet":
        net = ""
    else:
        net = net+"."

    token = post_data.get("token_address")
    account = post_data.get("account_address")
    # return json(request.json)
    try:
        result = tokenTransactionForAccount(net, token, account)
        # return json({"code": 500, "Error": "Yep, Our server catch a strange error"})
        return returnjsonresp({"code": 200, "result": result})
    except:
        return returnjsonresp({"code": 200, "result": None})

@app.route("/gasPrice", methods=['GET'])
def get_gas_Price():
    try:
        result = gasPrice()
    except:
        return returnjsonresp({"code":-200,"info":"browse etherscan.io meet an error"})
    return returnjsonresp({"code": 200, "result(GWei)": result})

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=3001,
        threaded=True
    )
