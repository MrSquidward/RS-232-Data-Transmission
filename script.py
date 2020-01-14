import window as win

window = win.Window()

Front = win.FrontWindow(window.root, window.port)

Front.addPortCombobox()
Front.addPortSpinbox()
Front.addCommandInputField()
Front.addCheckbutton()

Front.addStatusLabel()
Front.addPortNameLabel()
Front.addPortTimeoutLabel()
Front.addPortStatusLabel()
Front.addCommandLabel()

Front.addOpenClosePortButton()
Front.addOptionsButton()
Front.addReadFromPortButton()
Front.addWriteToPortButton()
Front.addSaveButton()
Front.addExitButton()

window.root.mainloop()
