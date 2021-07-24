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

#import <Foundation/Foundation.h>
#include <AudioToolbox/AudioToolbox.h>
#include "tinywav.h"

struct HeavyContextInterface;

@class MainViewController;

@interface AudioEngine : NSObject {
  double _sampleRate;

  int _blockSize;
  int _numOutputChannels;

@public
  TinyWav tinywav;
  MainViewController *viewController;
  NSLock *lock;
}

@property (readonly) AudioUnit outputUnit;
@property (assign) double startingFrameCount;
@property (assign) int counter;
@property (nonatomic) struct HeavyContextInterface *context;
@property (atomic) bool keepRunning;

+ (void)update:(AudioEngine *)engine;

- (id)initWithView:(MainViewController *)viewController;
- (void)start;
- (void)stop;
- (void)destroy;
- (void)sendFloat:(float)value toReceiver:(NSString *)receiverName;
- (void)printStreamDescription:(const AudioStreamBasicDescription)asbd;
- (void)recordAudioToFile:(NSString *)filepath;
- (void)stopRecordingAudio;

@end
