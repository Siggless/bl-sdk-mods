from typing import Any, Dict, List, Tuple
from mods_base import get_pc, hook, EInputEvent
from mods_base.hook import add_hook, remove_hook
from unrealsdk.hooks import Type, Block
from unrealsdk.logging import misc
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

from .controller_bind import ControllerBind
from .game_commands import _controller_commands

controllerBindsByMod: Dict[str, List[ControllerBind]] = {}

"""
These states handle the processing of combo binds, and blocking relevant input actions.
I hook into WillowUIInteraction.InputKey just like the KeybindManager, but check for controller keys.
Note there is an issue, where if a mod bind opens a GFxMovie (e.g. DialogOption), this breaks the
 sequence and still fires the normal behavior, and prevents the next action from that key.
 I've bodged a fix for this by just resetting the inputs when the GFxMovie is closed.
"""

class InputState():
    def Enter(self, heldKey:str | None):
        pass
    def Exit(self):
        pass
    def ReceiveInput(self, key: str, event: EInputEvent) -> Tuple[bool, type[Any] | None, str | None]:
        """
        Returns:
            bool: Whether to block the input
            InputState | None: The new state to change to   
            str | None: The consumed key to pass to the new InputState 
        """
        raise NotImplementedError
    def GFxMovieOpened(self, movieDef = None) -> Tuple[ type[Any] | None, str | None]:
        """
        Returns:
            InputState | None: The new state to change to   
            str | None: The consumed key to pass to the new InputState 
        """
        return (None, None)
    def GFxMovieClosed(self, movieDef = None) -> Tuple[type[Any] | None, str | None]:
        """
        Returns:
            InputState | None: The new state to change to   
            str | None: The consumed key to pass to the new InputState 
        """
        return (None, None)
    def BlockBehavior(self, command_key:str) -> type[Block] | None:
        """
        Returns:
            Block | None: Whether to Block the behavior function
        """
        return None
    

class Idle(InputState):
    def Enter(self, heldKey:str | None):
        # Upon returning to this state from Held, we still need to Block the consumed heldKey
        # This is a bit bodgey - Held state could only change back to this state after blocking that key in BlockBehavior
        self.blockKey = heldKey
    
    
    def ReceiveInput(self, key: str, event: EInputEvent) -> Tuple[bool, type[InputState] | None, str | None]:
        # If a controller bind is a single key then that can still be the relevant input event
        # if event is not EInputEvent.IE_Pressed:
        #     return (False, None, None)
        misc(f"Idle pressed {key}")
        for binds in controllerBindsByMod.values():
            for bind in binds:
                if not bind.IsSet():
                    continue
                if bind.buttonHeld == key:
                    if bind.buttonCombo and event is EInputEvent.IE_Pressed:
                        return (True, Held, key)
                elif not bind.buttonHeld and bind.buttonCombo[0] == key:
                        bind.Fire(event)
                        return (True, Idle, key)
                        
        return (False, None, None)

    
    def BlockBehavior(self, command_key: str) -> type[Block] | None:
        if not self.blockKey or self.blockKey not in _controller_commands:
            return
        if command_key in _controller_commands[self.blockKey]:
            # This should be the command that consumed modifier key would trigger upon release
            misc(f"Blocked {self.blockKey} via Idle")
            self.blockKey = None
            return Block
    

class Held(InputState):
    def Enter(self, heldKey:str | None):
        if not heldKey:
            raise ValueError("Entered Held InputState without a Held key!!!")
        self.heldButton = heldKey
        self.heldButtonConsumed = False
        self.lastComboButton: str | None = None
        self.gfxMovie = None
        self.validBindsByMod: Dict[str, Dict[ControllerBind, List[str]]] = {}
        # Make a list of all mod keybinds with that held button here
        for modName, modBinds in controllerBindsByMod.items():
            validBinds = [k for k in modBinds if k.buttonHeld == self.heldButton]
            if not validBinds:
                continue
            # Add this mod's valid binds to the dict, with a mod identifier
            thisModBinds = self.validBindsByMod[modName] = {}
            for bind in validBinds:
                thisModBinds[bind] = [*bind.buttonCombo]
            # Then each time we recieve a new input, pop any non-matching keybind from that list
        misc(self.validBindsByMod)
    
    
    def ReceiveInput(self, key: str, event: EInputEvent) -> Tuple[bool, type[InputState] | None, str | None]:
        if key == self.heldButton and event == EInputEvent.IE_Released:
            misc(f"Released held key {key}")
            return (True, Idle, self.heldButton if self.heldButtonConsumed else None)
        
        misc(f"Held with {key} {event}")
        if event == EInputEvent.IE_Repeat:
            return (True, None, None)
        ALWAYS_BLOCK_HELD_KEY_EVEN_IF_NOT_CONSUMED = True
        if ALWAYS_BLOCK_HELD_KEY_EVEN_IF_NOT_CONSUMED:
            self.heldButtonConsumed = True
        
        self.lastComboButton = key
        if event != EInputEvent.IE_Pressed:
            return (True, None, None)
        
        invalidModNames:List[str] = []  # Since we can't pop from the dict whilst iterating over it
        firedBindsByModName = {}
        for modName, modBinds in self.validBindsByMod.items():
            invalidBinds = []
            firedBinds = []
            for bind, combo in modBinds.items():
                if not combo or combo[0] != key:
                    # This bind is no longer valid for the input combo
                    misc(f"invalid bind {bind.buttonCombo}")
                    invalidBinds.append(bind)
                    continue
                misc(f"Still valid bind {bind.buttonHeld} + {combo}")
                combo.pop(0)
                if not combo:
                    # This bind combo has been completed! Fire it
                    self.heldButtonConsumed = True
                    misc("Firing this bind!")
                    MULTIPLE_BIND_OPTION = True
                    if MULTIPLE_BIND_OPTION:
                        if modName not in firedBindsByModName:
                            firedBindsByModName[modName] = []
                        firedBindsByModName[modName].append(bind)
                    firedBinds.append(bind)
                    bind.Fire()
            
            for bind in invalidBinds:
                modBinds.pop(bind)
                if len(modBinds) == 0:
                    invalidModNames.append(modName)
                    
        for modName in invalidModNames:
            self.validBindsByMod.pop(modName)
        
        # if firedBindsByModName:
        #     return (True, Held, self.heldButton)
        for modName, firedBinds in firedBindsByModName.items():
            for bind in firedBinds:
                self.validBindsByMod[modName][bind] = [*bind.buttonCombo]
                misc(f"... and resetting this bind to {bind.buttonCombo}")
        
        return (True, None, None)
    
    
    def GFxMovieOpened(self, movieDef = None) -> Tuple[type[InputState] | None, str | None]:
        # If a mod bind opens a GFxMovie, then this breaks our sequence and futzes 
        # with the final button's input after being closed. I try to prevent that.
        self.gfxMovie = movieDef
        return (None, None)
    
    
    def GFxMovieClosed(self, movieDef = None) -> Tuple[type[InputState] | None, str | None]:
        if self.gfxMovie and self.gfxMovie is movieDef:
            print("Closed our movie!")
            get_pc().PlayerInput.ReleasePressedButtons()
            return (Idle, None)
        return (None, None)
    
    
    def BlockBehavior(self, command_key: str) -> type[Block] | None:
        if self.lastComboButton and command_key in _controller_commands[self.lastComboButton]:
            # This is a command that the modded controller key would trigger (there might be multiple that have to be skipped here)
            misc(f"Blocked {self.lastComboButton} via Held")
            return Block
        
        if command_key in _controller_commands[self.heldButton]:
            # This should be the command that the modifier key would trigger
            misc(f"Blocked {self.heldButton} via Held")
            return Block
    
    
currentState: InputState = Idle()
currentState.Enter(None)
def ChangeToState(newState: type[InputState], key: str | None):
    global currentState
    currentState.Exit()
    currentState = newState()
    currentState.Enter(key)
    misc(f"Changed to state {str(newState)}") 


@hook("WillowGame.WillowUIInteraction:InputKey", immediately_enable=True)
def ui_interaction_input_key(
    _1: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> type[Block] | None:
    if not args.bGamepad:
        return
    
    (block, newState, newStateKey) = currentState.ReceiveInput(args.Key, args.Event)
    if newState:
        ChangeToState(newState, newStateKey)
    if block:
        return Block


@hook("WillowGame.WillowGFxUIManager:PlayMovie", immediately_enable=True)
def gfx_movie_opened(
    _1: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> type[Block] | None:
    misc("PlayMovie")
    (newState, newStateKey) = currentState.GFxMovieOpened(args.MovieDefinition)
    if newState:
        ChangeToState(newState, newStateKey)


@hook("WillowGame.WillowGFxUIManager:Movie_OnClosed", Type.POST, immediately_enable=True)
def gfx_movie_closed(
    _1: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> None:
    misc("CloseMovie")
    (newState, newStateKey) = currentState.GFxMovieClosed(args.Movie.MyDefinition)
    if newState:
        ChangeToState(newState, newStateKey)
    

@hook("Engine.Behavior_ClientConsoleCommand:ApplyBehaviorToContext", immediately_enable=True)
def InputCommand(obj: UObject, args: WrappedStruct, _3: Any, _4: BoundFunction,) -> type[Block] | None:
    """
    This function fires whenever a Behavior_ClientConsoleCommand is called (from an InputAction)
    I use this to prevent input button actions from firing when a modded bind has been used for this button e.g. InputActionDefinition GD_Input.Actions.InputAction_Jump
    Note for some reason calling unrealsdk.Log here causes other mod hooks like PickupAsTrash's NextWeapon() to break.
    """
    return currentState.BlockBehavior(obj.Command)


def InputPlayerBehavior(obj: UObject, args: WrappedStruct, _3: Any, _4: BoundFunction,) -> type[Block] | None:
    """
    This function fires whenever a BehaviorBase class that is hooked from out dictionary is called (from an InputAction)
    I use this to prevent input button actions from firing when a modded bind has been used for this button e.g. InputActionDefinition GD_Input.Actions.InputAction_ThrowGrenade
    """
    print("blockBehavior")
    return currentState.BlockBehavior(obj.Name)


# Create the hooks for each of the special Behavior classes in the dictionary
for k in _controller_commands:
    for behaviourClass in _controller_commands[k].values():
        if behaviourClass != "Engine.Behavior_ClientConsoleCommand":
            add_hook(behaviourClass + ":ApplyBehaviorToContext", Type.PRE, "ControllerBinds." + behaviourClass, InputPlayerBehavior)
