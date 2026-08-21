# Invisible Keyboard

An iOS custom keyboard extension whose standard QWERTY hit targets remain active while every visual key surface is transparent.

## Behavior

- Starts in invisible mode.
- Uses standard QWERTY rows plus numbers/symbols.
- Gives light haptic feedback for every accepted key.
- Two-finger long press anywhere for 1.2 seconds toggles visible calibration mode.
- Bottom-left hit target switches back to the next installed keyboard.
- Requests no Full Access permission.

## Build

1. Install Xcode and XcodeGen on macOS.
2. In this folder, run `xcodegen generate`.
3. Open `InvisibleKeyboard.xcodeproj`.
4. Select a signing team for both targets and replace the bundle identifiers if needed.
5. Build and run the containing app on the iPhone.
6. On iPhone: Settings → General → Keyboard → Keyboards → Add New Keyboard → Invisible Keyboard.

## Current boundary

Apple does not expose native Dictation to third-party keyboard extensions. Use ChatGPT's own voice control for dictation and this keyboard for remembered touch positions.

The project has not been device-built in this Linux workspace because UIKit and Apple code signing require Xcode/macOS. Ren or another macOS build runner can compile and sign the included source without redesigning the keyboard.
