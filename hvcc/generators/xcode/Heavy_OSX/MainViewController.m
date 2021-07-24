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

#import "MainViewController.h"
#import "AudioEngine.h"

@interface MainViewController ()

@end

@implementation MainViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
      self.audioEngine = [[AudioEngine alloc] initWithView:self];
    }
    return self;
}

- (void)loadView {
  [super loadView];
  [self.paramOneValue setStringValue:[self.paramOneSlider stringValue]];
  [self.paramTwoValue setStringValue:[self.paramTwoSlider stringValue]];
  [self.paramThreeValue setStringValue:[self.paramThreeSlider stringValue]];
  [self.paramFourValue setStringValue:[self.paramFourSlider stringValue]];
}

- (void)destroy {
	[self.audioEngine destroy];
}

- (IBAction)onStartAudio:(id)sender {
	if ([self.startAudioButton state] == 1) {
		[self.audioEngine start];
	} else {
		[self.audioEngine stop];
	}
}

- (IBAction)onRecordAudio:(id)sender {
  if ([self.recordAudioButton state] == 1) {
    [self.audioEngine recordAudioToFile:@"~/Desktop/Heavy_OSX.wav".stringByStandardizingPath];
  } else {
    [self.audioEngine stopRecordingAudio];
  }
}

- (IBAction)onSliderDidChange:(id)sender {
  float sliderValue = [sender floatValue];
  NSString *valueString = [NSString stringWithFormat:@"%.2f", sliderValue];

  if ([sender isEqualTo:self.paramOneSlider]) {
    [self.paramOneValue setStringValue:valueString];
    [self.audioEngine sendFloat:sliderValue toReceiver:@"Channel-A"];
  }
  else if ([sender isEqualTo:self.paramTwoSlider]) {
    [self.paramTwoValue setStringValue:valueString];
    [self.audioEngine sendFloat:sliderValue toReceiver:@"Channel-B"];
  }
  else if ([sender isEqualTo:self.paramThreeSlider]) {
    [self.paramThreeValue setStringValue:valueString];
    [self.audioEngine sendFloat:sliderValue toReceiver:@"Channel-C"];
  }
  else if ([sender isEqualTo:self.paramFourSlider]) {
    [self.paramFourValue setStringValue:valueString];
    [self.audioEngine sendFloat:sliderValue toReceiver:@"Channel-D"];
  }
}

- (void)updateCpuWithDuration:(NSTimeInterval)i andFraction:(double)p {
  [self.cpuIndicator setDoubleValue:10.0*log10(p) + 40.0];
}

@end
