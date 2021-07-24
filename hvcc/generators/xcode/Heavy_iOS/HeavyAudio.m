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

#import <Accelerate/Accelerate.h>
#import <AVFoundation/AVFoundation.h>
#import "HeavyAudio.h"
#include "TPCircularBuffer.h"

#import "Heavy_heavy.h"

#define SAMPLE_RATE 44100.0
#define BLOCK_SIZE 1024

@interface HeavyAudio() {
@public


@private
  AudioUnit audioUnit;
  TPCircularBuffer inputQueue;
  HeavyContextInterface *hv;
}
@end

@implementation HeavyAudio

static void printHook(HeavyContextInterface *context, const char *printName, const char *str, const HvMessage *msg) {
  NSLog(@"> [%s@%0.3fms] %s", printName, hv_getCurrentTime(context), str);
}

static void sendHook(HeavyContextInterface *context, const char *sendName, hv_uint32_t sendHash, const HvMessage *msg) {
  NSLog(@"> [%s@%0.3fms] received message via sendhook", sendName, hv_getCurrentTime(context));
}

- (HeavyAudio *)init {
  self = [super init];
  if (self != nil) {

    hv = hv_heavy_new(SAMPLE_RATE);

    // assert that the patch isn't claiming more input or output channels than we care to support
    assert(hv_getNumInputChannels(hv) < 2); // 0 or 1
    if (hv_getNumInputChannels(hv) >= 2) {
      NSLog(@"WARNING: Heavy requires more than one channel of input. "
             "This is NOT supported by this code. Undefined behaviour will result.");
    }

    assert(hv_getNumOutputChannels(hv) <= 2); // 0, 1, or 2

    // make input queue 4 times larger than necessary to protect against IO jitter
    // NOTE(mhroth): buffer length should never be zero
    TPCircularBufferInit( &inputQueue,
        MAX(1,hv_getNumInputChannels(hv)) * BLOCK_SIZE * 4 * sizeof(Float32));

    hv_setPrintHook(hv, printHook);
//    hv_setSendHook(hv, sendHook);
    hv_setUserData(hv, (__bridge void *) self);
  }
  return self;
}

- (void)dealloc {
  hv_delete(hv);
  TPCircularBufferCleanup(&inputQueue);
}

- (void)initialiseAudioSession {
    NSError *error = nil;

    [[AVAudioSession sharedInstance] setCategory:AVAudioSessionCategoryPlayAndRecord error:&error];
    [[AVAudioSession sharedInstance] setMode:AVAudioSessionModeMeasurement error:&error];

    // set the preferred sample rate
    [[AVAudioSession sharedInstance] setPreferredSampleRate:SAMPLE_RATE error:&error];

    // set the preferred block size
    const NSTimeInterval bufferDuration = BLOCK_SIZE / SAMPLE_RATE; // buffer duration in seconds
    [[AVAudioSession sharedInstance] setPreferredIOBufferDuration:bufferDuration error:&error];

    // register route change and interruption listeners
    [[NSNotificationCenter defaultCenter] addObserver:self
            selector:@selector(audioSessionRouteChangeListener:)
            name:AVAudioSessionRouteChangeNotification
            object:[AVAudioSession sharedInstance]];
    [[NSNotificationCenter defaultCenter] addObserver:self
            selector:@selector(audioSessionInterruptionListener:)
            name:AVAudioSessionInterruptionNotification
            object:[AVAudioSession sharedInstance]];

    [[AVAudioSession sharedInstance] setActive:YES error:&error];

    if (error == nil) {
        NSLog(@"++++ Audio Session successfully initialised.");
    } else {
        NSLog(@"There was an error initialising the Audio Session: %@", error.localizedDescription);
    }
}

// the interrupt listener for when the audio route changes (e.g., headphones are added or removed)
// this will be preceeded by a (begin) interruption, and proceeded by an (end) interruption
- (void)audioSessionRouteChangeListener:(NSNotification *)notification {
    NSLog(@"audioSessionRouteChangeListener: %@", notification.userInfo);
}

- (void)audioSessionInterruptionListener:(NSNotification *)notification {
    // get the interruption type
    NSNumber *type = [notification.userInfo objectForKey:AVAudioSessionInterruptionTypeKey];
    switch (type.intValue) {
        case kAudioSessionEndInterruption: {
            NSLog(@"kAudioSessionEndInterruption: %@", notification.userInfo);
            break;
        }
        case kAudioSessionBeginInterruption: {
            NSLog(@"kAudioSessionBeginInterruption: %@", notification.userInfo);
            break;
        }
        default: break;
    }
}

- (void)initialiseAudioUnit {
    AudioComponentDescription desc;
    desc.componentType = kAudioUnitType_Output;
    desc.componentSubType = kAudioUnitSubType_RemoteIO;
    desc.componentManufacturer = kAudioUnitManufacturer_Apple;
    desc.componentFlags = 0;
    desc.componentFlagsMask = 0;

    AudioComponent comp = AudioComponentFindNext(NULL, &desc);

    OSStatus status = AudioComponentInstanceNew(comp, &audioUnit);

    const UInt32 setProperty = 1;
    const UInt32 unsetProperty = 0;

    // https://developer.apple.com/library/ios/documentation/MusicAudio/Conceptual/AudioUnitHostingGuide_iOS/AudioUnitHostingFundamentals/AudioUnitHostingFundamentals.html

    // Enable mic
    status = AudioUnitSetProperty(audioUnit, kAudioOutputUnitProperty_EnableIO,
            kAudioUnitScope_Input, 1, &setProperty, sizeof(setProperty));

    // Add an output to the speaker
    status = AudioUnitSetProperty(audioUnit, kAudioOutputUnitProperty_EnableIO,
            kAudioUnitScope_Output, 0, &setProperty, sizeof(setProperty));

    // Set the input format to 32-bit, single channel, float, linear PCM
    const Float64 kSampleRate = SAMPLE_RATE;

    // set the sample rate on the input bus
    AudioUnitSetProperty(audioUnit, kAudioUnitProperty_SampleRate,
            kAudioUnitScope_Output, 1, &kSampleRate, sizeof(kSampleRate));

    // set the sample rate on the output bus
    AudioUnitSetProperty(audioUnit, kAudioUnitProperty_SampleRate,
            kAudioUnitScope_Input, 0, &kSampleRate, sizeof(kSampleRate));

    // mono input stream from the microphone
    AudioStreamBasicDescription inputStreamFormat;
    inputStreamFormat.mSampleRate = kSampleRate;
    inputStreamFormat.mFormatID = kAudioFormatLinearPCM;
    inputStreamFormat.mFormatFlags = kAudioFormatFlagsNativeFloatPacked;
    inputStreamFormat.mBytesPerPacket = hv_getNumInputChannels(hv) * sizeof(Float32);
    inputStreamFormat.mFramesPerPacket = 1;
    inputStreamFormat.mBytesPerFrame = hv_getNumInputChannels(hv) * sizeof(Float32);
    inputStreamFormat.mChannelsPerFrame = hv_getNumInputChannels(hv);
    inputStreamFormat.mBitsPerChannel = sizeof(Float32) * 8;

    // Set the output format to the same as above
    AudioStreamBasicDescription outputStreamFormat;
    outputStreamFormat.mSampleRate = kSampleRate;
    outputStreamFormat.mFormatID = kAudioFormatLinearPCM;
    outputStreamFormat.mFormatFlags = kAudioFormatFlagsNativeFloatPacked;
    outputStreamFormat.mBytesPerPacket = hv_getNumOutputChannels(hv) * sizeof(Float32);
    outputStreamFormat.mFramesPerPacket = 1;
    outputStreamFormat.mBytesPerFrame = hv_getNumOutputChannels(hv) * sizeof(Float32);
    outputStreamFormat.mChannelsPerFrame = hv_getNumOutputChannels(hv);
    outputStreamFormat.mBitsPerChannel = sizeof(Float32) * 8;

    if (hv_getNumInputChannels(hv) > 0) {
      // set the input stream format
      status = AudioUnitSetProperty(audioUnit, kAudioUnitProperty_StreamFormat,
          kAudioUnitScope_Output, 1, &inputStreamFormat, sizeof(AudioStreamBasicDescription));

      // Add a render callback to get input from the microphone
      AURenderCallbackStruct renderCallbackStructInput;
      renderCallbackStructInput.inputProc = inputCallback;
      renderCallbackStructInput.inputProcRefCon = (__bridge void *) self;
      status = AudioUnitSetProperty(audioUnit, kAudioOutputUnitProperty_SetInputCallback,
          kAudioUnitScope_Global, 0, &renderCallbackStructInput, sizeof(renderCallbackStructInput));
    }

    if (hv_getNumOutputChannels(hv) > 0) {
      // set the output stream format
      status = AudioUnitSetProperty(audioUnit, kAudioUnitProperty_StreamFormat,
          kAudioUnitScope_Input, 0, &outputStreamFormat, sizeof(AudioStreamBasicDescription));

      // Add a render callback to send the output to the speaker
      AURenderCallbackStruct renderCallbackStructOutput;
      renderCallbackStructOutput.inputProc = renderCallback;
      renderCallbackStructOutput.inputProcRefCon = (__bridge void *) self;
      status = AudioUnitSetProperty(audioUnit, kAudioUnitProperty_SetRenderCallback,
          kAudioUnitScope_Global, 0, &renderCallbackStructOutput, sizeof(renderCallbackStructOutput));
    }

    // no need to allocate an additional AU buffer (slight increase in efficiency)
    status = AudioUnitSetProperty(audioUnit, kAudioUnitProperty_ShouldAllocateBuffer,
        kAudioUnitScope_Output, 1, &unsetProperty, sizeof(unsetProperty));

    status = AudioUnitInitialize(audioUnit);
}

OSStatus inputCallback(void *inRefCon,
                        AudioUnitRenderActionFlags *ioActionFlags,
                        const AudioTimeStamp *inTimeStamp,
                        UInt32 inBusNumber,
                        UInt32 inNumberFrames,
                        AudioBufferList *ioData) {

  HeavyAudio *const heavyAudio = (__bridge HeavyAudio *) inRefCon;

  // get a buffer to render the input audio into
  const int32_t required = hv_getNumInputChannels(heavyAudio->hv) * inNumberFrames * sizeof(Float32);
  int32_t available = 0;
  Float32 *const inputBuffers = (Float32 *) TPCircularBufferHead(&heavyAudio->inputQueue, &available);
  if (available < required) {
    NSLog(@"inputCallback: available %i < required %i", available, required);
    return noErr;
  }

  // prepare a buffer to render the microphone data into
  AudioBuffer ab;
  ab.mNumberChannels = hv_getNumInputChannels(heavyAudio->hv);
  ab.mDataByteSize = hv_getNumInputChannels(heavyAudio->hv) * inNumberFrames * sizeof(Float32);
  ab.mData = inputBuffers;

  AudioBufferList list;
  list.mNumberBuffers = 1;
  list.mBuffers[0] = ab;

  // render the microphone data into the buffer
  AudioUnitRender(heavyAudio->audioUnit, ioActionFlags, inTimeStamp, 1, inNumberFrames, &list);

  TPCircularBufferProduce(&heavyAudio->inputQueue, required);

  return noErr;
}

OSStatus renderCallback(void *inRefCon,
                        AudioUnitRenderActionFlags *ioActionFlags,
                        const AudioTimeStamp *inTimeStamp,
                        UInt32 inBusNumber,
                        UInt32 inNumberFrames,
                        AudioBufferList *ioData) {

  // counters for average CPU usage
  static double frameCount = 0.0;
  static double tickCount = 0.0;

  const double tick_rc = CFAbsoluteTimeGetCurrent();

  HeavyAudio *const heavyAudio = (__bridge HeavyAudio *) inRefCon;

  // consume the input in the circular buffer and render the output
  int32_t available = 0;
  Float32 *inputBuffers = TPCircularBufferTail(&heavyAudio->inputQueue, &available);
  const int32_t required = hv_getNumInputChannels(heavyAudio->hv) * inNumberFrames * sizeof(Float32);
  if (available < required) {
    NSLog(@"renderCallback: available %i < required %i", available, required);
    return noErr;
  }

  double tock = 0.0;
  switch (hv_getNumOutputChannels(heavyAudio->hv)) {
    case 1: {
      const double tick = CFAbsoluteTimeGetCurrent();
      hv_process(heavyAudio->hv, &inputBuffers, (Float32 **) &(ioData->mBuffers[0].mData), inNumberFrames);
      tock = CFAbsoluteTimeGetCurrent() - tick;
      break;
    }
    case 2: {
      Float32 *outputBuffers[2] = {
        (Float32 *) alloca(inNumberFrames * sizeof(Float32)),
        (Float32 *) alloca(inNumberFrames * sizeof(Float32))
      };

      // process Heavy
      const double tick = CFAbsoluteTimeGetCurrent();
      hv_process(heavyAudio->hv, &inputBuffers, outputBuffers, inNumberFrames);
      tock = CFAbsoluteTimeGetCurrent() - tick;

      vDSP_ztoc((DSPSplitComplex *) outputBuffers, 1, (DSPComplex *) ioData->mBuffers[0].mData, 2, inNumberFrames);
      break;
    }
    default: break;
  }

  TPCircularBufferConsume(&heavyAudio->inputQueue, required);

  tickCount += tock;
  frameCount += (double) inNumberFrames;

  const double tock_rc = CFAbsoluteTimeGetCurrent() - tick_rc;
  NSLog(@"%iµs (%iµs) @ %i/%gHz (%0.3f%% CPU) [%0.3f%% avgCPU]",
      (int) (1000000.0 * tock), // execution time of heavy callback
      (int) (1000000.0 * tock_rc), // execution time of entire render callback
      (int) inNumberFrames,
      hv_getSampleRate(heavyAudio->hv),
      100.0*(tock/(inNumberFrames/hv_getSampleRate(heavyAudio->hv))),
      100.0*(tickCount/(frameCount/hv_getSampleRate(heavyAudio->hv))));

  return noErr;
}

- (void)play {
  AudioOutputUnitStart(audioUnit);
}

- (void)pause {
  AudioOutputUnitStop(audioUnit);
}

- (void)overrideOutputToSpeaker:(BOOL)shouldOverride {
  NSError *error = nil;
  AVAudioSessionPortOverride portOverride = shouldOverride ? AVAudioSessionPortOverrideSpeaker : AVAudioSessionPortOverrideNone;
  [[AVAudioSession sharedInstance] overrideOutputAudioPort:portOverride error:&error];
  if (error != nil) {
    NSLog(@"Error while overriding the AudioSession route: %@", error.localizedDescription);
  }
}

@end
