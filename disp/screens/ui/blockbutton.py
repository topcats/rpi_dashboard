# rpi_dashboard
# =================
# LCARS Button Classes
# - LcarsButton: Base class for rectangular buttons
# - LcarsBlockLarge: Large left navigation block
# - LcarsBlockMedium: Medium left navigation block
# - LcarsBlockSmall: Small left navigation block
# - LcarsImageButton: Rounded button with image

import tkinter as tk
from disp.screens.ui import colours


class LcarsButton():
    """Button - rectangular"""

    __root = None
    buttontItem = None

    def __init__(self, canvasroot, colour, pos, rectSize, text, handler=None):
        """
        Initialize LCARS Button
        
        :param canvasroot: Root Canvas
        :type canvasroot: tkinter.Tk
        :param colour: Button Colour
        :type colour: string
        :param pos: Button Position (x, y)
        :type pos: tuple
        :param rectSize: Button Size (width, height)
        :type rectSize: tuple
        :param text: Button Text
        :type text: string
        :param handler: Button Click Handler
        :type handler: function
        """
        
        # Capture the parameters
        self.__root = canvasroot
        self.colour = colour
        self.pos = pos
        self.size = rectSize
        self.text = text
        self.handler = handler

        # Create the button
        self.buttontItem = tk.Button(
                                self.__root,
                                text=self.text,
                                font=("Tungsten Bold", 20),
                                background=self.colour,
                                fg=colours.BLACK,
                                anchor=tk.SE,
                                relief="flat",
                                cursor="trek",
                                pady=0,
                                padx=2,
                                highlightthickness=0,
                                highlightbackground=self.colour,
                                highlightcolor=colours.BLACK,
                                activebackground=self.colour,
                                activeforeground=colours.BLACK,
                                borderwidth=0,
                                command=self.handler
                            )
        self.buttontItem.place(x=self.pos[0], y=self.pos[1], width=self.size[0], height=self.size[1])

    def setText(self, newText):
        self.__root.itemconfig(self.buttontItem, text=newText)



class LcarsBlockLarge(LcarsButton):
    """Left navigation block - large version"""

    def __init__(self, canvasroot, colour, pos, text, handler=None, width=98):
        """
        Initialize LCARS Block Large Button
        
        :param canvasroot: Root Canvas
        :type canvasroot: tkinter.Tk
        :param colour: Button Colour
        :type colour: string
        :param pos: Button Position (x, y) 
        :type pos: tuple
        :param text: Button Text
        :type text: string
        :param handler: Button Click Handler
        :type handler: function
        :param width: Button Width (default 98)
        :type width: int
        """
        size = (width, 147)
        LcarsButton.__init__(self, canvasroot, colour, pos, size, text, handler)



class LcarsBlockMedium(LcarsButton):
    """Left navigation block - medium version"""

    def __init__(self, canvasroot, colour, pos, text, handler=None, width=98):
        """
        Initialize LCARS Block Medium Button
                
        :param canvasroot: Root Canvas
        :type canvasroot: tkinter.Tk
        :param colour: Button Colour
        :type colour: string
        :param pos: Button Position (x, y) 
        :type pos: tuple
        :param text: Button Text
        :type text: string
        :param handler: Button Click Handler
        :type handler: function
        :param width: Button Width (default 98)
        :type width: int
        """
        size=(width, 62)
        LcarsButton.__init__(self, canvasroot, colour, pos, size, text, handler)



class LcarsBlockSmall(LcarsButton):
    """Left navigation block - small version"""

    def __init__(self, canvasroot, colour, pos, text, handler=None, width=98):
        """
        Initialize LCARS Block Small Button
                
        :param canvasroot: Root Canvas
        :type canvasroot: tkinter.Tk
        :param colour: Button Colour
        :type colour: string
        :param pos: Button Position (x, y) 
        :type pos: tuple
        :param text: Button Text
        :type text: string
        :param handler: Button Click Handler
        :type handler: function
        :param width: Button Width (default 98)
        :type width: int
        """
        size=(width, 34)
        LcarsButton.__init__(self, canvasroot, colour, pos, size, text, handler)



class LcarsImageButton():
    """Button - rounded"""

    __root = None
    buttontItem = None

    def __init__(self, canvasroot, colour, pos, handler=None):
        """
        Initialize LCARS Button
        
        :param canvasroot: Root Canvas
        :type canvasroot: tkinter.Tk
        :param colour: Button Colour
        :type colour: string
        :param pos: Button Position (x, y)
        :type pos: tuple
        :param handler: Button Click Handler
        :type handler: function
        """
        
        # Capture the parameters
        self.__root = canvasroot
        self.colour = colour
        self.pos = pos
        self.handler = handler

        # Create Image
        self.__image = tk.PhotoImage(file=self.__getFile())
        self.__root.image = self.__image

        # Create the button
        self.buttontItem = tk.Button(
                                self.__root,
                                image=self.__image,
                                background=colours.BLACK,
                                fg=colours.BLACK,
                                anchor=tk.CENTER,
                                relief="flat",
                                cursor="trek",
                                pady=0,
                                padx=2,
                                highlightthickness=0,
                                borderwidth=0,
                                highlightbackground=colours.BLACK,
                                activebackground=colours.BLACK,
                                activeforeground=colours.WHITE,
                                command=self.handler
                            )
        self.buttontItem.place(x=self.pos[0], y=self.pos[1], width=124, height=46)


    def __getFile(self):
        """
        Get Button Image from colour
        
        :return: Full path to image
        :rtype: string
        """
        if self.colour == colours.RED:
            return "disp/screens/assets/button-red.png"
        elif self.colour == colours.GREEN:
            return "disp/screens/assets/button-green.png"
        elif self.colour == colours.CORAL:
            return "disp/screens/assets/button-coral.png"
        else:
            return "disp/screens/assets/button.png"
        

    def setColour(self, newColour):
        self.colour = newColour
        self.__image = tk.PhotoImage(file=self.__getFile())
        self.__root.image = self.__image
        self.root.itemconfig(self.buttontItem, image=self.__image)
