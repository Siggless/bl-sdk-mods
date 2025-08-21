####################################
## Fix the controller remapping menu
####################################
"""
This function is called every time an item is added to a menu list.
There is a Gearbox bug in BL2 (and I'm assuming AoDK) that assumed the Controller Presets list item is always index 7 in the list (hard-coded),
    when it was actually index 8. TPS has index 9 hard-coded too.
This caused the selected list item to change when entering Custom mapping mode.
We prevent the 7th item from being added and add it afterwards instead to fix that.
"""