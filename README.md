
# TaxAutomaton
This project aims to create a automation process for organizing receipts for taxation purposes. 

## Powered By Fintelics
 ![](https://media.licdn.com/dms/image/C560BAQFSfx9gplUjhw/company-logo_200_200/0?e=2159024400&v=beta&t=dhD6MUwJUGa7cKYSZ8abF-P3DjaMLCnVoRpjBGh-pVc)
___
# Gmail Invoice Organizer
The gmail invoice organizer uses gmail api to look through the entire mail box and forward them to the accountant upon grouping   

### Setup
Go to this page: https://developers.google.com/gmail/api/quickstart/python

Note: When following the instructions, if there are errors thrown against the package for six on Macos, install with 

### OAuth
The GMail API follows google oauth flow, in order to gain access to the gmail account, first run receipt.py

### UserId Configuration 
Modify the config.example.ini file to change the userId to your own email address.

### Search Query
In the config file chagne the query based on the advanced search query following this link
https://support.google.com/mail/answer/7190

### Use Case #1 Organizing Uber Receipts for a certain month
For organizing Uber receipts, change the Title and Query parameters in the config.ini file as following:

```
UserId = your@email.com
Query = from:uber.canada@uber.com subject:Uber+Receipts after:2018/12/01 before:2019/01/01
SendTo = example@email.com
Title = December Receipts for Uber
MaxEmailCount = 10
```

___