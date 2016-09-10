import unicodecsv
from datetime import datetime as dt
from decimal import *

'''

This is a program for use by client for reconciling bank statements showing daily deposits and withdrawals related to sales
from sales with corresponding accounting software statements tracking daily deposits and withdrawals related to sales.

Prior to this program being created, client had to manually (with the aid of MS Excel) reconcile the statements by manually
deduping entries from both lists to end up with a list of deposits or withdrawals that are not on the other list.  Using the
resulting deduped list, the client would investigate why one list contains a deposit/withdrawal, while the other does not.

This program goes through each list, creates arrays corresponding to deposits and withdrawals, and dedupes the list automatically
to ultimately create printout of deposits and withdrawals that are not on the other list, thus save weeks of manual labor.


'''


######################################################
# Functions for returning two arrays from CVS of bank deposits generated from Quickbooks: 
# 1.  An array of all deposits from sales, conslidated by date
# 2.  an array of all withdrawals from refunds, conslidated by date
######################################################

with open('../all_deposits.csv', 'rb') as f:
	reader = unicodecsv.DictReader(f)
	all_deposits = list(reader)

# Convert date strings to date values and string amount values to float
for deposit in all_deposits:
	date = deposit['Date']
	deposit['Date'] = dt.strptime(date, '%m/%d/%y')
	deposit['Amount'] = float(deposit['Amount'])

# Function to create array with consolidated deposits from sales (i.e., excluding refunds) for each day
def consolidate_daily_deposits(all_deposits):
	consolidated_daily_deposits =[]
	current_amount = 0
	startIndex = 0
	# start index at first non-refund entry
	while all_deposits[startIndex]['Amount'] < 0:
		startIndex += 1
	current_date = all_deposits[startIndex]['Date']
	for deposit in all_deposits:
		# Skip the deposit if the amount is less than zero (i.e., a refund)
		if deposit['Amount'] < 0:
			continue
		# Otherwise, if date is same as previous date, add the amount to the running total
		elif deposit['Date'] == current_date:
			current_amount += deposit['Amount']
		# If date is different, first append the entry for the date to the array, then change current date and current amount to new date
		else:
			current_amount = round(current_amount, 2)
			consolidated_daily_deposits.append({'Date': current_date, 'Amount': current_amount})
			current_date = deposit['Date']
			current_amount = deposit['Amount']
	# Add the last entry to the array
	current_amount = round(current_amount, 2)
	consolidated_daily_deposits.append({'Date': current_date, 'Amount': current_amount})
	return consolidated_daily_deposits

# Similar function, but for withdrawals
def consolidate_daily_withdrawals(all_deposits):
	consolidated_daily_withdrawals =[]
	current_amount = 0
	startIndex = 0
	while all_deposits[startIndex]['Amount'] > 0:
		startIndex += 1
	current_date = all_deposits[startIndex]['Date']
	for deposit in all_deposits:
		if deposit['Amount'] > 0:
			continue
		elif deposit['Date'] == current_date:
			current_amount += deposit['Amount']
		else:
			current_amount = round(current_amount, 2)
			consolidated_daily_withdrawals.append({'Date': current_date, 'Amount': current_amount})
			current_date = deposit['Date']
			current_amount = deposit['Amount']
	current_amount = round(current_amount, 2)
	consolidated_daily_withdrawals.append({'Date': current_date, 'Amount': current_amount})
	return consolidated_daily_withdrawals

# Create the deposits and withdrawal arrays
consolidated_daily_deposits = consolidate_daily_deposits(all_deposits)
consolidated_daily_withdrawals = consolidate_daily_withdrawals(all_deposits)

# for deposit in consolidated_daily_deposits:
# 	print deposit

# for deposit in consolidated_daily_withdrawals:
# 	print deposit


######################################################
# Functions for returning two arrays from CVS of bank deposits generated from BANK ACCOUNT STATEMENTS: 
# 1.  An array of all deposits from sales, conslidated by date
# 2.  an array of all withdrawals from refunds, conslidated by date
######################################################
with open('../bank_transactions_FINAL.csv', 'rb') as f:
	reader = unicodecsv.DictReader(f)
	all_bank_transactions = list(reader)

# Extract only the deposits and withdrawals related to sales and refunds, put htem in "bank_deposits" and "bank_withdrawals" arrays
bank_deposits = []
bank_withdrawals = []
for transaction in all_bank_transactions:
	if transaction['Comments'] == 'External Deposit BANKCARD':
		string_amount = ""
		for char in transaction['Amount']:
			if char != "$" and char != ",":
				string_amount += char
		transaction['Amount'] = string_amount
		transaction['Amount'] = float(transaction['Amount'])
		# convert the string date to actual date
		date = transaction['Date']
		transaction['Date'] = dt.strptime(date, '%m/%d/%y')
		bank_deposits.append(transaction)
	elif transaction['Comments'] == 'External Withdrawal BANKCARD':
		# add "minus" sign since's it's a withdrwal
		string_amount = "-"
		# strip non-numerical characters except for decimal
		for char in transaction['Amount']:
			if char != "$" and char != "," and char != "(" and char != ")":
				string_amount += char
		transaction['Amount'] = string_amount
		transaction['Amount'] = float(transaction['Amount'])
		date = transaction['Date']
		transaction['Date'] = dt.strptime(date, '%m/%d/%y')
		bank_withdrawals.append(transaction)

# for transaction in bank_deposits:
# 	print transaction

# for transaction in bank_withdrawals:
# 	print transaction

# Function for deduping (i.e., finding unaccounted for) entries in the accounting software statement and the bank statement
# Returns results as a 2-item list
def find_unaccounted(qb_array, bank_array):
	unaccounted_for_qb_array = []
	unaccounted_for_bank_array = list(bank_array)
	for qb_entry in qb_array:
		count = 0
		index = 0
	 	while index < len(unaccounted_for_bank_array):
	 		while index < len(unaccounted_for_bank_array) and qb_entry['Date'] >= unaccounted_for_bank_array[index]['Date']:
	 			index +=1
	 		if index >= len(unaccounted_for_bank_array):
				unaccounted_for_qb_array.append(qb_entry)
	 			break
	 		count +=1
	 		if qb_entry['Amount'] == unaccounted_for_bank_array[index]['Amount']:
	 			del unaccounted_for_bank_array[index]
	 			break
			if count > 4:
				unaccounted_for_qb_array.append(qb_entry)
				break
			index += 1
			if index == len(unaccounted_for_bank_array):
				unaccounted_for_qb_array.append(qb_entry)
	return [unaccounted_for_qb_array, unaccounted_for_bank_array]

# Assign unaccounted for deposits from each list to variables
unaccounted_for_qb_deposits = find_unaccounted(consolidated_daily_deposits, bank_deposits)[0]
unaccounted_for_bank_deposits = find_unaccounted(consolidated_daily_deposits, bank_deposits)[1]

# Assign unaccounted for withdrawals from each list to variables
unaccounted_for_qb_withdrawals = find_unaccounted(consolidated_daily_withdrawals, bank_withdrawals)[0]
unaccounted_for_bank_withdrawals = find_unaccounted(consolidated_daily_withdrawals, bank_withdrawals)[1]

print '\n'
print '*'*100
print 'Unaccounted for QB Withdrawals:'
for withdrawal in unaccounted_for_qb_withdrawals:
	print withdrawal
print '*'*100
print '\n'

print '\n'
print '*'*100
print 'Unaccounted for Bank Withdrawals:'
for withdrawal in unaccounted_for_bank_withdrawals:
	print withdrawal
print '*'*100
print '\n'

# Further consolidate the unaccounted for daily deposits because sometimes a single day's deposits are split into 2 deposits
unaccounted_for_deposits_consolidated = consolidate_daily_deposits(unaccounted_for_bank_deposits)

# Do another deduping to get final arrays of unaccounded for deposits
unaccounted_for_qb_deposits_after_consolidating = find_unaccounted(unaccounted_for_qb_deposits, unaccounted_for_deposits_consolidated)[0]
unaccounted_for_bank_deposits_after_consolidating = find_unaccounted(unaccounted_for_qb_deposits, unaccounted_for_deposits_consolidated)[1]

print '\n'
print '*'*100
print 'Unaccounted for QB deposits:'
for deposit in unaccounted_for_qb_deposits_after_consolidating:
	print deposit
print '*'*100
print '\n'

print '\n'
print '*'*100
print 'Unaccounted for Bank deposits:'
for deposit in unaccounted_for_bank_deposits_after_consolidating:
	print deposit
print '*'*100
print '\n'

