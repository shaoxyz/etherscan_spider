# -*- coding:utf-8 -*-
# Python3
# File    : eth_services
# Time    : 2018/3/28 10:11
# Author  : Shaweb
# For     : https://etherscan.io/
# Do      : html2json as micro-service
from pprint import pprint
import re
import math
import requests
from bs4 import BeautifulSoup
import socket
socket.setdefaulttimeout(10)
URL = "https://{}etherscan.io/{}"


# transaction details
def txHash(which_net, tx_hash):
    headers = {
        ":path": "/tx/{}".format(tx_hash),
    }
    url = URL.format(which_net, 'tx/' + tx_hash)
    print(url)

    r = requests.get(url, headers, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')
    container = soup.find("div", "container row")
    if container == None:
        return None
    keys = container.find_all("div", "col-sm-3")
    values = container.find_all("div", "col-sm-9")

    result = {}
    for i in range(len(keys)):
        result[keys[i].text.replace(":", "").replace(" ", "")] = values[i].text.replace("\n", " ").replace("\xa0", "")
    # special fix
    pprint(result)
    result["InputData"] = result["InputData"].replace("Convert To Ascii", "")
    result["GasLimit"] = int(result["GasLimit"])
    try:
        result["Nonce"] = result["Nonce&{Position}"]
    except:
        pass
    result["TxHash"] = result["TxHash"].replace(" ", "")
    result["Value"] = result["Value"].replace("  ", "")
    result["GasUsedByTransaction"] = int(result["GasUsedByTransaction"].split(" ")[1])
    result["GasPrice"] = result["GasPrice"][1:] if result["GasPrice"][0] == " " else result["GasPrice"]
    result["ActualTxCost/Fee"] = result["ActualTxCost/Fee"][1:] if result["ActualTxCost/Fee"][0] == " " else result[
        "ActualTxCost/Fee"]

    result["url"] = url

    return result


# ETH balance and Token balances
def balance(which_net, account_address):
    headers = {
        ":path": "/address/{}".format(account_address),
    }
    url = URL.format(which_net, 'address/' + account_address)

    r = requests.get(url, headers, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')
    # Token Balances
    token = soup.find("ul", {"id": "balancelist"})
    if token == None:
        token_balances = {}
    else:
        _list = token.find_all("li")[2:-1]
        token_list = []
        token_adds = []
        for t in _list:
            try:
                token_list.append(t.find("br").next_sibling)
                token_adds.append(re.search(r"(?<=n\/)(.*?)(?=\?a)", t.find("a")['href']).group())
            except:
                pass

        token_balances = dict(zip(token_list, token_adds))

    # ETH Balance
    balance = soup.find("table", "table")
    ETH_balance = balance.find_all("tr")[1].find_all("td")[1].text.replace("\n", "")
    result = {"tokenBalances": token_balances, "ETHBalance": ETH_balance}

    # Transaction
    transfers = soup.find("div", "panel-body table-responsive").find("table", "table").find_all('tr')[1:]
    if len(transfers) <= 2:
        transactions = []
    else:
        transactions = []
        for t in transfers:
            keys = ['TxHash', 'Block', 'Age', 'From', 'To', 'Value', 'TxFee']
            values = []
            for value in t:
                if value.text in ["OUT", "\xa0 IN \xa0"]:
                    continue
                if value.text[0] == " ":
                    v = value.text[1:]
                else:
                    v = value.text
                values.append(v)
            event = dict(zip(keys, values))
            transactions.append(event)
    result["transaction"] = transactions

    return result


# Token transactions for the account, test use EOS Token
def tokenTransactionForAccount(which_net, token_address, account_address):
    url = "https://{}etherscan.io/token/generic-tokentxns2?contractAddress={}&a={}&mode=".format(which_net,
                                                                                                 token_address,
                                                                                                 account_address)
    print(url)
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')

    transfers = soup.find("table", "table").find_all('tr')[1:]
    if len(transfers) < 2:
        token_transfers = []
    else:
        token_transfers = []
        for t in transfers:
            keys = ['TxHash', 'Age', 'From', 'To', 'Quantity']
            values = []
            for value in t:
                if value.text in ["OUT", "\xa0 IN \xa0"]:
                    continue
                # if value.text[0] == " ":
                #     v = value.text[1:]
                else:
                    v = value.text
                values.append(v)
            event = dict(zip(keys, values))
            token_transfers.append(event)

    result = {"TokenTransfers": token_transfers}
    return result


# Token transaction
def tokenTransaction(which_net, token_address):
    url = "https://{}etherscan.io/token/generic-tokentxns2?contractAddress={}&mode=".format(which_net, token_address)
    print(url)
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')
    # print(soup.prettify())
    # Here we got token Transaction
    transfers = soup.find("table", "table").find_all('tr')[1:]
    if len(transfers) < 2:
        token_transfers = []
    else:
        token_transfers = []
        for t in transfers:
            keys = ['TxHash', 'Age', 'From', 'To', 'Quantity']
            values = []
            for value in t:
                if value.text == " ":
                    continue
                values.append(value.text)
            event = dict(zip(keys, values))
            token_transfers.append(event)

    result = {"TokenTransfers": token_transfers}
    return result


# Here we got Basic Info about the token
def tokenBasicInfo(which_net, token_address):
    total_supply = ""
    decimals = ""
    holders = ""

    headers = {
        ":path": "/token/{}".format(token_address),
    }

    url = URL.format(which_net, "token/" + token_address)
    print(url)
    r = requests.get(url, headers, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')
    # print(soup.prettify())
    name = soup.find("span", "lead-modify").text
    if name == '':
        return None
    infos = soup.find("div", {"id": "ContentPlaceHolder1_divSummary"}).find_all("tr")[1:]
    for i in infos:
        item = i.text.replace("\n", "")

        if "Total Supply" in item:
            total_supply = item.split(":")[1]
            # print(total_supply)
            supply = float(total_supply.split(" ")[0].replace(",", ""))
            try:
                symbol = total_supply.split(" ")[1]
            except:
                symbol = "null"
            total_supply = {"supply": supply, "symbol": symbol}

        if "Decimals" in item:
            decimals = int(item.split(":")[1].replace("\xa0", ""))

        if "Holders" in item:
            holders = int(item.split(":")[1].split(" ")[0])

    basic_info = {"totalSupply": total_supply,
                  "decimals": decimals,
                  "holders": holders,
                  "name": name}

    # add Token creator
    headers = {
        ":path": "/address/{}".format(token_address),
    }

    url = URL.format(which_net, 'address/' + token_address)

    r = requests.get(url, headers, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')
    creator = soup.find("tr", {"id": "ContentPlaceHolder1_trContract"}).find_all("a")[0]["href"].split("/")[-1]
    atTxn = soup.find("tr", {"id": "ContentPlaceHolder1_trContract"}).find_all("a")[1]["href"].split("/")[-1]
    basic_info["creator"] = creator
    basic_info["atTxn"] = atTxn
    return basic_info


# Here we got token holders list
def tokenHolders(which_net, token_address, supply=None, decimals=None):
    if (supply == None) or (decimals == None):
        # print("Execute tokenBasicInfo")
        try:
            basic_info = tokenBasicInfo(which_net, token_address)
            supply = basic_info.get("totalSupply").get("supply")
            decimals = basic_info.get("decimals")
        except:
            return "Error in get token basic info"

    multi = int(math.pow(10, decimals))
    supply = int(supply * multi)
    url = "https://{}etherscan.io/token/generic-tokenholders2?a={}&s={}".format(which_net, token_address, supply)
    print(url)
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')

    holders = soup.find("table", "table").find_all('tr')[1:]
    if len(holders) < 2:
        token_holders = []
    else:
        token_holders = []
        for t in holders:
            keys = ['Rank', 'Address', 'Quantity', 'Percentage']
            values = []
            for value in t:
                values.append(value.text)
            event = dict(zip(keys, values))
            token_holders.append(event)

    return token_holders

def gasPrice():
    url = "https://etherscan.io/gastracker"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'lxml')
    minimum_price = soup.find("span",{"id":"ContentPlaceHolder1_ltGasPrice"}).text
    return minimum_price


if __name__ == '__main__':
    which_net = "ropsten."
    main_net = ""
    tx_hash = "0x1b2e8afc9661235d7e7dfaec1b2c420d2c8d74a39fefb44945c7b9e17786ee18"

    account_address = "0xf7a32f64a8a43d454a1a9bd9c8bfa50362e88260"
    token_address = "0x4d2812008c5b06fa16a3c74c161d32f7700a104c"
    EOS_address = "0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0"

    # print(gasPrice())

    print(txHash("", "0xd048b643a569d18b18e7be7149114c7596041b5f7a2d6c6114c5c3687ac85d89"))

    # pprint(balance(main_net, "0x42B13cDF6Af8EfF8377CcE5295B0b5757932891B"))

    # pprint(tokenTransaction(which_net, "0xE4D64085fc58F3C067c30215ce92cd9Ee661740A"))


