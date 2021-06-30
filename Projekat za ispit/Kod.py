import numpy as np
import hashlib
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import random
import os
import time

def sha3(data):
    return hashlib.sha3_256(data.encode('utf-8')).hexdigest()

def hashValue(index, data, timestamp, prevHash, nonce):
    allData = str(index) + str(data) + str(timestamp) + str(prevHash) + str(nonce)
    allData = sha3(allData)
    return allData

def pcg32(param1, param2, param3) -> np.uint32:
    np.seterr(all='ignore') # uklanja overflow poruke.

    engine = np.array([param1, param2], dtype='uint64')
    multiplier = param3
    big_1 = np.uint32(1)
    big_18 = np.uint32(18)
    big_27 = np.uint32(27)
    big_59 = np.uint32(59)
    big_31 = np.uint32(31)

    while True:
        old_state = engine[0]
        inc = engine[1]
        engine[0] = old_state * multiplier + (inc | big_1)
        xorshifted = np.uint32(((old_state >> big_18) ^ old_state) >> big_27)
        rot = np.uint32(old_state >> big_59)
        yield np.uint32((xorshifted >> rot) | (xorshifted << ((-rot) & big_31)))


def read_file(filename):
    data = pd.read_csv(filename)
    return data

def create_blockchain():
    filename = "Blockchain.csv"
    newData = pd.DataFrame(columns=['Index','Data','Time','Previous Hash','Nonce','Hash'], index=None)
    newData = newData.append({'Index':str(0), 'Data': 'Genesis', 'Time': str(datetime.now()), 'Previous Hash': "0", 'Nonce': "0", 'Hash': "0"}, ignore_index=True)

    newData.to_csv(filename, index=None)

def addBlockchain(newData):
    filename = "Blockchain.csv"
    param1 = np.uint64(random.random()*(2**64))
    param2 = np.uint64(random.random()*(2**64))
    param3 = np.uint64(6364136223846793005)
    data = read_file(filename)
    index = len(data)
    timestamp = str(datetime.now())
    prevHash = data['Hash'][index - 1]
    randomGen = pcg32(param1, param2, param3)
    i = 0
    start = time.time()
    nonce = next(randomGen)
    Hash = hashValue(index, newData, timestamp, prevHash, nonce)
    while True:
        nonce = nonce - 1
        Hash = hashValue(index, newData, timestamp, prevHash, nonce)
        if Hash[0:6] == '00ff00':
            data = data.append({"Index": str(index), "Data": newData, "Time": timestamp, "Previous Hash": prevHash, "Nonce": str(nonce), "Hash": Hash}, ignore_index=True)
            data.to_csv(filename, index=None)
            break
        if i > 1000:
            i = 0
            nonce = next(randomGen)

        i = i + 1
    total_time = time.time() - start
    print("Vreme utroseno u majnovanje: "+str(total_time) +' s')

def viewBlock():
    filename = "Blockchain.csv"
    data = pd.read_csv(filename, delimiter=',',names=['Index','Data','Time','Previous Hash','Nonce','Hash'])
    for i in range(1, len(data)):
        print("Index: ", data["Index"][i])
        print("Data: ", data["Data"][i])
        print("Time: ", data["Time"][i])
        print("Previous Hash: ", data["Previous Hash"][i])
        print("Hash: ", data["Hash"][i])
        print("Nonce: ", data["Nonce"][i])
        print("\n")

def validateBlock():
    filename = "Blockchain.csv"
    data = pd.read_csv(filename, delimiter=',',names=['Index','Data','Time','Previous Hash','Nonce','Hash'])
    status = False
    for i in range(3, len(data)):
        prevHash = data["Previous Hash"][i]
        currentHash = hashValue(data['Index'][i-1], data['Data'][i-1], data['Time'][i-1], data['Previous Hash'][i-1], data['Nonce'][i-1])
        if (currentHash == prevHash):
            status = True
        else:
            status = False
            break

    if status==True:
        status = "Siguran"
    else:
        status = "Ugrozen"
    print("Blockchain Status: ", status)

def changeBlcok(newData, index):
    filename = "Blockchain.csv"
    data = pd.read_csv(filename)
    print(newData)
    data["Data"][index] = newData
    data.to_csv(filename, index=None)



def main():
    exit = False
    while (exit==False):
        print("\nBlockchain\n")
        print("1. Kreiraj novi Blockchain (Prethodni fajl ce biti izbrisan)")
        print("2. Dodati novi blok (podatak)")
        print("3. Pregled blokova")
        print("4. Validacija blokova")
        print("5. Izlaz")
        x = int(input("\nUnesite broj zeljene akcije: "))
        if x == 1:
            os.system('cls')
            create_blockchain()
            print("Blockchain uspesno kreiran")
        elif x == 2:
            os.system('cls')
            newData = input("Unesite novu vrednost: ")
            addBlockchain(newData)
            print("Nova vrednost uspesno dodata")
        elif x == 3:
            os.system('cls')
            viewBlock()
        elif x == 4:
            os.system('cls')
            validateBlock()
        elif x == 5:
            exit = True
            os.system('cls')


if __name__ == '__main__':
    main()
