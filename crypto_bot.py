from coinbase.wallet.client import Client
import mysql.connector
import time


client = Client('api_key', 'api_secret')

account_id = "account_id_number"
payment_m = "payment_method_number"



print("*****---------------------------------------*****")

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print(current_time)


#initialize variables
max_price = 60000
buy_percent = 0.10
sell_percent = 0.055
sell = 0
count = 0
sum = 0
average = 0
percent_gain =0
percent_gain_top = 0
balance = float(client.get_primary_account()["balance"]["amount"])
usd_balance = float(client.get_account("account_id")["balance"]["amount"])
btc_balance = float(client.get_primary_account()["native_balance"]["amount"])
total_balance = usd_balance+btc_balance


print("Current Portfolio Value: " + str(total_balance))
print("Current BTC Value: " + str(btc_balance))



current_btc = str(client.get_sell_price(currency_pair = 'BTC-USD')["amount"])
print("Current sell price of btc: " + current_btc)

current_btc_buy = str(client.get_buy_price(currency_pair = 'BTC-USD')["amount"])
print("Current buy price of btc: " + current_btc_buy)

#get the latest tran info
latest_tran_type = str(client.get_transactions(account_id)[0]["type"])
latest_tran_amount = str(client.get_transactions(account_id)[0]["amount"])

#get the highest price recorded yet
mydb = mysql.connector.connect(
  host="localhost",
  user="user",
  password="password",
  database="database")

mycursor = mydb.cursor()

mycursor.execute("SELECT Highest_Price FROM Trader")

h = mycursor.fetchone()

highest_P = h[0]

if(float(current_btc) > highest_P):
    print("api max price is higher" + current_btc)



    sql = "UPDATE Trader SET Highest_Price = '" + current_btc+"'"

    mycursor.execute(sql)

    mydb.commit()

    print(mycursor.rowcount, "record(s) affected")
    max_price = float(current_btc)

else:
    print("database price is higher")
    max_price = highest_P
    print("max_price is "+ str(max_price))


if (latest_tran_type == "buy"):
    latest_tran_bamount= str(client.get_buys(account_id)[0]["unit_price"]["amount"])
else:
    latest_tran_bamount= str(client.get_sells(account_id)[0]["unit_price"]["amount"])

#calculate buys, and average
for i in range(10):
    if (client.get_transactions(account_id)[i]["type"] ==  "buy"):
        count=count + 1
        sum = sum + float(client.get_buys(account_id)[i]["unit_price"]["amount"])
        average = sum/count
        percent_gain = (float(current_btc)- average)/average
        percent_gain_top = (float(current_btc)- max_price)/max_price

    else:
        break

if count == 0:
    buy_percent = 0.05
    sell_percent = 0.055
elif count ==1:
    buy_percent = 0.12
    sell_percent = 0.04
elif count ==2:
    buy_percent = 0.25
    sell_percent = 0.08
elif count ==3:
    buy_percent = 0.45
    sell_percent = 0.1025
elif count ==4:
    buy_percent = 0.70
    sell_percent = 0.15
elif count ==5:
    buy_percent = 0.80
    sell_percent = 0.15
else:
    buy_percent = 0.95
    sell_percent = 0.15

sell_price = (average * sell_percent) + average
buy_price = max_price-(max_price * buy_percent)

print("Latest transaction was a: " + latest_tran_type + " For: " + latest_tran_amount + " At 1 BTC for: " + latest_tran_bamount)


print("Percent gain since last transaction: " + str(100*percent_gain))
print("Percent gain from max price: " + str(100*percent_gain_top))


print("the count, sum and average is: " + str(count)+" " + str(sum)+ " " + str(average))
print("Will sell at: " + str(sell_price))
print("Will buy at: " + str(buy_price))


#action of buy sell or hold
if ((balance > 0) and (float(current_btc) > sell_price) and count > 0):
    print("Sell")
    client.sell(account_id, amount=str(balance), currency='BTC')
elif((balance == 0) and (count == 0) and (float(current_btc_buy)< buy_price)):
    print("Buy")
    client.buy(account_id, total ='200', currency='USD', payment_method = payment_m)
elif((balance < 0.07) and (count > 0) and (float(current_btc_buy)< buy_price)):
    print("Buy")
    client.buy(account_id, total ='200', currency='USD', payment_method = payment_m)
else:
    print("Hold")

sql ="UPDATE Trader SET "+"latest_tran_type ='"+latest_tran_type+"',latest_tran_amount='" + str(latest_tran_amount)+ "',latest_tran_bamount='" + latest_tran_bamount+"',percent_gain='" + str(percent_gain)+"',average='" + str(average)+ "',buy_price='" + str(buy_price)+"',sell_price='" + str(sell_price)+"',percent_gain_top='" + str(percent_gain_top)+"',count='" + str(count)+"',usd_balance='" + str(usd_balance)+"',btc_balance='" + str(btc_balance)+"',current_btc='" + str(current_btc)+"' WHERE ID =1"

mycursor.execute(sql)

mydb.commit()

print(mycursor.rowcount, "record(s) affected")
