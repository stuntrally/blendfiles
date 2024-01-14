SpaceSkyNebula_*.blend
License: CC-BY-SA 4.0
self created in blender by rubberduck, with help of some tutorials and assets listed here.


Blender Nebula tutorial by Samuel Krug VFX 
https://www.youtube.com/watch?v=v6pULIv8sZA

Simon Thommes Noise Pack (CC0)
https://simonthommes.gumroad.com/l/NOISE-P

Saturn model
Author: Akshat
License: CC-BY 4.0
https://sketchfab.com/3d-models/saturn-8fb67d3defd74aaa880df3a08317e641
used in SpaceSkyNebula_02

=======================================================================

how to use: (wip)

before opening file, make sure to use blender 4.0 or later

-----------------------------------------------------------------------

how the system works:

Complex skies are using 2 layers, one for the sky and one for additional planets as an example
this allows adjusting a planet's position without rerendering the rest of the sky.
For this switch to the scene you want to render.

In some cases it may happen that it renders only the star, but the sky is not rendered (for example after start),
or that renders the sky after changing to planets scene, and or changing the workspace.
To prevent that go into Comp/Render Workspace and make sure that the composite node in that scene is active / clicked.

It took me a while to setup the layer system, and understanding how I can control it. 
Meaning first it was a bit confusing to me at the beggining, I was experimenting with rendering at a low resolution multiple times over a shorter time, which lead me to understanding it much better.



-----------------------------------------------------------------------
render setup / settings

there are multiple ways to adjust render settings, quality and render time for preview and final renders
mostly used to speed up production time

1: the render resolution (output tab), for a preview I usually use 50%, sometimes even lower
   When rendering a sky with mulptiple scenes (for planets), make sure that this matches in both scenes, and if needed to rerender the other scene.

2: samples amount
   for the final render 150, max 250 if really needed
   for preview I often go lower

3: Step rate settings (under render > Volumes)
   lower values mean more volumetric detail but lower render times
	
   settings used for the final render of SpaceSkyNebula_02
   render: 0.25
   viewport: 0.5
   max steps 128
	
   for preview I go up to values of 1 or higher
   also see results in documentation_images dir (render_comarisation_steprate_time.jpg)

4: stars or the nebula can be deactivated for rendering to save some rendering time.
   While though not much, but it depends on the amount of stars visible,
   the main use is for development of the stars by hiding the nebula, 
   rendering only the stars, adjust amount, size, brightness, color or distribution of stars
   
   
-----------------------------------------------------------------------
the nebula sphere

todo

-----------------------------------------------------------------------
the star system

the amount and many other properties of stars can be changed inside the geometry modifier on the star system object
the basic settings can be found in the modifier panel (see example image with various used values)
But be careful modifying these values, setting the amount of stars too high may lead to blender hanging / not responding or crashing.

deeper and more advanced settings can be made inside the modifier's node tree and for colors, brightness etc the setting inside the star material (the object called "_Star")
Also the distribution of the stars inside are made that they match the noise used for the nebula sphere, though this is really advanced



