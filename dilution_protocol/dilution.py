from opentrons import protocol_api 
import csv 

metadata = {
	'apiLevel' :  '2.4',
	'protocolName' : 'Test Dilution Protocol',
	'author' : 'Becky Sadler',
	'description' : 'Test protocol for dilution'
}

''' 
Protocol Requirements: 

Pipettes: P20 GEN2 single channel 1-20ul (LEFT), P300 GEN2 single channel 20-300ul (RIGHT)

Custom Labware: 
	NonSkirted 96-well plate in flat plate holder (API Load name = 4t_96_wellplate_200ul)

Deck Layout:
	Position 10:	OpenTrons 20ul tip rack (opentrons_96_tiprack_20ul)
	Position 11:	OpenTrons 300ul tip rack (opentrons_96_tiprack_300ul)
	Position 8:		NonSkirted 96-well plate in flat plate holder (Plate 1 - full strength)
	Position 7:		NonSkirted 96-well plate in flat plate holder (Plate 2 - Diluted)
	Position 4:		4x6 rack for 1.5ml microfuge tubes (Water pot - A1) ???Would water be held this way???

Liquid Handling properties:
	??? Do these need to change????
	Aspirate height: 2mm from bottom
	Dispense height: 1mm from bottom at start increase by 0.5mm with each loop 
	Touch tip on aspirate: 2-3mm from top

Transfer process:
	Adding water to the diluted plate:
	Get tip 
	Aspirate 200ul of water 
	Touch tip (2-3mm from top)
	Cycle through water values in csv and dispense appropriate amount in each. 
	Have loop to make sure that the amount of water in the tip is always enough for next dispense. 

	Loop through the dna transfers from a csv file
	Get tip (NEW ONE)
	Aspirate from well at 2mm 
	Touch tip (2-3mm from top)
	Dispense into well (At 1mm)
	Blow out (+0.5mm above) - ??? Should this instead be a mix ??? 
	Touch tip 
	Drop tip. 
'''

csv_name = '11111_dilution.csv'

welllist=[]
dnalist=[]
waterlist=[]
with open(csv_name, newline='') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',')
	for row in reader:
		welllist.append(row['Well'])
		dnalist.append(float(row['Vol of dna']))
		waterlist.append(float(row['Vol of water']))

def run(protocol: protocol_api.ProtocolContext):

	# Add labware
	dna_plate = protocol.load_labware('4t_96_wellplate_200ul', '8')
	dilution_plate = protocol.load_labware('4t_96_wellplate_200ul', '7')
	biomek_tube_rack = protocol.load_labware('biomekmicrofuge_24_wellplate_1700ul', '4')
	tiprack_20ul = protocol.load_labware('opentrons_96_tiprack_20ul', '10')
	tiprack_300ul = protocol.load_labware('opentrons_96_tiprack_300ul', '11')

	# Add pipettes
	left_pipette = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20ul])
	right_pipette = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack_300ul])
	# Height for the aspirate and dispense doesn't change, so I will state outside the loop. 
	left_pipette.well_bottom_clearance.aspirate = 2
	left_pipette.well_bottom_clearance.dispense = 1
	right_pipette.well_bottom_clearance.aspirate = 2
	right_pipette.well_bottom_clearance.dispense = 1

# Add water via transfer
	'''right_pipette.pick_up_tip()
	right_pipette.aspirate(200, biomek_tube_rack['A1'])
	right_pipette.touch_tip(biomek_tube_rack['A1'], speed = 20.0, v_offset = -3.0)

	volume_in_pipette = float(200)

	for well, water in zip(welllist, waterlist):
		if volume_in_pipette > float(water):
			right_pipette.dispense(float(water), dilution_plate[well])
			right_pipette.touch_tip(dilution_plate[well], speed = 20.0, v_offset = -3.00)
			volume_in_pipette -= float(water)
		else: 
			right_pipette.aspirate(200, biomek_tube_rack['A1'])
			right_pipette.touch_tip(biomek_tube_rack['A1'], speed = 20.0, v_offset = -3.0)
			right_pipette.dispense(float(water), dilution_plate[well])
			right_pipette.touch_tip(dilution_plate[well], speed = 20.0, v_offset = -3.00)
			volume_in_pipette = 200 - float(water)'''
	
	# Add water via distribute (disposal volume is 20ul - the minimum for the pipette)
	right_pipette.distribute(waterlist, biomek_tube_rack['A1'], [dilution_plate.wells_by_name()[well_name] for well_name in welllist], touch_tip=True, disposal_volume=20 )


	# Transfer dna
	for well, dna in zip(welllist, dnalist):
		left_pipette.pick_up_tip()
		left_pipette.aspirate(float(dna), dna_plate[well])
		left_pipette.touch_tip(dna_plate[well], speed = 20.0, v_offset = -3.0) 
		# Blow out height is 0.5 above the dispense height (1 + 0.5) 
		blow_out_height = 1.5
		left_pipette.dispense(float(dna), dilution_plate[well])
		left_pipette.move_to(dilution_plate[well].bottom(blow_out_height), force_direct=True)
		left_pipette.touch_tip(dilution_plate[well], speed = 20.0, v_offset = -4.0) 
		left_pipette.drop_tip()

