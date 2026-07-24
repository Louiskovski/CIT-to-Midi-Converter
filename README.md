# CIT-to-Midi-Converter
Converts CIT (chord Information table) files used in *Super Mario Galaxy* games and *Donkey Kong Jungle Beat* (and maybe more?) in combination with extracted Midis from BMS to a readable Midi file.

## Usage
Command line usage:
`python CIT2Midi.py Input.mid Input.cit Output.mid`

A drag and drop batch file is included.

## Guide
#### 1. Extract the BMS file and its corresponding CIT file
- In *Galaxy*, BMS files are located in `AudioRes/Seqs/JaiSeq.arc`, while CIT files are in `AudioRes/Info/JayChord.arc`.
- *Galaxy*'s BMS files are YAZ0-compressed; you must decompress them.
- You can extract and decompress them using [WiiExplorer](https://github.com/SuperHackio/WiiExplorer).

#### 2. Convert the BMS back to MIDI
- Open the BMS file in [this VGMTrans fork](https://github.com/magcius/vgmtrans).
- Right-click on the file under "Detected Music Files" (on the left) and select "Save as Midi".

#### 3. Place the MIDI and CIT files in the same folder and ensure they share the same filename
(e.g., `Galaxy1.midi` and `Galaxy1.cit`).

#### 4. Drag and drop the MIDI file onto "CIT+Midi to Readable Midi.bat".

#### 5. A new MIDI file containing the added chords will now appear in the same folder.


## Structure

[The note structure corresponds to this](https://github.com/Louiskovski/MIDI-to-BMS-Converter?tab=readme-ov-file#-timing-and-cit-data-generation). This way, you can also use this tool to convert MIDI directly back to CIT and BMS for testing purposes.

## Additional notes
- The tool cannot currently detect the specific time signature; therefore, only a **BEAT_4/4** marker is inserted into the extracted MIDI. If the song uses a different time signature and you wish to convert it back to CIT and BMS using the MIDI-to-BMS converter, you must open the MIDI file in a DAW and adjust the marker name.
- There are special cases (e.g., the *Good Egg Galaxy* theme) involving time signature changes during the song. Consequently, the time signature sections in the extracted MIDI might not align correctly, even if the note positions themselves are accurate.
  - A potential downside of this is that, upon conversion back to CIT and BMS, the resulting BMS file may be significantly larger because it is more difficult to compress.
  - Another downside is, that beats may also not align correctly when converting back.
