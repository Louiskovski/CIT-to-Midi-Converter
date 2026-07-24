import sys
import struct
import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack


### Command line stuff
if __name__ == "__main__":
    Input_MIDI = sys.argv[1]
    Input_CIT = sys.argv[2]
    Output_MIDI = sys.argv[3]

    
    print("--- 🎵 CIT to Midi v.0.5.2 🎶 ---") # to check Version
    print()



## Step 1: collect infos from CIT file:

with open(Input_CIT, "rb") as CIT:

    ##get number of chord and scales
    CIT.seek(0x0C)
    value = CIT.read(2)
    ChordNo = int.from_bytes(value, byteorder='big')
    CIT.seek(0x0E)
    value = CIT.read(2)
    ScaleNo = int.from_bytes(value, byteorder='big')
    
    print()
    print("Number of Chords: " + str(ChordNo))
    print("Number of Scales: " + str(ScaleNo))
    print()
    
    CIT.seek(0x10)
    
    
    # Collect Offsets
    
    ChordOffsetList = []
    for ID in range(ChordNo):

        value = int.from_bytes(CIT.read(4), byteorder='big')
        ChordOffsetList.append(value)
      
        #CIT.seek(4, 1) # 4 bytes weitergehen

      
    ScalesOffsetList = []
    for ID in range(ScaleNo):
    
        value = int.from_bytes(CIT.read(4), byteorder='big')
        ScalesOffsetList.append(value)
        
        #CIT.seek(4, 1) # 4 bytes weitergehen
        
        
    
    #### Collect Notes -------------
    
    #Dictionary
    ChordNotesDict = {}
    ChordNotes = []
    ScaleNotesDict = {}
    ScaleNotes = []
    
    
    ## -- Chord Notes --
    for ID in range(ChordNo):
        
        CIT.seek(ChordOffsetList[ID]) #hinspringen
        
        for x in range(8): #für jede Note
            value = int.from_bytes(CIT.read(1), byteorder='big') #Achtung, damit geht der Cursor weiter!
            if x == 0:
                if value == 0x00:
                    ChordNotes.append(48)
                elif value == 0x01:
                    ChordNotes.append(49)
                elif value == 0x02:
                    ChordNotes.append(50)
                elif value == 0x03:
                    ChordNotes.append(51)
                elif value == 0x04:
                    ChordNotes.append(52)
                elif value == 0x05:
                    ChordNotes.append(53)
                elif value == 0x06:
                    ChordNotes.append(54)
                elif value == 0x07:
                    ChordNotes.append(55)
                elif value == 0x08:
                    ChordNotes.append(56)
                elif value == 0x09:
                    ChordNotes.append(57)
                elif value == 0x0A:
                    ChordNotes.append(58)
                elif value == 0x0B:
                    ChordNotes.append(59)
            else:
                if value == 0x00:
                    ChordNotes.append(60)
                elif value == 0x01:
                    ChordNotes.append(61)
                elif value == 0x02:
                    ChordNotes.append(62)
                elif value == 0x03:
                    ChordNotes.append(63)
                elif value == 0x04:
                    ChordNotes.append(64)
                elif value == 0x05:
                    ChordNotes.append(65)
                elif value == 0x06:
                    ChordNotes.append(66)
                elif value == 0x07:
                    ChordNotes.append(67)
                elif value == 0x08:
                    ChordNotes.append(68)
                elif value == 0x09:
                    ChordNotes.append(69)
                elif value == 0x0A:
                    ChordNotes.append(70)
                elif value == 0x0B:
                    ChordNotes.append(71)
            
            
        ChordNotesDict[ID] = ChordNotes #Noten mit ID als Schluessl speichern
        ChordNotes = [] #Liste leeren
        
    ## -- Scale Notes --
    for ID in range(ScaleNo):
        
        CIT.seek(ScalesOffsetList[ID]) #hinspringen
        
        
        #get individual Pointers
        PointerA = int.from_bytes(CIT.read(4), byteorder='big')
        PointerB = int.from_bytes(CIT.read(4), byteorder='big')
        #print(PointerA)
        #print(PointerB)
        
        #Check if the stuff is valid
        if not PointerA == PointerB: # Midi-to-BMS Tool uses the same pointers to save file space
            #Check if notepairs are the same.
            CIT.seek(PointerA) #hinspringen
            ScaleAnotes = int.from_bytes(CIT.read(1), byteorder='big')
            CIT.seek(PointerB) #hinspringen
            ScaleBnotes = int.from_bytes(CIT.read(1), byteorder='big')
            
            if not ScaleAnotes == ScaleBnotes:
                raise ValueError("\n \n \n====================\n--- SPECIAL CASE --- \n====================\n\nScale Note Pair " + str(ID) + " uses notepairs that are not equal! \n \nIf this is a vanilla CIT file, tell this the Community! This is a new discovery!!")

            
        CIT.seek(PointerA) #hinspringen
        
        for x in range(12): #für jede Note
            value = int.from_bytes(CIT.read(1), byteorder='big') #Achtung, damit geht der Cursor weiter!
            if value == 0x00:
                ScaleNotes.append(72)
            elif value == 0x01:
                ScaleNotes.append(73)
            elif value == 0x02:
                ScaleNotes.append(74)
            elif value == 0x03:
                ScaleNotes.append(75)
            elif value == 0x04:
                ScaleNotes.append(76)
            elif value == 0x05:
                ScaleNotes.append(77)
            elif value == 0x06:
                ScaleNotes.append(78)
            elif value == 0x07:
                ScaleNotes.append(79)
            elif value == 0x08:
                ScaleNotes.append(80)
            elif value == 0x09:
                ScaleNotes.append(81)
            elif value == 0x0A:
                ScaleNotes.append(82)
            elif value == 0x0B:
                ScaleNotes.append(83)

            
        ScaleNotesDict[ID] = ScaleNotes #Noten mit ID als Schluessl speichern
        ScaleNotes = [] #Liste leeren

        
        
## STEP 2: take midi and replace Bank/Program Change commands with notes from the CIT file:

mid = MidiFile(Input_MIDI)
MidiChannel = 1
wechsel_liste = []
for i, track in enumerate(mid.tracks):
    #print(f"- Track {i}: {track.name} - ")
    
    # Tick-counter startet für jeden Track bei 0
    absoluter_tick = 0
    
    for msg in track:
        # also der Delta-Tick muss IMMER aufaddiert werden, unabhängig von Kanal oder Typ!
        absoluter_tick += msg.time
        
        #kanalfilter
        
        BankCheck = 0
        
        if hasattr(msg, 'channel') and msg.channel == MidiChannel:

            # if msg.type == 'program_change':
                # ChordCMD = msg.program
                # MidiCMDpositions[absoluter_tick] = ChordCMD
            # elif msg.type == 'control_change' and msg.control in (0, 32):
                # ScaleCMD = msg.value
                # MidiCMDpositions[absoluter_tick] = ScaleCMD


            if msg.type == 'program_change':
                wechsel_liste.append({'ChordChangeCMD': msg.program, 'tick': absoluter_tick})
            elif msg.type == 'control_change' and msg.control == 32: #(0, 32):
                wechsel_liste.append({'ScaleChangeCMD': msg.value,'tick': absoluter_tick})
                    
                    
#print(wechsel_liste)


data = wechsel_liste

#Nach Tick gruppieren
ticks = {}

for entry in data:
    tick = entry['tick']
    ticks.setdefault(tick, {}).update(entry)


#Die beiden Chord und Scale Listen kombninieren, einfacher zum loopen
AllCMDs = []
current_scale = None
current_chord = None

for tick in sorted(ticks):
    entry = ticks[tick]

    if 'ScaleChangeCMD' in entry:
        current_scale = entry['ScaleChangeCMD']

    if 'ChordChangeCMD' in entry:
        current_chord = entry['ChordChangeCMD']

    AllCMDs.append({'tick': tick,'ScaleChangeCMD': current_scale, 'ChordChangeCMD': current_chord})

#print("HIER:")
#print(AllCMDs)






mid = MidiFile(Input_MIDI)
old_track = mid.tracks[1]  # VGMtrans verschiebt die Kanäle um eins, lol

AllMidi_events = []
currentTick = 0

# Track 0: Meta-Events übernehmen
AllMidi_events = []

currentTick = 0
for msg in mid.tracks[0]:
    currentTick += msg.time
    if msg.is_meta:
        AllMidi_events.append((currentTick, msg))

#laenge kriegen
currentTick = 0
for msg in mid.tracks[1]:
    currentTick += msg.time
LetzterTick = currentTick



# #Beat ermittlen #Nee klappt noch net. Irgendwie ist die Anzahl der Ticks in BMS weird ?!
# if LetzterTick % 480 == 0:
    # print("Possibly 4/4 beat")
    # AllMidi_events.append((LetzterTick/2, MetaMessage('marker'), text('BEAT_4/4'), time(0)))
# elif LetzterTick % 360 == 0:
    # print("Possibly 3/4 beat")
    # AllMidi_events.append((LetzterTick/2, MetaMessage('marker'), text('BEAT_3/4'), time(0)))
# elif LetzterTick % 600 == 0:
    # print("Possibly 5/4 beat")
    # AllMidi_events.append((LetzterTick/2, MetaMessage('marker'), text('BEAT_5/4'), time(0)))
# else:
    # print("Beat not clearly discernible.")
    
    
    
#temp Fix: einfach immer 4/4 Takt:
AllMidi_events.append((int(LetzterTick / 2),MetaMessage('marker', text='BEAT_4/4', time=0)))

#temp Fix: Loop Points an Start und letzten Tick
AllMidi_events.append((int(0),MetaMessage('marker', text='LoopStart', time=0)))
AllMidi_events.append((int(LetzterTick+1),MetaMessage('marker', text='LoopEnd', time=0)))


## Harfe als Instrument setzen
#Bank Select MSB
AllMidi_events.append((0, Message('control_change',channel=0,control=0,value=0,time=0)))
#Bank Select LSB
AllMidi_events.append((0, Message('control_change',channel=0,control=32,value=0,time=0)))
#Program Change
AllMidi_events.append((0, Message('program_change',channel=0,program=11,time=0)))
    



def AddNotes(Events, Note, Velocity, StartTick, EndTick):
    # Note On hinzufügen
    Events.append((StartTick, Message('note_on', note=Note, velocity=Velocity, time=0)))
    # Note Off hinzufügen
    Events.append((EndTick, Message('note_off', note=Note, velocity=64, channel=0, time=0)))




for X in range(len(AllCMDs)):

    TickStart = AllCMDs[X]["tick"]
    try:
        TickEnd = (AllCMDs[X+1]["tick"]) #- 1
    except:
        TickEnd = LetzterTick
    Scale = AllCMDs[X]["ScaleChangeCMD"]
    Chord = AllCMDs[X]["ChordChangeCMD"]
    #print(TickEnd)
    
    # Add Chord notes
    for Z in ChordNotesDict[Chord]:
        AddNotes(AllMidi_events, Z, 90, TickStart, TickEnd)
    

    # Add Scale notes
    Counter = 0
    for Y in ScaleNotesDict[Scale]:
    
        #damit die noten aufsteigend sind
        Counter = Counter +   18
        StartTick = TickStart+Counter
        EndTick = TickStart+Counter+6
        
        if StartTick >= TickEnd:
            #print()
            StartTick = TickEnd -4
        if EndTick >= TickEnd:
            EndTick = TickEnd -2
            #print()
        
        
        AddNotes(AllMidi_events, Y, 50, StartTick, EndTick)





#Events sortieren nach dem absoluten Tick
AllMidi_events.sort(key=lambda x: x[0])

#neuen Track erstellen
Newtrack = MidiTrack()
last_tick = 0

for abs_tick, msg in AllMidi_events:
    delta_time = abs_tick - last_tick
    new_msg = msg.copy(time=delta_time)
    Newtrack.append(new_msg)
    last_tick = abs_tick




# Speichern
NewMidi = MidiFile(ticks_per_beat=mid.ticks_per_beat)
NewMidi.tracks.append(Newtrack)
NewMidi.save(Output_MIDI)

print()
print("✅ Done!")
print()
print()
print()
