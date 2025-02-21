# Copyright 2022 James Adams
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
from cadqueryhelper import shape

def init_bunker_params(self):
    self.render_panel_details=True
    self.render_cut_panels=True
    self.panel_length = 28
    self.panel_width = 6
    self.panel_padding = 4

    self.arch_padding_top = 3
    self.arch_padding_sides = 3
    self.arch_inner_height = 6
    self.inner_arch_top = 5
    self.inner_arch_sides = 4

    self.panels = None
    self.cut_panels = None

def make_cut_panels(self):
    height = self.height
    p_length = self.panel_length
    p_width = self.panel_width
    padding = self.panel_padding
    p_height = height - padding

    cut_panel = (
    cq.Workplane("XY")
        .box(p_length, p_width, p_height)
        .translate((0,-1*(p_width/2),1*(p_height/2)))
        .rotate((1,0,0),(0,0,0),self.angle-90)
        .translate((0,0,-1*(height/2)))
    )

    x_translate = self.length/2
    y_translate = self.width/2
    self.cut_panels = self.make_series(cut_panel, length_offset=self.panel_padding*2, x_translate=x_translate,y_translate=y_translate, z_translate=0)

def arch_detail(self):
    height = self.height
    p_length = self.panel_length
    p_width = self.panel_width
    padding = self.panel_padding

    panel_outline = cq.Workplane("XY").box(p_length, p_width, height - padding)
    arch = shape.arch_pointed(p_length+self.arch_padding_sides, p_width/2 , height - padding + self.arch_padding_top, ((height - padding)/2) + self.arch_inner_height).translate((0,-1*(p_width/4),0))
    inner_arch = shape.arch_pointed(p_length + self.arch_padding_sides - self.inner_arch_sides, p_width , height - padding + self.arch_padding_top - self.inner_arch_top, ((height - padding)/2) + self.arch_inner_height - self.inner_arch_sides)
    inner_inner_arch = shape.arch_pointed(
        p_length - self.inner_arch_sides,
        p_width/2,
        height - padding - self.inner_arch_top,
        ((height - padding)/2) + self.arch_inner_height - self.inner_arch_sides
    ).translate((0,(p_width/4),-1.5))

    panel_back = cq.Workplane("XY").box(p_length, p_width/2, height - padding).translate((0,(p_width/4),0))
    panel_detail = cq.Workplane("XY").add(panel_back).add(arch)
    inside_arch = panel_back.cut(inner_inner_arch)
    panel = panel_outline.intersect(panel_detail).cut(inner_arch).add(inside_arch)
    return panel

def make_detail_panels(self):
    height = self.height
    p_length = self.panel_length
    p_width = self.panel_width
    padding = self.panel_padding
    p_height = height - padding

    detail_panel = (
        arch_detail(self)
        .translate((0,1*(p_width/2),1*(p_height/2)))
        .rotate((0,0,1),(0,0,0),180)
        .rotate((1,0,0),(0,0,0),self.angle-90)
        .translate((0,0,-1*(height/2)))
    )

    x_translate = self.length/2
    y_translate = self.width/2
    self.panels = self.make_series(detail_panel, length_offset=self.panel_padding*2, x_translate=x_translate,y_translate=y_translate, z_translate=0)
