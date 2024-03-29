from opentrons import protocol_api 
import csv 
import os 


metadata = {
    'apiLevel' :  '2.5',
    'protocolName' : 'Pooling Protocol',
    'author' : 'Becky Sadler',
    'description' : 'Pooling protocol for the TWIST library preparation - Without user input of variables'
}

''' 
Protocol Requirements: 

Pipettes: P20 GEN2 single channel 1-20ul (LEFT)

Custom Labware: 
    NonSkirted 96-well plate in flat plate holder (API Load name = 4t_96_wellplate_200ul)
    4x6 rack for 1.5ml microfuge tubes (API Load name = biomekmicrofuge_24_wellplate_1700ul)

Deck Layout:
    Position 10:    OpenTrons 20ul tip rack (opentrons_96_tiprack_20ul)
    Position 8:        NonSkirted 96-well plate in flat plate holder
    Position 7:        4x6 rack for 1.5ml microfuge tubes 

Liquid Handling properties:
    Aspirate height: 2mm from bottom
    Dispense height: 1mm from bottom at start increase by 0.5mm with each loop 
    Touch tip on aspirate: 2-3mm from top
    Blow out on the dispense (+0.5mm above dispense height)

Transfer process:
    Loop through the transfers from a csv file 
    Get tip (NEW ONE)
    Aspirate from well at 2mm 
    Touch tip (2-3mm from top)
    Dispense into well (At 1mm)
    Blow out (+0.5mm above)
    Touch tip (at different points each time)
    Drop tip. 
'''

csv_name = 'Pooling.csv'

csvfile = open(csv_name).readlines()
#Getting the worklist number from the first row of the csv file
firstLine = csvfile.pop(0)
worklist_number = firstLine.split(',')[1]
#start_tip = firstLine.split(',')[3].rstrip()
#Creating reader object to loop through the transfers
reader = csv.DictReader(csvfile)


# Define the protocol desk set up and steps. 
def run(protocol):

    protocol.pause("The worklist about to be processed is {0}. Please ensure this is correct before proceeding.".format(worklist_number))
    # Add labware
    non_skirted_plate = protocol.load_labware('4t_96_wellplate_200ul', '7')
    biomek_tube_rack = protocol.load_labware('biomekmicrofuge_24_wellplate_1700ul', '8')
    tiprack_20ul = protocol.load_labware('opentrons_96_tiprack_20ul', '10')

    # Add pipettes
    pipette = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20ul])
    # Height for the aspirate and dispense (in mm above the bottom of the well/tube)
    pipette.well_bottom_clearance.aspirate = 2
    pipette.well_bottom_clearance.dispense = 1

    # Transfers 
    for row in reader: 
        pipette.pick_up_tip()
        pipette.aspirate(float(row['VolumeToTransfer']), non_skirted_plate[(row['SourceWell'])])
        # Touch tip 8mm from the top of the well
        pipette.touch_tip(non_skirted_plate[(row['SourceWell'])], speed = 20.0, v_offset = -8.0) 
         # Blow out height is 1mm above the bottom of the well
        blow_out_height = 1
        pipette.dispense(float(row['VolumeToTransfer']), biomek_tube_rack[row['DestinationWell']])
        # Touch tip 8mm from the top of the well 
        pipette.touch_tip(biomek_tube_rack[(row['DestinationWell'])], speed = 20.0, v_offset = -8.0) 
        pipette.move_to(biomek_tube_rack[row['DestinationWell']].bottom(blow_out_height), force_direct=True)
        pipette.blow_out()
        pipette.drop_tip()

# Remove the CSV file at the end of the protocol
#os.remove(csv_name)
            

    