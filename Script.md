## <Section 1: Welcome + Hardware>

Welcome to our presentation,I'm ..., and ... we are group ... .Our project is using passive Infrated sensor to control Fan and Light with the help of DAQ device. 

Our main objective is to acquire digital signal from passive IR sensor using USB-6255 DAQ device. Through LABVIEW,we then  determine whether there are heat source in front of it or not (Can be any thing from animal to human), and use it to control the intensity of LED light and speed of fan. Additionally, LED and Fan can be controlled manually or we can schedule it to run at a specific time. <Show TBA label>

About hardware: we created a simple circuit that read the PIR sensor input in Terminal 1: AI0 of USB-6255. Fan and LED are controlled by Analog output terminal AO0, AO1 respectively. We use LM298 DC Motor Driver Controller to amplify the signal from DAQ to 9volt and use it to control the Fan.

<Show Schenematic>

## <Section 2: Front panel>

To control the DAQ, we created a simple Labview virtual instrument. On front panel, there're 1 control panel on the left and 3 sub-tabs on the right.

<Show front-panel>

 On top of the control panel are status section, these 3 boolean will indicate the status of the program:

- DAQ have 3 color:
  - Green mean connected sucessfuly to DAQ
  - Yellow mean simulation mode is on
  - Red mean DAQ connect error

- PIR light will indicate whether sensor value pass the threshold or not
- Fan light will indicate whether fan is running or not

You can control fan and LED manually with Manual section.



Live feed tab show lastest 100 datapoint:

- PIR voltage is the raw data from DAQ
- PIR Sensor show processed sensor data, 1 mean passed the threshold, 0 mean below.
- Fan speed and LED graph show Output data.

__History tab__ show all data from current session, it can also save and load data.

__Configuration tab__ contain all setting available: 

- DAQ device and PIR input terminal choose
- PIR threshold, time before Fan turn off. etc. /et'sedra/

##  <Section 3: Block diargam>

We can break the block diagram in to 2 part: Main program and a event handler

### Main program

The main program is Flat sequence structure. It contain 3 frame which execute in order from left to right

The first frame to set up all required variable each run. This frame will run each time the user press the Run button.

The second frame is to check DAQ connection and determine to run in simulation mode or not: It try to send a signal to turn on fan to the DAQ, the error out from DAQ write wired to simulation check to handle the error.

Last frame contain a while loop to read the sensor data continuously:

- The data from DAQ then sent to 3 independent section: Manipulate Output subVI, Show waveform on Live feed tab, save data on history tab.

- Manipulate subVi handle everything need to control light and fan.

- Set waveform subVi create and combine data to show as waveform on Live feed tab.

In the manipulate output subVI, we first compare the sensor data to the threshold. If it exceed the threshold, _Last on_ variable will be set to current time and trigger the program to start output signal to Fan and LED. The user can control how long the output signal stay on, how fast it goes between on and off, and delay between Fan and LED.

The _set data waveform_ subVI take 3 argument: The waveform before it, current data and datapoint value. and it will replace the input waveform with a new waveform with new data in it. It also output a waveform called subWaveform contain newest data to datapoint.

Beside all of the subVi above, We also implement 3 subVI: Error collector, Error handler and DAQ handler to collect and handle all possible error case happen.

## <Sector 4: End>

We believe that with our project, people can rest assured about forgetting to turn off fans or lights, which can be a waste of electricity.









​    







 