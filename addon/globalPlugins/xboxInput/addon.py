import logging

import threading
import time

import addonHandler
import globalPluginHandler

import inputCore
import ui
from .  import xinput

class XboxControllerInputGesture(inputCore.InputGesture):

    def __init__(self, state):
        super(XboxControllerInputGesture, self).__init__()
        self.state = state  

    def _get_identifiers(self):
        pressed = self.getPressed()
        if pressed:
            res = 'xb:' + '+'.join(pressed)
            return [res]
        raise RuntimeError("No button pressed")

    def getPressed(self):
        result = []
        if self.state.bLeftTrigger:
            result.append('left_trigger')
        if self.state.bRightTrigger:
            result.append('right_trigger')
        for field in self.state.wButtons._fields_:
                if getattr(self.state.wButtons, field[0]):
                    result.append(field[0].lower())
        return result

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    """Reads input from an Xbox controller and translates it to NVDA gestures"""

    packetNumber: int = 0
    running: bool = False   
    prev_pressed: set = set()

    def __init__(self) -> None:
        super().__init__()
        self.xinput = xinput.XInput()
        self.running = True
        self.thread = threading.Thread(target=self.inputLoop)
        self.thread.daemon = True
        self.thread.start()

    def dispatch            (self, gamepadState) -> None:
        gesture = XboxControllerInputGesture(gamepadState)
        pressed = set(gesture.getPressed())
        if not pressed:
            return
        try:
            inputCore.manager.executeGesture(gesture)
        except inputCore.NoInputGestureAction:
            pass
            self.prev_pressed = pressed

    def inputLoop(self):
            while self.running:
                packetNumber, state = self.xinput.GetState(0)
                if (packetNumber != self.packetNumber):
                    self.dispatch(state)
                    self.packetNumber =     packetNumber
                time.sleep(0.016)

    def terminate(self):
        self.running = False
