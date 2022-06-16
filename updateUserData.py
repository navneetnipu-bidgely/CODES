#!/bin/python3
import random

import requests
import calendar
import time

# Automation script RAW data and BILLING data update for test users in UAT/DEV/NONPROD/PROD environment

# ALGORITHM

# get the last data timestamp for the user
# get the RAW/INVOICE file format
# generate the RAW/INVOICE data file as required
# provide the visuals for the data generated
# upload the files to s3 if required
# create the algorithm visual for the implemented algorihtm.


# class having some variables used to update the user data
from matplotlib import pyplot as plt


class UpdateData:
    pilotName = ""
    pilotId = 0
    dataServerURL = ""
    uuid = ""
    hid = 0
    gid = 0
    accessToken = ""
    lastDataTimestamp = 0
    # dataUptoTimestamp will be by default current day timestamp.
    dataUptoTimestamp=calendar.timegm(time.gmtime())
    dataFormat = {}
    # stores raw and invoice data in dictionary data structures where key=time and value=raw data/invoive data
    rawData={}
    InvoiceData={}
    # gap between consecutive raw data points which is defaults to 900 seconds=15 minutes
    gapInRawData=900

    def __init__(self,pilotName,pilotId,dataServerURL,uuid,hid,gid,accessToken,DataUptoTimestamp):
        print("inside constructor...")
        self.pilotName=pilotName
        self.pilotId=pilotId
        self.dataServerURL=dataServerURL
        self.uuid=uuid
        self.hid=hid
        self.gid=gid
        self.accessToken=accessToken
        self.dataUptoTimestamp=DataUptoTimestamp
        print("object construction completed!")

    # please use the below function to generate the visual of the algorithm used in this script.
    # todo => function to generate the algorithm

    # function to get the last data timestamp for the user (can be done from meter api's lastDataTimestamp)

    def getLastDataTimestamp(self):

        # {{url}}/meta/users/{{uuid}}/homes/{{hid}}/gws/{{gid}}/meters
        # assignment os values to the variables needed to construct the api.

        print("inside function getLastDataTimestamp(self) to get the last data timestamp...")

        url = self.dataServerURL
        uuid = self.uuid
        hid = self.hid
        gid = self.gid
        accessToken = self.accessToken

        api = url + "/meta/users/"+uuid+"/homes/"+hid+"/gws/"+gid+"/meters"
        print("meter api:",api)

        # get the meter api response in order to fetch the last data timestamp

        apiResponse = requests.get(url=api, params={"access_token": accessToken})
        try:
            apiResponseJSON=apiResponse.json()
            print(apiResponseJSON)
        except Exception:
            print(Exception)

        # inside /users/86a02776-63f4-4ec1-b5fa-28262af6525a/homes/1/gws/2/meters/1 key, we have to get lastDataTimestamp keys value.

        key="/users/"+uuid+"/homes/"+hid+"/gws/"+gid+"/meters/1"

        # return the lastDataTimestamp value.

        return apiResponseJSON[key]["lastDataTimestamp"]

    # todo => function to get the RAW/INVOICE file format

    # function to generate the RAW data as required

    def generateRawData(self):
        From=self.lastDataTimestamp
        To=self.dataUptoTimestamp
        gap=self.gapInRawData
        for time in range(From,To+1,gap):
            self.rawData[time]=round(random.uniform(0, 3),2)
        print("raw data points for user from:",From," to:",To,"is:")
        print(self.rawData)
        print("raw data generation for the user completed!")


    # todo => function to generate the INVOICE data as required

    def generateInvoiceData(self):

        return "done"

    def generateRawDataVisuals(self):

        # plot to show raw data points on 15 mintutes interval
        data=self.rawData
        y = []
        x = sorted(data)
        for time in x:
            y.append(data[time])
        plt.plot(x, y)
        # naming the x axis
        plt.xlabel('timestamp')
        # naming the y axis
        plt.ylabel('raw data point')
        # giving a title to the graph
        plt.title('raw data plot')
        # show a legend on the plot
        plt.legend()
        # function to show the plot
        plt.show()

        # plot to show raw data points on day basis




    # todo => function to provide the visuals for the invoice data generated

    # todo => function to generate the RAW/INVOICE data file as required

    # todo => function to upload the files to s3 if required


if __name__ == '__main__':
    print("inside main function...")

    # get the necessary details from user to generate the data

    pilotName = input("enter the pilotName:")
    pilotId = input("enter the pilotID:")
    dataServerURL = input("enter the dataServerURL:")
    uuid = input("enter the uuid:")
    hid = input("enter the hid:")
    gid = input("enter the gid:")
    accessToken = input("enter the access token:")

    # creating UpdateData class object to bind all its attributes and methods inside it.

    UpdateDataObject=UpdateData(pilotName,pilotId,dataServerURL,uuid,hid,gid,accessToken)

    # calling getLastDataTimestamp() function to get the last data timestamp for that user.

    UpdateDataObject.lastDataTimestamp=UpdateDataObject.getLastDataTimestamp();
    print("last Data Timestamp:",UpdateDataObject.lastDataTimestamp)
