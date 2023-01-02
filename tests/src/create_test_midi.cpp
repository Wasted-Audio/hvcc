//
// Programmer:    Craig Stuart Sapp <craig@ccrma.stanford.edu>
// Creation Date: Tue Jan  8 10:08:15 PST 2002
// Last Modified: Mon Feb  9 21:24:41 PST 2015 Updated for C++11.
// Filename:      ...sig/doc/examples/all/createmidifile/createmidifile.cpp
// Syntax:        C++
//
// Description:   Demonstration of how to create a Multi-track MIDI file.
//

#include "MidiFile.h"
#include <iostream>

using namespace std;
using namespace smf;

///////////////////////////////////////////////////////////////////////////
//
// To compile:
// g++ create_test_midi.cpp midifile/src/MidiFile.cpp midifile/src/MidiEventList.cpp midifile/src/MidiMessage.cpp midifile/src/MidiEvent.cpp midifile/src/Binasc.cpp -I midifile/include/ -o create_test_midi
//

int main(int argc, char** argv) {
   MidiFile outputfile;        // create an empty MIDI file with one track
   outputfile.absoluteTicks();  // time information stored as absolute time
                              // (will be coverted to delta time when written)
   // outputfile.addTrack(2);     // Add another two tracks to the MIDI file
   vector<uchar> midievent;     // temporary storage for MIDI events
   midievent.resize(3);        // set the size of the array to 3 bytes
   int tpq = 120;              // default value in MIDI file is 48
   outputfile.setTicksPerQuarterNote(tpq);

   // data to write to MIDI file: (60 = middle C)
   // C5 C  G G A A G-  F F  E  E  D D C-
   int melody[50]  = {72,72,79,79,81,81,79,77,77,76,76,74,74,72,-1};
   int mrhythm[50] = { 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2,-1};

   // C3 C4 E C F C E C D B3 C4 A3 F G C-
   int bass[50] =   {48,60,64,60,65,60,64,60,62,59,60,57,53,55,48,-1};
   int brhythm[50]= { 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2,-1};


   // store a melody line in track 1 (track 0 left empty for conductor info)
   int i = 0;
   int actiontime = 0;      // temporary storage for MIDI event time
   midievent[2] = 64;       // store attack/release velocity for note command
   while (melody[i] >= 0) {
      midievent[0] = 0x90 | 0;     // store a note on command (MIDI channel 0)
      midievent[1] = melody[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * mrhythm[i];
      midievent[0] = 0x80 | 0;     // store a note off command (MIDI channel 0)
      outputfile.addEvent(0, actiontime, midievent);
      i++;
   }

   // append a bass line on channel 1
   i = 0;
   actiontime = 0;
   midievent[2] = 64;
   while (bass[i] >= 0) {
      midievent[0] = 0x90 | 1;
      midievent[1] = bass[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * brhythm[i];
      midievent[0] = 0x80 | 1;
      outputfile.addEvent(0, actiontime, midievent);
      i++;
   }

   int cc0[50] = {73,74,75,76,77,78,79,77,76,75,76,75,74,73,-1};
   int cc0rhythm[50] = {1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2,-1};


   int cc1[50] = {59,60,61,62,63,62,63,62,61,60,59,58,57,56,55,-1};
   int cc1rhythm[50]= {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2,-1};

   int cc2[50] = {59,60,61,62,63,62,63,62,61,60,59,58,-1};
   int cc2rhythm[50]= {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2,-1};

   // append CC message to channel 0
   i = 0;
   actiontime = 0;
   midievent[1] = 13;
   while (cc0[i] >= 0) {
      midievent[0] = 0xB0 | 0;
      midievent[2] = cc0[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * cc1rhythm[i];
      i++;
   }

   // append second CC message to channel 1
   i = 0;
   actiontime = 0;
   midievent[1] = 15;
   while (cc1[i] >= 0) {
      midievent[0] = 0xB0 | 1;
      midievent[2] = cc1[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * cc1rhythm[i];
      i++;
   }

   // append third CC message to channel 2
   i = 0;
   actiontime = 0;
   midievent[1] = 13;
   while (cc2[i] >= 0) {
      midievent[0] = 0xB0 | 2;
      midievent[2] = cc2[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * cc2rhythm[i];
      i++;
   }

   int bend0[50] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1};
   int bend0rhythm[50] = {1, 1, 1, 1, 1, 1, 1, 1, 1, 2, -1};

   int bend1[50] = {8192, 8193, 8194, 8195, 8196, 8197, 8198, 8199, 8200, -1};
   int bend1rhythm[50] = {1, 1, 1, 1, 1, 1, 1, 1, 1 -1};

   // append pitch bend to channel 0
   i = 0;
   actiontime = 0;
   while (bend0[i] >= 0) {
      uint8_t lsb = bend0[i] & 0x7F;
      uint8_t msb = (bend0[i] >> 7) & 0x7F;

      midievent[0] = 0xE0 | 0;
      midievent[1] = lsb;
      midievent[2] = msb;
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * bend0rhythm[i];
      i++;
   }
   
   // append second pitch bend to channel 1
   i = 0;
   actiontime = 0;
   while (bend1[i] >= 0) {
      uint8_t lsb = bend1[i] & 0x7F;
      uint8_t msb = (bend1[i] >> 7) & 0x7F;

      midievent[0] = 0xE0 | 1;
      midievent[1] = lsb;
      midievent[2] = msb;
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * bend1rhythm[i];
      i++;
   }

   int polytouch0[50] = {0, 1, 2, 3, 4, 5, 6, 7, 8, -1};
   int polytouch0rhythm[50] = {1, 1, 1, 1, 1, 1, 2, 1, 1 -1};

   int polytouch1[50] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, -1};
   int polytouch1rhythm[50] = {1, 1, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1 -1};

   // append polytouch to channel 0
   i = 0;
   actiontime = 0;
   midievent[1] = 22; // note
   while (polytouch0[i] >= 0) {
      midievent[0] = 0xA0 | 0;
      midievent[2] = polytouch0[i]; // pressure
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * polytouch0rhythm[i];
      i++;
   }

   // append polytouch to channel 1
   i = 0;
   actiontime = 0;
   midievent[1] = 22; // note
   while (polytouch1[i] >= 0) {
      midievent[0] = 0xA0 | 1; // pressure
      midievent[2] = polytouch1[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * polytouch1rhythm[i];
      i++;
   }

   midievent.resize(2);        // following events only use 2 bytes

   int pgmin0[50] = {0, 1, 10, 14, 16, 20, -1};
   int pgmin0rhythm[50] = {1, 2, 1, 1, 2, 1, -1};

   int pgmin1[50] = {127, 100, 30, 5, -1};
   int pgmin1rhythm[50] = {1, 1, 2, 1, -1};

   // append program change to channel 0
   i = 0;
   actiontime = 0;
   while (pgmin0[i] >= 0) {
      midievent[0] = 0xC0 | 0;
      midievent[1] = pgmin0[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * pgmin0rhythm[i];
      i++;
   }

   // append second program change to channel 1
   i = 0;
   actiontime = 0;
   while (pgmin1[i] >= 0) {
      midievent[0] = 0xC0 | 1;
      midievent[1] = pgmin1[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * pgmin1rhythm[i];
      i++;
   }

   int touchin0[50] = {0, 1, 2, 3, 4, 5, -1};
   int touchin0rhythm[50] = {1, 2, 2, 1, 2, 1, -1};

   int touchin1[50] = {0, 1, 2, 3, 4, 3, 2, 1, 0 -1};
   int touchin1rhythm[50] = {1, 3, 2, 1, 1, 1, 1, 1, -1};

   // append channel pressure to channel 0
   i = 0;
   actiontime = 0;
   while (touchin0[i] >= 0) {
      midievent[0] = 0xD0 | 0;
      midievent[1] = touchin0[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * touchin0rhythm[i];
      i++;
   }

   // append channel pressure change to channel 1
   i = 0;
   actiontime = 0;
   while (touchin1[i] >= 0) {
      midievent[0] = 0xD0 | 1;
      midievent[1] = touchin1[i];
      outputfile.addEvent(0, actiontime, midievent);
      actiontime += tpq * touchin1rhythm[i];
      i++;
   }

   outputfile.sortTracks();         // make sure data is in correct order
   outputfile.write("test_midi.mid"); // write Standard MIDI File twinkle.mid
   return 0;
}


/*  FUNCTIONS available in the MidiFile class:

void absoluteTime(void);
   Set the time information to absolute time.
int addEvent(int aTrack, int aTime, vector<uchar>& midiData);
   Add an event to the end of a MIDI track.
int addTrack(void);
   Add an empty track to the MIDI file.
int addTrack(int count);
   Add a number of empty tracks to the MIDI file.
void deltaTime(void);
   Set the time information to delta time.
void deleteTrack(int aTrack);
   remove a track from the MIDI file.
void erase(void);
   Empty the contents of the MIDI file, leaving one track with no data.
MFEvent& getEvent(int aTrack, int anIndex);
   Return a MIDI event from the Track.
int getTimeState(void);
   Indicates if the timestate is TIME_STATE_ABSOLUTE or TIME_STATE_DELTA.
int getTrackState(void);
   Indicates if the tracks are being processed as multiple tracks or
   as a single track.
int getTicksPerQuarterNote(void);
   Returns the ticks per quarter note value from the MIDI file.
int getTrackCount(void);
   Returns the number of tracks in the MIDI file.
int getNumTracks(void);
   Alias for getTrackCount();
int getNumEvents(int aTrack);
   Return the number of events present in the given track.
void joinTracks(void);
   Merge all tracks together into one track.  This function is reversable,
   unlike mergeTracks().
void mergeTracks(int aTrack1, int aTrack2);
   Combine the two tracks into a single track stored in Track1.  Track2
   is deleted.
int read(char* aFile);
   Read the contents of a MIDI file into the MidiFile class data structure
void setTicksPerQuarterNote    (int ticks);
   Set the MIDI file's ticks per quarter note information
void sortTrack(vector<MFEvent>& trackData);
   If in absolute time, sort particular track into correct time order.
void sortTracks(void);
   If in absolute time, sort tracks into correct time order.

*/



