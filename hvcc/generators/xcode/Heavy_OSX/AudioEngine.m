/**
 * Copyright (C) 2014-2018 Enzien Audio, Ltd.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#import <stdio.h>
#import "AudioEngine.h"
#import "Heavy_heavy.h"
#import "MainViewController.h"

static void printHook(HeavyContextInterface *c, const char *name, const char *s, const HvMessage *m) {
  double timestampMs = 1000.0 * ((double) hv_msg_getTimestamp(m)) / hv_getSampleRate(c);
	NSLog(@"[%0.3fms] %s: %s", timestampMs, name, s);
}

static void checkError(OSStatus error, const char *operation) {
	if (error == noErr) return;

	char errorString[20] = {};
	// See if it appears to be a 4-char code
	*(UInt32 *)(errorString+1) = CFSwapInt32HostToBig(error);
	if (isprint(errorString[1]) && isprint(errorString[2]) &&
		isprint(errorString[3]) && isprint(errorString[4])) {
		errorString[0] = errorString[5] = '\'';
		errorString[6] = '\0';
	} else {
		sprintf(errorString, "%d", (int)error);
	}
	fprintf(stderr, "Error: %s (%s)\n", operation, errorString);

	exit(1);
}

OSStatus AudioEngineRenderProc(void *inRefCon,
							   AudioUnitRenderActionFlags *ioActionsFlags,
							   const AudioTimeStamp *inTimeStamp,
							   UInt32 inBusNumber,
							   UInt32 inNumberFrames,
							   AudioBufferList *ioData) {
//  const double tick_rc = CFAbsoluteTimeGetCurrent();

  AudioEngine *audioEngine = (__bridge AudioEngine *) inRefCon;

  [audioEngine->lock lock];

  int n = 0;
  double tock = 0.0;
  switch (hv_getNumOutputChannels(audioEngine.context)) {
    case 2: {
      const double tick = CFAbsoluteTimeGetCurrent();
      float *outputBuffers[2] = {
        (float *) ioData->mBuffers[0].mData,
        (float *) ioData->mBuffers[1].mData
      };
      n = hv_process(audioEngine.context, NULL, outputBuffers, inNumberFrames);
      tock = CFAbsoluteTimeGetCurrent() - tick;
      if (tinywav_isOpen(&audioEngine->tinywav)) {
        tinywav_write_f(&audioEngine->tinywav, outputBuffers, inNumberFrames);
      }
      break;
    }
    case 1: {
      const double tick = CFAbsoluteTimeGetCurrent();
      float *b = (float *) ioData->mBuffers[0].mData;
      n = hv_process(audioEngine.context,
          NULL, &b, inNumberFrames);
      tock = CFAbsoluteTimeGetCurrent() - tick;
      if (tinywav_isOpen(&audioEngine->tinywav)) {
        tinywav_write_f(&audioEngine->tinywav, &b, inNumberFrames);
      }
      break;
    }
    default: break;
  }

//  const double tock_rc = CFAbsoluteTimeGetCurrent() - tick_rc;
//  NSLog(@"%iµs (%iµs) @ %i/%gHz (%0.3f%% CPU)",
//        (int) (1000000.0 * tock), // execution time of heavy callback
//        (int) (1000000.0 * tock_rc), // execution time of entire render callback
//        (int) inNumberFrames,
//        hv_getSampleRate(audioEngine.context),
//        100.0*(tock/(inNumberFrames/hv_getSampleRate(audioEngine.context))));

  [audioEngine->lock unlock];

  dispatch_async(dispatch_get_main_queue(), ^{
    [audioEngine->viewController updateCpuWithDuration:tock
        andFraction:tock/(inNumberFrames/hv_getSampleRate(audioEngine.context))];
  });

  if (n != inNumberFrames) {
    NSLog(@"WARNING: Heavy did not process the full frame: %i/%i", n, inNumberFrames);
  }

	return noErr;
}

@implementation AudioEngine

+ (void)update:(AudioEngine *)engine {
  while (engine.keepRunning) {
    unsigned int sendHash = 0;
    HvMessage *msg = (HvMessage *) malloc(hv_msg_getByteSize(100));

    while (hv_getNextSentMessage(engine.context, &sendHash, msg, (hv_uint32_t) hv_msg_getByteSize(100))) {
      if (sendHash == hv_stringToHash("hello")) {
        if (hv_msg_hasFormat(msg, "f")) {
          NSLog(@"hello: %f", hv_msg_getFloat(msg, 0));
        }
      }
      if (sendHash == hv_stringToHash("finished")) {
        if (hv_msg_hasFormat(msg, "b")) {
          NSLog(@"finished");
        }
      }
    }

    [NSThread sleepForTimeInterval:0.0001f];
  }
}

- (id)initWithView:(MainViewController *)view {
  self = [super init];
  if (self) {
    _sampleRate = 48000.0;
    _context = hv_heavy_new_with_options(_sampleRate, 10, 2, 2);
    hv_setPrintHook(_context, &printHook);

    _blockSize = 512;
    _counter = 0;
    _numOutputChannels = hv_getNumOutputChannels(_context);
    lock = [[NSLock alloc] init];
    self->viewController = view;
    memset(&tinywav, 0, sizeof(TinyWav));
    [self initialiseAudioUnit];
  }
  return self;
}

- (void)initialiseAudioUnit {

	// Generate output audio unit
	AudioComponentDescription outputcd = {0};
	outputcd.componentType = kAudioUnitType_Output;
	outputcd.componentSubType = kAudioUnitSubType_DefaultOutput;
	outputcd.componentManufacturer = kAudioUnitManufacturer_Apple;

	AudioComponent comp = AudioComponentFindNext(NULL, &outputcd);
	if (comp == NULL) {
		NSLog(@"Can't get output unit");
		exit(-1);
	}

	checkError(AudioComponentInstanceNew(comp, &_outputUnit),
			   "Couldn't open component for outputUnit");

	// Get stream format
	AudioStreamBasicDescription asbd = {0};
	UInt32 size = sizeof(asbd);
	checkError(AudioUnitGetProperty(_outputUnit,
									kAudioUnitProperty_StreamFormat,
									kAudioUnitScope_Input,
									0,
									&asbd,
									&size),
			   "AudioUnitGetProperty (kAudioUnitProperty_StreamFormat) failed");

	// Set stream format
	asbd.mBytesPerPacket = 4;
	asbd.mFramesPerPacket = 1;
	asbd.mChannelsPerFrame = _numOutputChannels;
	asbd.mBitsPerChannel = 32;
	asbd.mFormatID = kAudioFormatLinearPCM;
	asbd.mFormatFlags = kAudioFormatFlagIsNonInterleaved | kAudioFormatFlagIsFloat | kAudioFormatFlagIsPacked;
  asbd.mSampleRate = _sampleRate;
	[self printStreamDescription:asbd];

	checkError(AudioUnitSetProperty(_outputUnit,
									kAudioUnitProperty_StreamFormat,
									kAudioUnitScope_Input,
									0,
									&asbd,
									size),
			   "AudioUnitSetProperty (kAudioUnitProperty_StreamFormat) failed");

	// Register the render callback
	AURenderCallbackStruct input;
	input.inputProc = AudioEngineRenderProc;
	input.inputProcRefCon = (__bridge void *)(self);
	checkError(AudioUnitSetProperty(_outputUnit,
									kAudioUnitProperty_SetRenderCallback,
									kAudioUnitScope_Input,
									0,
									&input,
									sizeof(input)),
			   "AudioUnitSetProperty (kAudioUnitProperty_SetRenderCallback) failed");

	// Initialise the unit
	checkError(AudioUnitInitialize(_outputUnit),
			   "Couldn't initialise outut unit");

  // Make sure samplerate is correctly set after initialisation
	_sampleRate = asbd.mSampleRate;
}

- (void)start {
	checkError(AudioOutputUnitStart(_outputUnit),
			   "Couldn't start output unit");
  _keepRunning = true;
//  [NSThread detachNewThreadSelector:@selector(update:) toTarget:[AudioEngine class] withObject:self];
}

- (void)stop {
  _keepRunning = false;
	checkError(AudioOutputUnitStop(_outputUnit),
			   "Couldn't stop output unit");
}

- (void)sendFloat:(float)value toReceiver:(NSString *)receiverName {
  if (self.context != NULL) {
    [lock lock];
    hv_sendFloatToReceiver(self.context, hv_stringToHash([receiverName cStringUsingEncoding:NSASCIIStringEncoding]), value);
    [lock unlock];
  }
}

- (void)destroy {
  AudioOutputUnitStop(_outputUnit);
  AudioUnitUninitialize(_outputUnit);
  AudioComponentInstanceDispose(_outputUnit);
  _keepRunning = false;
}

- (void)printStreamDescription:(const AudioStreamBasicDescription)asbd {
  NSLog(@"AudioStreamBasicDescription:");
  NSLog(@"\t Sample Rate:\t\t %g", asbd.mSampleRate);
  NSLog(@"\t Bytes Per Packet:\t %d", asbd.mBytesPerPacket);
  NSLog(@"\t Frames Per Packet:\t %d", asbd.mFramesPerPacket);
  NSLog(@"\t Channels Per Frame: %d", asbd.mChannelsPerFrame);
  NSLog(@"\t Bits Per Channel:\t %d", asbd.mBitsPerChannel);

  char formatID[20] = {};
  *(UInt32 *)(formatID+1) = CFSwapInt32HostToBig(asbd.mFormatID);
  if (isprint(formatID[1]) && isprint(formatID[2]) &&
    isprint(formatID[3]) && isprint(formatID[4])) {
    formatID[0] = formatID[5] = '\'';
    formatID[6] = '\0';
    NSLog(@"\t Format ID:\t\t\t %s", formatID);
  } else {
    NSLog(@"\t Format ID:\t\t\t unknown");
  }

  NSLog(@"\t Format Flags:");
  if (asbd.mFormatFlags & kAudioFormatFlagIsFloat) NSLog(@"\t\t kAudioFormatFlagIsFloat");
  if (asbd.mFormatFlags & kAudioFormatFlagIsBigEndian) NSLog(@"\t\t kAudioFormatFlagIsBigEndian");
  if (asbd.mFormatFlags & kAudioFormatFlagIsSignedInteger) NSLog(@"\t\t kAudioFormatFlagIsSignedInteger");
  if (asbd.mFormatFlags & kAudioFormatFlagIsPacked) NSLog(@"\t\t kAudioFormatFlagIsPacked");
  if (asbd.mFormatFlags & kAudioFormatFlagIsAlignedHigh) NSLog(@"\t\t kAudioFormatFlagIsAlignedHigh");
  if (asbd.mFormatFlags & kAudioFormatFlagIsNonInterleaved) NSLog(@"\t\t kAudioFormatFlagIsNonInterleaved");
  if (asbd.mFormatFlags & kAudioFormatFlagIsNonMixable) NSLog(@"\t\t kAudioFormatFlagIsNonMixable");
  if (asbd.mFormatFlags & kAudioFormatFlagIsNonMixable) NSLog(@"\t\t kAudioFormatFlagsAreAllClear");
}

- (void)recordAudioToFile:(NSString *)filepath {
  [lock lock];
  tinywav_new(&tinywav,
      (int16_t) hv_getNumOutputChannels(_context), (int32_t) _sampleRate,
      TW_FLOAT32, TW_SPLIT,
      [filepath cStringUsingEncoding:NSASCIIStringEncoding]);
  [lock unlock];
}

- (void)stopRecordingAudio {
  [lock lock];
  tinywav_close(&tinywav);
  [lock unlock];
}

@end
