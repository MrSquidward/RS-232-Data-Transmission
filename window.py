import serial
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import time


def parity2string(parity):
    if parity == 'N':
        return 'none'
    if parity == 'E':
        return 'even'
    if parity == 'O':
        return 'odd'
    if parity == 'M':
        return 'mark'
    if parity == 'S':
        return 'space'

    return ''

def string2parity(parity):
    if parity == 'none':
        return serial.PARITY_NONE
    if parity == 'even':
        return serial.PARITY_EVEN
    if parity == 'odd':
        return serial.PARITY_ODD
    if parity == 'mark':
        return serial.PARITY_MARK
    if parity == 'space':
        return serial.PARITY_SPACE

    return ''

def string2stopbits(stopbits):
    if stopbits == '1':
        return serial.STOPBITS_ONE
    if stopbits == '1.5':
        return serial.STOPBITS_ONE_POINT_FIVE
    if stopbits == '2':
        return serial.STOPBITS_TWO

    return 0

def getPortOptions(port):
    options = {
        'baudrate': str(port.baudrate),
        'bytesize': str(port.bytesize),
        'parity': parity2string(port.parity),
        'stopbits': str(port.stopbits)
    }
    print(options)
    return options

def setValueToCombobox(combobox, value):
    valuesList = combobox['values']
    combobox.current(valuesList.index(value))


class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('RS-232 Data transmission')

        self.port = serial.Serial()


class FrontWindow:
    def __init__(self, root, port):
        self.root = root
        self.port = port

        self.Frame = tk.Frame(self.root, height=600, width=700)
        self.Frame.pack(side=tk.RIGHT)

        self.textField = ScrolledText(self.Frame)
        self.textField.place(relx=0.05, rely=0.05, height=525, width=350)

        self.statusLabel = tk.Label(self.Frame)

        self.combobox = ttk.Combobox(self.Frame)
        self.spinbox = tk.Spinbox(self.Frame, from_=1.0, to=10.0, increment=0.5)
        self.commandInput = tk.Entry(self.Frame)
        self.ending = tk.IntVar()

        self.openClosePortButton = tk.Button(self.Frame)

    def addPortCombobox(self):
        self.combobox['font'] = ('Arial', 14)
        self.combobox['state'] = 'readonly'
        self.combobox['values'] = ('COM1', 'COM2', 'COM3', 'COM4',
                                   'COM5', 'COM6', 'COM7', 'COM8')
        self.combobox.current(2)
        self.combobox.place(relx=0.8, rely=0.05, width=100)

    def addPortSpinbox(self):
        defaultValue = tk.StringVar()
        defaultValue.set('5.0')

        self.spinbox['textvariable'] = defaultValue
        self.spinbox['font'] = ('Arial', 14)
        self.spinbox['state'] = 'readonly'

        self.spinbox.place(relx=0.8, rely=0.15, width=100)

    def addCommandInputField(self):
        self.commandInput['font'] = ('Arial', 14)
        self.commandInput.place(relx=0.55, rely=0.65, width=200)

    def addCheckbutton(self):
        checkbutton = tk.Checkbutton(self.Frame, text='Adjust CR+LF',
                                     font=('Arial', 13), variable=self.ending)

        checkbutton.place(relx=0.55, rely=0.7)

    # labels
    def addStatusLabel(self):
        self.statusLabel.destroy()

        if self.port.is_open:
            labelText = 'opened'
            color = 'green'
        else:
            labelText = 'closed'
            color = 'red'

        self.statusLabel = tk.Label(self.Frame, font=('Arial', 15), text=labelText, fg=color)
        self.statusLabel.place(relx=0.8, rely=0.36)

    def addPortNameLabel(self):
        portNameLabel = tk.Label(self.Frame, font=('Arial', 15), text='Port name: ')
        portNameLabel.place(relx=0.6, rely=0.05)

    def addPortTimeoutLabel(self):
        portTimeoutLabel = tk.Label(self.Frame, font=('Arial', 15), text='Port timeout: ')
        portTimeoutLabel.place(relx=0.58, rely=0.15)

    def addPortStatusLabel(self):
        portStatusLabel = tk.Label(self.Frame, font=('Arial', 15), text='Port status: ')
        portStatusLabel.place(relx=0.6, rely=0.36)

    def addCommandLabel(self):
        commandLabel = tk.Label(self.Frame, font=('Arial', 15), text='Insert command: ')
        commandLabel.place(relx=0.58, rely=0.59)

    # buttons callbacks
    def callbackOptionsBtn(self):
        self.port.port = str(self.combobox.get())
        OptionsWindow(self.root, self.port)

    def callbackOpenClosePortBtn(self):
        if not self.port.is_open:
            self.port.port = str(self.combobox.get())
            self.port.timeout = float(self.spinbox.get())

            try:
                self.port.open()
            except serial.serialutil.SerialException as e:
                print(e)
                errorMsg = 'Could not open port: ' + str(self.port.port)
                messagebox.showinfo('Error', errorMsg)
                return

            status = 'Close port'

        else:
            try:
                self.port.close()
            except serial.serialutil.SerialException as e:
                print(e)
                errorMsg = 'Could not close port: ' + str(self.port.port)
                messagebox.showinfo('Error', errorMsg)
                return

            status = 'Open port'

        self.openClosePortButton.config(text=status)
        self.addStatusLabel()

    def getInputFromPort(self):
        wasLastStringEmpty = True

        if self.port.is_open:
            timeout = float(self.spinbox.get())
            start = time.time()
            while True:
                inputFromPort = self.port.readline()

                if inputFromPort == b'':
                    if wasLastStringEmpty:
                        if time.time() - start >= timeout:
                            infoMsg = 'Timeout expired'
                            messagebox.showinfo('Message', infoMsg)
                            break
                        else:
                            continue
                    else:
                        break
                else:
                    wasLastStringEmpty = False

                self.textField.insert(tk.END, inputFromPort)
                self.textField.yview(tk.END)
                self.root.update()
        else:
            errorMsg = 'Port ' + str(self.combobox.get()) + ' is not open!'
            messagebox.showinfo('Error', errorMsg)

    def writeToPort(self):
        if self.port.is_open:
            command = self.commandInput.get()

            if self.ending.get():
                command += chr(13) + chr(10)

            self.port.write(command.encode('utf-8'))
            self.commandInput.delete(0, 'end')
        else:
            errorMsg = 'Port ' + str(self.combobox.get()) + ' is not open!'
            messagebox.showinfo('Error', errorMsg)

    def callbackSaveBtn(self):
        fileTypes = (('text files', '*.txt'), ('all files', '*.*'))
        filename = filedialog.asksaveasfilename(title='Select file', filetypes=fileTypes)

        try:
            txtFile = open(filename, 'w+')
        except FileNotFoundError as e:
            print(e)
            return

        txtFile.write(self.textField.get('1.0', tk.END))

        txtFile.close()

    # buttons definitions
    def addOptionsButton(self):
        optionsButton = tk.Button(self.Frame, text='More options', font=('Arial', 15),
                                       command=self.callbackOptionsBtn)

        optionsButton.place(relx=0.67, rely=0.23, width=150)

    def addOpenClosePortButton(self):
        self.openClosePortButton['text'] = 'Open Port'
        self.openClosePortButton['font'] = ('Arial', 15)
        self.openClosePortButton['command'] = self.callbackOpenClosePortBtn

        self.openClosePortButton.place(relx=0.67, rely=0.45, width=150)

    def addReadFromPortButton(self):
        readFromPortButton = tk.Button(self.Frame, text='Read', font=('Arial', 15),
                                        command=self.getInputFromPort)

        readFromPortButton.place(relx=0.7, rely=0.77, width=100)

    def addWriteToPortButton(self):
        writeToPortButton = tk.Button(self.Frame, text='Write', font=('Arial', 15),
                                        command=self.writeToPort)

        writeToPortButton.place(relx=0.85, rely=0.64, width=100)

    def addSaveButton(self):
        saveButton = tk.Button(self.Frame, font=('Arial', 15), text='Save',
                                command=self.callbackSaveBtn)

        saveButton.place(relx=0.6, rely=0.9, width=100)

    def addExitButton(self):
        exitButton = tk.Button(self.Frame, text='Exit', font=('Arial', 15),
                                 command=lambda: self.root.destroy())

        exitButton.place(relx=0.8, rely=0.9, width=100)


class OptionsWindow:
    def __init__(self, root, port):
        self.mainRoot = root
        self.port = port

        self.root = tk.Toplevel(self.mainRoot)
        self.root.title(str(self.port.name))

        self.Frame = tk.Frame(self.root, height=350, width=350)
        self.Frame.pack()

        self.baudrateWidget = ttk.Combobox(self.Frame, font=('Arial', 14), state='readonly')
        self.bytesizeWidget = ttk.Combobox(self.Frame, font=('Arial', 14), state='readonly')
        self.parityWidget = ttk.Combobox(self.Frame, font=('Arial', 14), state='readonly')
        self.stopbitsWidget = ttk.Combobox(self.Frame, font=('Arial', 14), state='readonly')

        self.addLabels()
        self.addInputsFields()
        self.addSaveOptionsButton()
        self.addDefaultOptionsButton()
        self.addExitButton()

    def addLabels(self):
        baudrateLabel = tk.Label(self.Frame, font=('Arial', 15), text=' Baudrate: ')
        bytesizeLabel = tk.Label(self.Frame, font=('Arial', 15), text='Byte size: ')
        parityLabel = tk.Label(self.Frame, font=('Arial', 15), text='     Parity: ')
        stopbitsLabel = tk.Label(self.Frame, font=('Arial', 15), text='Stop bits: ')

        baudrateLabel.place(relx=0.1, rely=0.1)
        bytesizeLabel.place(relx=0.1, rely=0.2)
        parityLabel.place(relx=0.1, rely=0.3)
        stopbitsLabel.place(relx=0.1, rely=0.4)

    def addInputsFields(self):
        options = getPortOptions(self.port)

        self.baudrateWidget['values'] = ('300', '600', '1200', '1800', '2400',
                                         '4800', '9600', '19200', '38400', '57600')
        self.bytesizeWidget['values'] = ('5', '6', '7', '8')
        self.parityWidget['values'] = ('none', 'even', 'odd', 'mark', 'space')
        self.stopbitsWidget['values'] = ('1', '1.5', '2')

        setValueToCombobox(self.baudrateWidget, options['baudrate'])
        setValueToCombobox(self.bytesizeWidget, options['bytesize'])
        setValueToCombobox(self.parityWidget, options['parity'])
        setValueToCombobox(self.stopbitsWidget, options['stopbits'])

        self.baudrateWidget.place(relx=0.5, rely=0.1, width=100)
        self.bytesizeWidget.place(relx=0.5, rely=0.2, width=100)
        self.parityWidget.place(relx=0.5, rely=0.3, width=100)
        self.stopbitsWidget.place(relx=0.5, rely=0.4, width=100)

    # callbacks
    def callbackSaveOptionsBtn(self):
        self.port.baudrate = int(self.baudrateWidget.get())
        self.port.bytesize = int(self.bytesizeWidget.get())
        self.port.parity = string2parity(self.parityWidget.get())
        self.port.stopbits = string2stopbits(self.stopbitsWidget.get())

    def callbackExitBtn(self):
        self.callbackSaveOptionsBtn()
        self.root.destroy()

    def callbackDefaultOptionsBtn(self):
        defaultOptions = {
            'baudrate': '9600',
            'bytesize': '8',
            'parity': 'none',
            'stopbits': '1'
        }

        setValueToCombobox(self.baudrateWidget, defaultOptions['baudrate'])
        setValueToCombobox(self.bytesizeWidget, defaultOptions['bytesize'])
        setValueToCombobox(self.parityWidget, defaultOptions['parity'])
        setValueToCombobox(self.stopbitsWidget, defaultOptions['stopbits'])

    # buttons definitions
    def addSaveOptionsButton(self):
        saveButton = tk.Button(self.Frame, font=('Arial', 15), text='Save',
                               command=self.callbackSaveOptionsBtn)

        saveButton.place(relx=0.1, rely=0.6, width=100)

    def addDefaultOptionsButton(self):
        defaultButton = tk.Button(self.Frame, font=('Arial', 15), text='Default',
                                  command=self.callbackDefaultOptionsBtn)

        defaultButton.place(relx=0.5, rely=0.6, width=100)

    def addExitButton(self):
        exitButton = tk.Button(self.Frame, font=('Arial', 15), text='Exit',
                               command=self.callbackExitBtn)

        exitButton.place(relx=0.65, rely=0.85, width=100)
