Softimage-Speedometer
=====================

Ever wanted to find out how fast your vehicles are going? Then try this Speedometer plugin for Autodesk Softimage. -- You move the thing; it tells you how fast. Easy! :)


FEATURES:
---------
- It evaluates constantly as the label itself moves through space.
- Just about all units of speed you could possibly want:
xsi/s, m/s, ft/s, kmh, mph, knots and Mach number (so you know when your baby's gone supersonic!)
- It's a floaty label that always faces you. o_o
- In SI|2013+ it uses "annotation objects". In older versions, it uses ICE showvalues to fake it.
- Customizable scale factor. (By default assumes 10 xsi units = 1 metre.)
- You can declare a title in each speedometer, so when you have multiples you know which is which!


USAGE:
------
You can approach things a few ways:
* Have no selection to make the speedometer object alone.
* Select one or more objects to make multiple speedometers which will be pose-constrained to them. (If it's geo it will attempt to place it on top of the actual mesh.)
* For deformed meshes, you can tag some points or faces and it will do an Object-to-Cluster constraint instead of the usual Pose constraint.

After that, just look for the DisplayInfo_options property to enable what you need, and don't forget to clarify what 1 metre equals in XSI units in your production. By default it will assume 10 units = 1 metre, which is a scale a lot of folks go by, but you're free to change it.

By the way, it's highly recommended to enable on-screen DisplayInfo support by doing Ctrl+Shift+S and in the Stats tab, in the "Custom Info" section, enable the first and last options. (Now when you select a speedometer, you'll see the settings in your viewport on the side.)
