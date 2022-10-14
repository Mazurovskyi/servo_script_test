import usb.core
import usb.util
import sys
import time
import os

def clean_out_debug_file():
	with open('D:/My_projects/python_projects/py_usb/log.txt', 'w') as err_file:
		try:
			err_file.truncate(0)
		except Exception as file_error:
 			print(file_error)



# Launch:
# python driver_setup.py PYUSB_DEBUG='debug' PYUSB_LOG_FILENAME='D:\My_projects\python_projects\py_usb\log.txt'

print("--- start ---")
clean_out_debug_file()

device = usb.core.find(idVendor=0x5555, idProduct=0x5710)
if device is None:
	raise ValueError('Device not found')

#print(device)
device.set_configuration()

# --- data to setup servo in relative position mode (SDO packages) 0x601 = [0x06, 0x01] ---
control_word_0F = [0x06, 0x01, 0x2B, 0x40, 0x60, 0x00, 0x0F, 0x00]		
work_mod = [0x06, 0x01, 0x2F, 0x60, 0x60, 0x00]
location_cash = [0x06, 0x01, 0x23, 0x7A, 0x60, 0x00, 0x50, 0xC3, 0x00, 0x00]
trapezoidal_speed = [0x06, 0x01, 0x23, 0x81, 0x60, 0x00, 0xE8, 0x03, 0x00, 0x00]
trapezoidal_acceleration = [0x06, 0x01, 0x23, 0x83, 0x60, 0x00, 0x20, 0x4E, 0x00, 0x00]
control_word_4F = [0x06, 0x01, 0x2B, 0x40, 0x60, 0x00, 0x4F, 0x00]
control_word_5F = [0x06, 0x01, 0x2B, 0x40, 0x60, 0x00, 0x5F, 0x00]		# setup control_word = "5F" for relative position mode (as specify in manual)
status_word = [0x06, 0x01, 0x40, 0x41, 0x60, 0x00]


sdo_config = [control_word_0F, work_mod, location_cash, trapezoidal_speed, 
trapezoidal_acceleration, control_word_4F, control_word_5F, status_word]


# --- data to control the servo in relative position mode (PDO packages) 0x301 = [0x03, 0x01]	0x201 = [0x02, 0x01] ---
rpdo_2 = [0x03, 0x01, 0x20, 0x4E, 0x00, 0x00, 0xE8, 0x03, 0x00, 0x00] 	# target_position: 20000 (0x4E20); trapezoidal_speed: defoult 1000 rpm (3E8)
rpdo_1 = [0x02, 0x01, 0x2F, 0x00, 0x01, 0x20, 0x4E, 0x00, 0x00]			# target_position: 20000 (0x4E20); control_word = 2F (Maybye need to specify: "5F")


pdo_instructions = [rpdo_2, rpdo_1]


print("--- transmit SDO ---")
for sdo_pkg in sdo_config:

	written_bytes = device.write(0x01, sdo_pkg)							# written bytes	from SDO pkg at bulk OUT endpoint							
	print("written_bytes_SDO: {0}".format(written_bytes))
	

	try:
		returned_bytes = device.read(0x83, len(sdo_pkg))				# reading the servo reply from bulk IN endpoint
		print("returned_bytes: {0}\n".format(returned_bytes))
	except Exception as err:
		print('{0}\n'.format(err))
		continue



print("--- transmit PDO ---")
for pdo_pkg in pdo_instructions:

	written_bytes = device.write(0x01, pdo_pkg)							# written bytes	from PDO pkg at bulk OUT endpoint				
	print("written_bytes_PDO: {0}".format(written_bytes))


	try:
		returned_bytes = device.read(0x83, len(pdo_pkg))				# reading the servo reply from bulk IN endpoint
		print("returned_bytes: {0}\n".format(returned_bytes))	
	except Exception as err:
		print('{0}\n'.format(err))
		continue


for i in range(0, 2):													# try to send target location at 2 times

	written_bytes = device.write(0x01, rpdo_2)
	print("written_bytes_PDO: {0}".format(written_bytes))


	try:
		returned_bytes = device.read(0x83, len(rpdo_2))					
		print("returned_bytes: {0}\n".format(returned_bytes))	
	except Exception as err:
		print('{0}\n'.format(err))
		continue


usb.util.dispose_resources(device)