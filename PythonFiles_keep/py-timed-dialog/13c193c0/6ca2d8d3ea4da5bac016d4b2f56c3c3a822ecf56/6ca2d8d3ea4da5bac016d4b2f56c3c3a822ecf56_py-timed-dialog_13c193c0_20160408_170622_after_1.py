'''
A simple python library that helps create dialog boxes that self destruct after a timeout period.
'''

# Support for Python 2 and Python 3
try:
    import tkinter
except:
    import Tkinter as tkinter

class TimedDialog:
    '''
    Core class that will be used to create self destructing dialog boxes.
    '''
    def __init__(self):
        pass

    def selected(self, value):
        '''
        Handler for button click.
        '''
        self.response = value
        self.top.destroy() # destroy the dialog box

    def button_input(self, title, message, buttons, default, timeout=None, dimensions=None):
        '''
        Function to accept input in the form of a button click.
        '''

        # Create the dialog box
        self.response = default
        self.top = tkinter.Tk()
        self.top.title(title)

        # Use dimensions if passes
        if dimensions is not None:
            self.top.minsize(width=dimensions[0], height=dimensions[1])
            self.top.maxsize(width=dimensions[0], height=dimensions[1])

        # Display a message
        labelString = tkinter.StringVar()
        labelString.set(message)
        label = tkinter.Label(self.top, textvariable=labelString, relief=tkinter.RAISED)
        label.pack(ipadx=100, ipady=10)

        # Populate dialog box with buttons
        for key in buttons.keys():
            button = tkinter.Button(self.top, text=buttons[key], command=lambda key=key: self.selected(key))
            button.pack(fill='both', pady=5, padx=10)

        # Destroy the dialog box if there has been no button click within the timeout period
        if timeout != None:
            try:
                self.top.after(timeout, lambda: self.top.destroy())
            except:
                pass

        self.top.mainloop()
        return self.response
