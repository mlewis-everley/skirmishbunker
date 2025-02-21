## Main wip

## 2.0.1
* breaking stuff in the DetailedRoof
  * re-wrote how wall cuts care calculated
  * fixed positioning of wall details.
  * Code is still full of nonense and magic constants
* Cleaned up dependencies

## 2.0.0
### Contributed By Morven Lewis-Everley
* Updated flat roof to use hatches and tiles.
* Migrate Roof to Detailed roof, make it inherit from FlatRoof and refactor how tiles, hatches and magnet holes are generated.
* Introduce a helper class that assist in generation of a Series of shapes (as all series code seems to be 90% duplication with only a few changes).
* Added basic dependency injection for swapping out roof type on the fly.
* Added the ability to customise the hatches when generating the roof and the bunker together.
* Added an example of swapping out the roof.

### Cleanup
* Added Apache 2 license to top of source files.
* Restored cut hatch code.
* Restored tile generation code for detailed roof.
  * this was due to a regression bug.
  * temp hack for now
* Fix parameter order when making pip / magnet holes in the roof.
* Make Calc methods protected
* Brought back the render_hatches flag
* Added the render_hatch_cuts flag
* FlatRoof changed hole_diameter to hole_radius
* Added Bunker 5 example.
* Added Bunker 6 example.


## 1.2.0
* New parameter floor_thickness
  * Allows better granular control of the inner dimensions of the bunker.

## 1.1.4
* Updated The License
* Added window width as parameter which can override inset.

## 1.1.3
* Added Split Door
* Increased magnet height from 1.7 to 2.1
* Added catwalk generator.
* Fixed roof magnet cuts.
* Attempt to fix bunker floor placement.
* Updated dependencies
  * cadqueryhelper went to 0.1.1
  * cqterrain went to 0.1.5

## 1.1.2
* Jamie Broke the __init__.py at the root directory of cqterrain

## 1.1.1 Updated version dependencies, added better support for magnets
* Increased Pip Cuts height by .2 mm to try account for magnet sizing
  * Affected Bunker and roof code
* Updated medium bunker to use regular flooring
* Updated Cadquery version
* cadqueryhelper 0.0.8
* cqterrain 0.1.1

## 1.1.0 Customization
* Added support for custom window cuts
* Added support for custom windows
* Custom floor tiles
* Added ladder support
  * Custom Ladders
* Added hatch detailing and hatch cut
* Added floor cuts
* Fix Floor cut with tiles

## 1.0.0 Initial Release
* Date: 2022-12-14
* Initial release of the project
