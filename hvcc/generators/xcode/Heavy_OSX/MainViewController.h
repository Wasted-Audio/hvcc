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

#import <Cocoa/Cocoa.h>

@class AudioEngine;

@interface MainViewController : NSViewController

@property (weak) IBOutlet NSButton *startAudioButton;
@property (weak) IBOutlet NSButton *recordAudioButton;
@property (weak) IBOutlet NSLevelIndicator *cpuIndicator;
@property (nonatomic, strong) AudioEngine *audioEngine;
@property (weak) IBOutlet NSTextField *paramOneValue;
@property (weak) IBOutlet NSTextField *paramTwoValue;
@property (weak) IBOutlet NSTextField *paramThreeValue;
@property (weak) IBOutlet NSTextField *paramFourValue;
@property (weak) IBOutlet NSSlider *paramOneSlider;
@property (weak) IBOutlet NSSlider *paramTwoSlider;
@property (weak) IBOutlet NSSlider *paramThreeSlider;
@property (weak) IBOutlet NSSlider *paramFourSlider;

- (void)destroy;
- (IBAction)onStartAudio:(id)sender;
- (IBAction)onRecordAudio:(id)sender;
- (IBAction)onSliderDidChange:(id)sender;

- (void)updateCpuWithDuration:(NSTimeInterval)i andFraction:(double)p;

@end
