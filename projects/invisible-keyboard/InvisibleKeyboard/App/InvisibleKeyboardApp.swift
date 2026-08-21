import SwiftUI

@main
struct InvisibleKeyboardApp: App {
    var body: some Scene {
        WindowGroup {
            SetupView()
        }
    }
}

private struct SetupView: View {
    var body: some View {
        NavigationStack {
            List {
                Section("Enable") {
                    Text("Settings → General → Keyboard → Keyboards → Add New Keyboard → Invisible Keyboard")
                    Text("Full Access is not required.")
                }

                Section("Use") {
                    Text("Switch keyboards with the globe key.")
                    Text("The layout starts invisible. Every key remains active and gives light haptic feedback.")
                    Text("Long-press anywhere with two fingers for 1.2 seconds to reveal or hide the layout.")
                }

                Section("Recovery") {
                    Text("The bottom-left invisible zone switches to the next keyboard.")
                    Text("Password fields may automatically return to Apple's keyboard.")
                }
            }
            .navigationTitle("Invisible Keyboard")
        }
    }
}
