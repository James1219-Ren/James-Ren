import UIKit

final class KeyboardViewController: UIInputViewController {
    private enum LayoutMode {
        case letters
        case numbers
    }

    private let keyboardStack = UIStackView()
    private let feedback = UIImpactFeedbackGenerator(style: .light)
    private var buttons: [UIButton] = []
    private var invisible = true
    private var shifted = false
    private var layoutMode: LayoutMode = .letters

    override func viewDidLoad() {
        super.viewDidLoad()
        configureRootView()
        configureRecoveryGesture()
        rebuildKeyboard()
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        applyAppearance()
    }

    private func configureRootView() {
        view.backgroundColor = .clear
        view.isOpaque = false

        keyboardStack.axis = .vertical
        keyboardStack.spacing = 7
        keyboardStack.distribution = .fillEqually
        keyboardStack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(keyboardStack)

        NSLayoutConstraint.activate([
            keyboardStack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 5),
            keyboardStack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -5),
            keyboardStack.topAnchor.constraint(equalTo: view.topAnchor, constant: 8),
            keyboardStack.bottomAnchor.constraint(equalTo: view.bottomAnchor, constant: -8),
            view.heightAnchor.constraint(equalToConstant: 268)
        ])
    }

    private func configureRecoveryGesture() {
        let gesture = UILongPressGestureRecognizer(target: self, action: #selector(toggleVisibility(_:)))
        gesture.minimumPressDuration = 1.2
        gesture.numberOfTouchesRequired = 2
        gesture.cancelsTouchesInView = true
        view.addGestureRecognizer(gesture)
    }

    private func rebuildKeyboard() {
        keyboardStack.arrangedSubviews.forEach { row in
            keyboardStack.removeArrangedSubview(row)
            row.removeFromSuperview()
        }
        buttons.removeAll()

        switch layoutMode {
        case .letters:
            addEqualRow(["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"])
            addEqualRow(["a", "s", "d", "f", "g", "h", "j", "k", "l"], sideInset: 18)
            addEqualRow(["shift", "z", "x", "c", "v", "b", "n", "m", "delete"])
        case .numbers:
            addEqualRow(["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"])
            addEqualRow(["-", "/", ":", ";", "(", ")", "$", "&", "@", "\""])
            addEqualRow(["symbols", ".", ",", "?", "!", "'", "delete"])
        }

        addBottomRow()
        applyAppearance()
    }

    private func addEqualRow(_ keys: [String], sideInset: CGFloat = 0) {
        let row = UIStackView()
        row.axis = .horizontal
        row.spacing = 5
        row.distribution = .fillEqually

        row.isLayoutMarginsRelativeArrangement = sideInset > 0
        row.layoutMargins = UIEdgeInsets(top: 0, left: sideInset, bottom: 0, right: sideInset)
        keys.forEach { row.addArrangedSubview(makeButton(for: $0)) }

        keyboardStack.addArrangedSubview(row)
    }

    private func addBottomRow() {
        let row = UIStackView()
        row.axis = .horizontal
        row.spacing = 6
        row.distribution = .fill

        let next = makeButton(for: "next")
        let mode = makeButton(for: "mode")
        let space = makeButton(for: "space")
        let enter = makeButton(for: "return")

        next.widthAnchor.constraint(equalToConstant: 50).isActive = true
        mode.widthAnchor.constraint(equalToConstant: 58).isActive = true
        enter.widthAnchor.constraint(equalToConstant: 78).isActive = true

        row.addArrangedSubview(next)
        row.addArrangedSubview(mode)
        row.addArrangedSubview(space)
        row.addArrangedSubview(enter)
        keyboardStack.addArrangedSubview(row)
    }

    private func makeButton(for key: String) -> UIButton {
        let button = UIButton(type: .custom)
        button.accessibilityLabel = accessibilityName(for: key)
        button.setTitle(displayName(for: key), for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 20)
        button.layer.cornerRadius = 6
        button.clipsToBounds = true
        button.addAction(UIAction { [weak self] _ in
            self?.handle(key)
        }, for: .touchUpInside)
        buttons.append(button)
        return button
    }

    private func handle(_ key: String) {
        feedback.impactOccurred()

        switch key {
        case "delete":
            textDocumentProxy.deleteBackward()
        case "space":
            textDocumentProxy.insertText(" ")
        case "return":
            textDocumentProxy.insertText("\n")
        case "shift":
            shifted.toggle()
            refreshTitles()
        case "mode", "symbols":
            layoutMode = layoutMode == .letters ? .numbers : .letters
            shifted = false
            rebuildKeyboard()
        case "next":
            advanceToNextInputMode()
        default:
            let output = shifted ? key.uppercased() : key
            textDocumentProxy.insertText(output)
            if shifted {
                shifted = false
                refreshTitles()
            }
        }
    }

    private func refreshTitles() {
        guard layoutMode == .letters else { return }
        buttons.forEach { button in
            guard let label = button.accessibilityLabel,
                  label.count == 1 else { return }
            button.setTitle(shifted ? label.uppercased() : label.lowercased(), for: .normal)
        }
        applyAppearance()
    }

    private func applyAppearance() {
        view.backgroundColor = invisible ? .clear : UIColor.systemGray5
        buttons.forEach { button in
            button.alpha = 1.0
            button.backgroundColor = invisible ? .clear : UIColor.systemGray3
            button.setTitleColor(invisible ? .clear : .label, for: .normal)
            button.layer.borderWidth = invisible ? 0 : 0.5
            button.layer.borderColor = invisible ? UIColor.clear.cgColor : UIColor.separator.cgColor
        }
    }

    @objc private func toggleVisibility(_ gesture: UILongPressGestureRecognizer) {
        guard gesture.state == .began else { return }
        invisible.toggle()
        feedback.impactOccurred()
        applyAppearance()
        UIAccessibility.post(
            notification: .announcement,
            argument: invisible ? "Keyboard hidden" : "Keyboard visible"
        )
    }

    private func displayName(for key: String) -> String {
        switch key {
        case "shift": return "⇧"
        case "delete": return "⌫"
        case "space": return "space"
        case "return": return "return"
        case "next": return "🌐"
        case "mode": return "123"
        case "symbols": return "ABC"
        default: return key
        }
    }

    private func accessibilityName(for key: String) -> String {
        switch key {
        case "shift", "delete", "space", "return", "next", "mode", "symbols": return key
        default: return key.lowercased()
        }
    }
}
