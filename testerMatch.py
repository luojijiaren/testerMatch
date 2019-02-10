# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 21:35:35 2019

@author: fzhan
"""
import pandas as pd
import os

'''
This class will match Testers based on a User's search Criteria (Country and device). 
The search results will be ranked in order of Experience. Experience is 
measured by the number of Bug(s) a Tester filed for the given Device(s).
'''
class TesterMatch(object):
    #load data
    def __init__(self, path):
        #path can be absolute path or relative path
        self.testers=pd.read_csv(os.path.join(path,'testers.csv'))
        self.devices=pd.read_csv(os.path.join(path,'devices.csv'))
        self.tester_device=pd.read_csv(os.path.join(path,'tester_device.csv'))
        self.bugs=pd.read_csv(os.path.join(path,'bugs.csv'))

    #find the quanlified test id from tester.csv
    def qualified_testers(self, chooseAllCountries='NO', country_filter=[]):
        #user can chooseAllCountries(1) or give country_filter : a list of countries like ['US']
        qualified_testers=self.testers
        if chooseAllCountries!='YES':
            print(country_filter)
            qualified_testers=self.testers[self.testers.country.isin(country_filter)]        
        qualified_testerId=qualified_testers['testerId']
        return qualified_testerId.tolist()
    
    #find the quanlified device id from devices.csv
    def qualified_devices(self,chooseAllDevices='NO', device_filter=[]):  
        #user can chooseAllDevices(1) or give device_filter : a list of devices like ['iPhone 4','iPhone 5']
        qualified_devices=self.devices
        if chooseAllDevices!='YES':
            qualified_devices=self.devices[self.devices.description.isin(device_filter)]      
        qualified_deviceId=qualified_devices['deviceId']
        return qualified_deviceId.tolist()

    #find the bug numbers for qualified testers and devices 
    #in bugs.csv, use testid,devices to choose rows then group by useid, count bugs and sort
    def Tester_bugs(self, qualified_testerId_list, qualified_deviceId_list):
        #qualified_testerId_list is filtered by tester's country
        #qualified_deviceId_list is filtered by device names
        qualified_bugs=self.bugs[(self.bugs.testerId.isin(qualified_testerId_list))&(self.bugs.deviceId.isin(qualified_deviceId_list))]
        tester_bug_number=pd.DataFrame(qualified_bugs.groupby(self.bugs.testerId).size(),columns=['bugNum'])
        tester_bug_number['testerId']=tester_bug_number.index
        #add testers who are in qualified_testerId_list, but bug number is 0
        result0=pd.DataFrame(qualified_testerId_list,columns=['testerId']).merge(tester_bug_number,how='left').fillna(0)
        result0.bugNum=result0.bugNum.astype(int)
        #add tester names
        result0=self.testers[['testerId','firstName','lastName']].merge(result0)
        return result0.sort_values(by='bugNum',ascending=False).reset_index().drop(['index'],axis=1)
    
# main function which actually starts the testers match 
def main(args):
    path=input('Please put in the data fold path: ')
    match = TesterMatch(path)
    chooseAllCountries=input('Do you want to choose All countries?YES/NO   ')
    country_filter=[]
    #print(bool(chooseAllCountries))
    if chooseAllCountries!='YES':
        country_filter=eval(input('Please put in the country list of testers: '))
    qualified_testerId_list = match.qualified_testers(chooseAllCountries,country_filter)
    chooseAllDevices=input('Do you want to choose All devices?YES/NO   ')
    if chooseAllDevices!='YES':
        device_filter=eval(input('Please put in the device list:'))
    device_filter=[]
    qualified_deviceId_list = match.qualified_devices(chooseAllDevices, device_filter) 
    print("starting matching")
    result=match.Tester_bugs(qualified_testerId_list, qualified_deviceId_list)
    #print (index._bt.formattree())
    print(result)
    

# this little helper will call main() if this file is executed from the command
# line but not call main() if this file is included as a module
if __name__ == "__main__":
    import sys
    main(sys.argv)
