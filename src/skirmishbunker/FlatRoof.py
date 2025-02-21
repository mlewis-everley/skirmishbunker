# Copyright 2023 Morven Lewis-Everley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cadquery as cq
from . import Base
from .Hatch import Hatch
from .SeriesHelper import SeriesHelper
from cadqueryhelper import series, grid
from math import floor as math_floor

class FlatRoof(Base):
    def __init__(self):
        super().__init__()

        # base parameters
        self.length = 160
        self.width = 150
        self.height = 25
        self.bunker_int_length=None
        self.bunker_int_width=None

        self.inset = 0
        self.wall_width = 0

        self.panel_length = 0
        self.panel_padding = 0

        # select all edges on the positive z face
        self.roof_chamfer_faces_selector = "+Z"
        self.roof_chamfer_edges_selector = ""
        self.roof_chamfer = 0
        self.roof_operation = "chamfer" # chamfer, fillet

        # roof tiles
        self.render_tiles = False
        self.tile_size = 21
        self.tile_padding = 2
        self.tile_height = 1.5
        # less then -1 results in a cut
        self.tile_z_offset = -1

        # Hatches
        self.render_hatches = False
        self.render_hatch_cuts = False
        self.hatch_panels = []
        self.hatch_length = 25
        self.hatch_width = 25
        self.hatch_radius = 10.5
        self.hatch_height = 6
        self.hatch_cut_inset = 2
        self.hatch_cut_chamfer = 2
        self.hatch_z_translate = 0

        # Pip/Magnet holes
        self.cut_holes = False
        self.hole_inset = 1.5
        self.hole_depth = 1
        #@todo discussion point - I would prefer if this radius.
        self.hole_radius = 1

        #shapes
        self.roof_body = None
        self.tiles = None
        self.hatches = None
        self.cut_hatches = None
        self.holes = None

    def __should_cut_tiles(self):
        if self.tile_z_offset < -1:
            return True

        return False

    def _calc_final_length(self):
        return self.length - (self.inset * 2)

    def _calc_final_width(self):
        return self.width - (self.inset * 2)

    def _calc_tile_space_length(self):
        length = self.length
        length -= 2 * self.inset
        length -= 2 * self.roof_chamfer
        return length

    def _calc_tile_space_width(self):
        width = self.width
        width -= 2 * self.inset
        width -= 2 * self.roof_chamfer
        return width

    def _calc_tile_spacing(self):
        return self.tile_size + self.tile_padding

    def _calc_tile_z_translate(self):
        cut_tiles = self.__should_cut_tiles()
        translate = (self.height / 2 + self.tile_height / 2)

        if cut_tiles == True:
            translate = self.height - translate
        else:
            translate = translate

        return translate

    def _calc_hatch_space_length(self):
        length = self.length
        length -= 2 * self.inset
        length -= 2 * self.roof_chamfer
        return length

    def _calc_hatch_space_width(self):
        width = self.width
        width -= 2 * self.inset
        width -= 2 * self.roof_chamfer
        return width

    def _calc_hatch_length_offset(self):
        return self.panel_length - self.hatch_length + self.panel_padding * 2

    def _calc_hatch_z_translate(self):
        return (self.height / 2 + self.hatch_height / 2)

    def _calc_hole_x_translate(self):
        translate = ((self.length - (self.inset * 2)) / 2)
        translate -= (self.hole_radius)
        translate -= self.hole_inset
        return translate

    def _calc_hole_y_translate(self):
        translate = ((self.width - (self.inset * 2)) / 2)
        translate -= (self.hole_radius)
        translate -= self.hole_inset
        return translate

    def _calc_hole_z_translate(self):
        return -1 * (self.height / 2 - self.hole_depth / 2)

    # Calculate how far the default
    # slot translation will be (This is ~85% of
    # the tile size)
    def _calc_slot_translation(self):
        return self.tile_size * 0.143

    # Calculate the slot radius/thickness.
    # This is ~90.5% of the tile size
    def _calc_slot_radius(self):
        return self.tile_size * 0.095

    # Calculate the length of mid size slots.
    # This is ~66.666% of the tile size
    def _calc_slot_length_md(self):
        return self.tile_size - (self.tile_size * 0.333)

    # Calculate the length of short size slots.
    # This is ~33.333% of the tile size
    def _calc_slot_length_sm(self):
        return self.tile_size - (self.tile_size * 0.666)

    def _make_roof_body(self):
        roof_body = cq.Workplane("XY").box(
            self._calc_final_length(),
            self._calc_final_width(),
            self.height
        )

        # if no chamfer/fillet, just return the new body
        if self.roof_chamfer == 0:
            self.roof_body = roof_body
            return

        # better to kill if this condition is met otherwise it fails silently.
        if self.roof_chamfer >= self.height:
            raise Exception(f"roof_chamfer {self.roof_chamfer} >= roof height {self.height}")

        if self.roof_operation.lower() == "chamfer":
            roof_body = (
                roof_body
                .faces(self.roof_chamfer_faces_selector)
                .edges(self.roof_chamfer_edges_selector)
                .chamfer(self.roof_chamfer)
            )
        elif self.roof_operation.lower() == "fillet":
            roof_body = (
                roof_body
                .faces(self.roof_chamfer_faces_selector)
                .edges(self.roof_chamfer_edges_selector)
                .fillet(self.roof_chamfer)
            )
        else:
            raise Exception("Unrecognied roof operation")

        self.roof_body = roof_body

    def _make_tiles(self):
        length = self._calc_tile_space_length()
        width = self._calc_tile_space_width()
        tile_space = self._calc_tile_spacing()
        slot_translate = self._calc_slot_translation()
        slot_radius = self._calc_slot_radius()
        slot_length_md = self._calc_slot_length_md()
        slot_length_sm = self._calc_slot_length_sm()

        tile = cq.Workplane("XY").box(
            self.tile_size,
            self.tile_size,
            self.tile_height
        )

        slot = (cq.Workplane("XY")
            .slot2D(self.tile_size, slot_radius)
            .extrude(self.tile_height * 2)
            .rotate((0, 0, 1), (0, 0, 0), 45)
            .translate((0, 0, 0 - (self.tile_height / 2))))

        slot2 = (cq.Workplane("XY")
            .slot2D(slot_length_md, slot_radius)
            .extrude(self.tile_height * 2)
            .rotate((0, 0, 1), (0, 0, 0), 45)
            .translate((0 - slot_translate, 0 - slot_translate, 0 - (self.tile_height / 2))))

        slot3 = (cq.Workplane("XY")
            .slot2D(slot_length_md, slot_radius)
            .extrude(self.tile_height * 2)
            .rotate((0, 0, 1), (0, 0, 0), 45)
            .translate((slot_translate, slot_translate, 0 - (self.tile_height / 2))))

        slot4 = (cq.Workplane("XY")
            .slot2D(slot_length_sm, slot_radius)
            .extrude(self.tile_height * 2)
            .rotate((0, 0, 1), (0, 0, 0), 45)
            .translate((0 - (slot_translate *2), 0 - (slot_translate * 2), 0 - (self.tile_height / 2))))

        slot5 = (cq.Workplane("XY")
            .slot2D(slot_length_sm, slot_radius)
            .extrude(self.tile_height * 2)
            .rotate((0, 0, 1), (0, 0, 0), 45)
            .translate((slot_translate * 2, slot_translate * 2, 0 - (self.tile_height / 2))))

        tile = (tile
                .cut(slot)
                .cut(slot2)
                .cut(slot3)
                .cut(slot4)
                .cut(slot5))

        columns = math_floor(width / (tile_space))
        rows = math_floor(length / (tile_space))
        tile_grid = grid.make_grid(
            part = tile,
            dim = [tile_space, tile_space],
            columns = columns,
            rows = rows
        )

        self.tiles = tile_grid.translate((0, 0, self._calc_tile_z_translate()))

    def __make_cut_hatches(self):
        int_length = self._calc_hatch_space_length()
        int_width = self._calc_hatch_space_width()

        #@todo discussion point - allow the parent bunker to inform the roof of interior room dimensions.
        # this could also be enabled by a feature flag
        if self.bunker_int_length and self.bunker_int_width:
            int_length = self.bunker_int_length
            int_width = self.bunker_int_width

        cut_length = self.hatch_length - self.hatch_cut_inset
        cut_width = self.hatch_width - self.hatch_cut_inset
        cut_height = self.wall_width + self.tile_height

        hatch_base_cut = (
            cq.Workplane("XY")
            .box(cut_length,cut_width,cut_height)
            .edges("|Z").chamfer(self.hatch_cut_chamfer)
            .faces("Z").edges().chamfer(3)
        )

        hatch_top_cut = (
            cq.Workplane("XY")
            .box(cut_length,cut_width,cut_height)
            .edges("|Z").chamfer(self.hatch_cut_chamfer)
            .faces("Z").edges().chamfer(3)
        )

        hatch_cut = (
            cq.Workplane("XY")
            .union(hatch_base_cut)
        ).translate((0,0,-1*(self.height/2)+(cut_height)/2 ))

        length_offset= self.panel_length - cut_length + self.panel_padding*2
        series = SeriesHelper()
        series.shape = hatch_cut
        series.outer_length = int_length
        series.outer_width = int_width
        series.length_offset = length_offset
        series.comp_length = self.panel_length
        series.comp_padding = self.panel_padding
        series.x_translate = (int_length / 2) - (cut_width/ 2)
        series.y_translate = (int_width / 2) - (cut_width / 2)
        series.z_translate = 0
        series.keep_list = self.hatch_panels
        series.make()

        self.cut_hatches = series.get_scene()

    def __make_hatches(self):
        int_length = self._calc_hatch_space_length()
        length_offset = self._calc_hatch_length_offset()
        int_width = self._calc_hatch_space_width()
        z_translate = self._calc_hatch_z_translate()

        #@todo discussion point - allow the parent bunker to inform the roof of interior room dimensions.
        # this could also be enabled by a feature flag
        if self.bunker_int_length and self.bunker_int_width:
            int_length = self.bunker_int_length
            int_width = self.bunker_int_width

        bp = Hatch()
        bp.length = self.hatch_length
        bp.width = self.hatch_width
        bp.height = self.hatch_height
        bp.hatch_radius = self.hatch_radius
        bp.make()

        hatch = bp.build()

        series = SeriesHelper()
        series.shape = hatch
        series.outer_length = int_length
        series.outer_width = int_width
        series.length_offset = length_offset
        series.comp_length = self.panel_length
        series.comp_padding = self.panel_padding
        series.x_translate = (int_length / 2) - (bp.width / 2)
        series.y_translate = (int_width / 2) - (bp.width / 2)
        series.z_translate = z_translate
        series.keep_list = self.hatch_panels
        series.make()

        self.hatches = series.get_scene()

    def make_hole_cuts(self):
        x_translate = self._calc_hole_x_translate()
        y_translate = self._calc_hole_y_translate()
        z_translate = self._calc_hole_z_translate()

        # fun quirk cylinder method signature is height then radius
        hole = cq.Workplane("XY").cylinder(
            self.hole_depth,
            self.hole_radius
        )

        holes = (
            cq.Workplane("XY")
            .union(hole.translate((x_translate, y_translate, z_translate)))
            .union(hole.translate((-1 * x_translate, y_translate, z_translate)))
            .union(hole.translate((-1 * x_translate, -1 * y_translate, z_translate)))
            .union(hole.translate((x_translate, -1 * y_translate, z_translate)))
        )

        self.holes = holes

    def make(self):
        super().make()

        self._make_roof_body()

        if self.render_tiles:
            self._make_tiles()

        if self.render_hatches:
            self.__make_hatches()

        if self.render_hatch_cuts:
            self.__make_cut_hatches()

        if self.cut_holes:
            self.make_hole_cuts()

    def build(self):
        super().build()

        tiles = self.render_tiles
        cut_tiles = self.__should_cut_tiles()

        result = (
            cq.Workplane("XY")
            .union(self.roof_body)
        )

        if tiles and self.tiles and cut_tiles == True:
            result = result.cut(self.tiles)
        elif tiles and self.tiles:
            result = result.union(self.tiles)

        if self.render_hatch_cuts and self.cut_hatches:
            result = result.cut(self.cut_hatches)

        if self.render_hatches and self.hatches:
            result = result.add(self.hatches)

        if self.cut_holes and self.holes:
            result = result.cut(self.holes)

        #return self.cut_hatches.union(self.tiles).add(self.hatches)
        #return self.holes
        return result
