import ipaddress

# contains the list of overlapping IPs
overlapping_list = {}

def find_overlapping_ip(search_ip, mo_name):
	for mo, mo_iplist in ipList.items():
		for ip in mo_iplist:
			try:

				# convert to IP_Network object to check for overlappig
				loop_ip = ipaddress.ip_network(ip, strict=False)
			except ValueError as ve:
				print('May be the IP is incorrect ... '+str(ip))
				print('Moving to the next IP ...')
				print(ve)

			# bypass if the following conditions are true
			# 1. both the IP i.e. search_ip and loop_ip are same
			# 2. the MO to which search_ip and loop_ip belongs to are same ...			
			if ipaddress.ip_network(loop_ip,strict=False).compare_networks(ipaddress.ip_network(search_ip, strict=False)) == 0 and \
				mo_name == mo:
				#print('Skipping this one ... with MO '+str(mo)+' and IP '+str(search_ip)+' target ip '+str(loop_ip))
				continue

			# do we have an overlapping IPs	??
			if search_ip.overlaps(loop_ip):
				
				#print('The search IP '+str(search_ip)+' is overlapping with '+str(loop_ip))

				# in case, where search_ip has a broader range	
				# so we will compare the CIDR of both the IP ...
				if search_ip.prefixlen < loop_ip.prefixlen:
					
					# time to add the overlapping IP in the list ...
					# first ensure, the MO name is not there
					# if not there, then create one ...
					if mo_name not in overlapping_list:
						overlapping_list[mo_name] = {}

					# now check if the overlapping IP is there in the list 	
					if str(search_ip) not in overlapping_list[mo_name]:
						overlapping_list[mo_name][str(search_ip)] = {}

					# store the overlapping as followed:
					# MO Name -> Search_ip -> Overlapping IP = MO name 
					# [MO Name]
					#	[Search IP]
					#		[Loop IP] = Mo Name
					overlapping_list[mo_name][str(search_ip)][str(loop_ip)] = mo

				# in case, where loop_ip or targetted ip has a broader range	
				else:
					
					if mo_name not in overlapping_list:
						overlapping_list[mo_name] = {}

					if str(loop_ip)	not in overlapping_list[mo_name]:
						overlapping_list[mo_name][str(loop_ip)] = {}

					overlapping_list[mo_name][str(loop_ip)][str(search_ip)] = mo					


def count_total_ips():
	total_ip = 0
	total_mo = 0

	for mo, mo_iplist in ipList.items():
		total_ip += len(mo_iplist)
		total_mo += 1

	print('Total of '+str(total_ip)+' IPs found in '+str(total_mo)+' Managed Object ...')

# The program starts from here ...

print('---------------------')
print('Opening MO.csv file ...')
fd = open('MO.csv', 'r')

ipList = {}

for line in fd:

	# Comma as delimiter as it's a CSV file
	tmp = line.split(',')

	# first col. will be the MO name ..
	ipList[tmp[0]] = []

	# copy everything after first col to new array
	newtmp = tmp[1:]

	# loop through the list and then perform some filtering - removing spaces and new lines ...
	# then add the IPs into the list that will be used for searching
	for ip in newtmp:

		# removing any newline or spaces
		t_ip = ip.replace(' ', '').replace('\n', '')

		# if no IP is mentioned in between then don't add them
		if len(t_ip) == 0 or t_ip == '\n':
			continue
		else:
			ipList[tmp[0]].append(t_ip) # add the IP to the list 

print('Closing the file now ... all the IPs are added')
fd.close() # Closing the file ...no need to keep it open
count_total_ips()	# counting the total IP and MO

# The IP that will be searched 
search_ip = ''

for mo, mo_iplist in ipList.items():
	print('-----------------------------')
	print('Checking overlapping IPs in '+str(mo)+' Managed Object ...')
	for ip in mo_iplist:
		try:
			# strict - is used to bypass the error when the IP 
			# passed has CIDR notation but IP is not a network IP
			# For eg. 8.8.8.0/24 == correct
			# but 8.8.8.8/24 == incorrect (so with strict=False)
			# the code will return the correct network IP
			search_ip = ipaddress.ip_network(ip, strict=False)

			# let's find the overlapping IP for the IP in the MO
			# we are using Bubble-sort algo out here ...
			find_overlapping_ip(search_ip, mo)

		except ValueError as ve:
			print('May be the IP is incorrect ... '+str(ip))
			print('Moving to the next IP ...')
			print(ve)

print('-----------------------')
#print(overlapping_list)

fdw = open('Overlapping.csv', 'w')

print('-----------------------')

# store the overlapping as followed:
# MO Name -> Search_ip -> Overlapping IP = MO name 
# 	[MO Name]
#		[Search IP]
#			[Loop IP] = Mo Name

for mo, mo_ip in overlapping_list.items():
	print('MO '+str(mo))

	fdw.write('\n')	# start with new line ...
	# data0 = str(mo)
	# fdw.write(data0)

	for ip_name, overlap_list in mo_ip.items():
		print('Broader range ... '+str(ip_name))

		fdw.write('\n')
		data = str(ip_name)
		fdw.write(data)

		for overlap_ip, overlap_ip_mo in overlap_list.items():
			print('\tSmaller IP '+str(overlap_ip)+' ('+str(overlap_ip_mo)+')')

			data1 = ','+str(overlap_ip)+','+str(overlap_ip_mo)
			fdw.write('\n')
			fdw.write(data1)

	fdw.write('\n')	
	fdw.write('\n')	
	print('-----------')		

fdw.close()

print('The result has been stored in Overlapping.csv file ...')

