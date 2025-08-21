from inspect import signature
from typing import List, Mapping, Optional, Sequence
from mods_base import EInputEvent
from mods_base.keybinds import KeybindCallback_NoArgs, KeybindCallback_Event, KeybindType
from mods_base.options import KeybindOption

class ControllerBind():
    """
    If buttonHeld is None, then the first item in buttonCombo is used as a normal bind
    If buttonHeld is not None, then buttonCombo is used as a combo macro
    """
    def __init__(self, keybind:KeybindType):
        self.keybind = keybind
        self.callback = keybind.callback
        self.buttonHeld: str | None = None
        self.buttonCombo: List[str] = []
    
    def IsSet(self) -> bool:
        return len(self.buttonCombo) > 0
    
    def GetCallback(self) -> KeybindCallback_Event | KeybindCallback_NoArgs | None:
        if not self.callback:
            return
        return self.keybind.callback
    
    def Fire(self, event: Optional[EInputEvent] = None):
        """Checks the keybind event and fires the relevant callback event with proper args.
        For the event type, we need to force it to the relevant event, not what the controller mod gives"""
        if not self.callback:
            print(f"No callback for keybind {self.keybind.identifier}")
            return
        try:
            if len(signature(self.callback).parameters) == 0:
                self.callback() # type: ignore
            else:
                if event:
                    self.callback(event) # type: ignore
                elif self.keybind.event_filter:
                    self.callback(self.keybind.event_filter) # type: ignore
                else:
                    self.callback(EInputEvent.IE_Released) # type: ignore
        except Exception:
            pass    # If a bind throws an error then we don't want it to affect other binds in the combo
    
    def ToKeybindOption(self) -> KeybindOption:
        bind = self.keybind
        opt =  KeybindOption(
            identifier=bind.identifier,
            value=str(self),
            is_rebindable=bind.is_rebindable,
            display_name=bind.display_name,
            description=bind.description,
            description_title=bind.description_title,
            is_hidden=bind.is_hidden,
            on_change=self.OnBindChanged,
        )
        opt.default_value = "None"  # For handle_reset_keybinds
        return opt
        
    def OnBindChanged(self, option, newValue):
        """Options menu option was changed (from handle_reset_keybinds)"""
        self.from_string(newValue)

    def __str__(self) -> str:
        return ControllerBind.bind_string(self.buttonHeld, self.buttonCombo)
    
    @staticmethod
    def button_string(key: str | None) -> str:
        """Returns a nice string for the button name."""
        if not key:
            return "None"
        if "_" in key:
            return key.split('_')[-1]
        else:
            return key.removeprefix("JOY ")
        
    @staticmethod
    def bind_string(buttonHeld: str | None, buttonCombo: List[str]) -> str:
        """Returns a nice string for the controller bind."""
        if not buttonHeld:
            if len(buttonCombo) == 1:
                return ControllerBind.button_string(buttonCombo[0])
            else:
                return "None"
        return f"{ControllerBind.button_string(buttonHeld)} + [{','.join(ControllerBind.button_string(b) for b in buttonCombo)}]"

    
    
    @staticmethod
    def to_string(buttonHeld, buttonCombo) -> str:
        """
        String used for encoding the bind
        Yes I'm doing this to pass through the KeybindOption. No I'm not sorry.
        """
        return f"{buttonHeld} + [{','.join(b for b in buttonCombo)}]"
      
    def from_string(self, input:str) -> None:
        print(f"from_string {input}")
        self.buttonHeld = None
        self.buttonCombo = []
        
        if '+' in input:
            parts = input.split(' + ')
            combo = parts[1].strip('[]')
            if combo:
                self.buttonHeld = parts[0]
                self.buttonCombo = combo.split(',')
        
        if not self.buttonHeld or self.buttonHeld == "None":
            self.buttonHeld = None

    
    def _to_json(self):
        """
        Turns this option into a JSON value.

        Returns:
            This option's JSON representation, or Ellipsis if it should be considered to have no
            value.
        """
        if not self.buttonHeld and not self.buttonCombo:
            return ...

        return {
            self.keybind.identifier: {
                "buttonHeld": self.buttonHeld,
                "buttonCombo": self.buttonCombo
            }
        }
        
    def _from_json(self, value) -> None:
        """
        Assigns this option's value, based on a previously retrieved JSON value.

        Args:
            value: The JSON value to assign.
        """
        if value is None:
            raise TypeError("ControllerBindOption is None!")
        
        self.buttonHeld = value["buttonHeld"]
        self.buttonCombo = value["buttonCombo"]
