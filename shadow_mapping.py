import math
from pathlib import Path
from pyrr import Matrix44, matrix44, Vector3

import moderngl
import moderngl_window
from moderngl_window import geometry

from base import CameraWindow
import config
import skymap

class ShadowMapping(CameraWindow):
    title = "Shadow Mapping"
    resource_dir = "./"


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera.projection.update(near=1, far=200)
        self.wnd.mouse_exclusivity = True
        self.camera.set_position(9,34,32)
        self.camera.set_rotation(-105,-43)

        offscreen_size = 1024, 1024
        self.offscreen_depth = self.ctx.depth_texture(offscreen_size)
        self.offscreen_depth.compare_func = ''
        self.offscreen_depth.repeat_x = False
        self.offscreen_depth.repeat_y = False
        self.offscreen_color = self.ctx.texture(offscreen_size, 4)

        self.offscreen = self.ctx.framebuffer(
            color_attachments=[self.offscreen_color],
            depth_attachment=self.offscreen_depth,
        )

        loaded_floor = self.load_scene('objects/flat_ground.obj')
        self.floor = loaded_floor.root_nodes[0].mesh.vao

        loaded_object = self.load_scene(config.object_filename)
        self.sphere = loaded_object.root_nodes[0].mesh.vao

        self.sun = geometry.sphere(radius=1.0)

        self.cube = geometry.cube(size=(200, 200, 200))
        if config.skybox_filename == 'default':
            self.texture = self.load_texture_cube(
                neg_x='images/posx.jpg',
                neg_y='images/negy.jpg',
                neg_z='images/negz.jpg',
                pos_x='images/negx.jpg',
                pos_y='images/posy.jpg',
                pos_z='images/posz.jpg',
                flip_x=True,
            )

        else:
            skybox_list = skymap.processImage(config.skybox_filename)
            self.texture = self.load_texture_cube(
                neg_x=skybox_list[1],
                neg_y=skybox_list[5],
                neg_z=skybox_list[2],
                pos_x=skybox_list[3],
                pos_y=skybox_list[0],
                pos_z=skybox_list[4],
                flip_x=True,
            )

        self.skybox_prog = self.load_program('opengl/skybox.glsl')
        self.basic_light = self.load_program('opengl/directional_light.glsl')
        self.basic_light['shadowMap'].value = 0
        self.basic_light['color'].value = 1.0, 1.0, 1.0, 1.0
        self.shadowmap_program = self.load_program('opengl/shadowmap.glsl')
        #self.texture_prog = self.load_program('opengl/texture.glsl')
        #self.texture_prog['texture0'].value = 0
        self.sun_prog = self.load_program('opengl/cube_simple.glsl')
        self.sun_prog['color'].value = 1, 1, 0, 1
        self.lightpos = Vector3((0, 0, 0), dtype='f4')

    def render_skybox(self):
        self.wnd.use()
        self.ctx.cull_face = 'front'
        cam = self.camera.matrix
        cam[3][0] = 0
        cam[3][1] = 0
        cam[3][2] = 0

        self.texture.use(location=0)
        self.skybox_prog['m_proj'].write(self.camera.projection.matrix)
        self.skybox_prog['m_camera'].write(cam)
        self.cube.render(self.skybox_prog)
        self.ctx.cull_face = 'back'

    def render(self, time, frametime):
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        self.lightpos = Vector3((math.sin(time) * 21, 12, math.cos(time) * 21), dtype='f4')
        ground_pos = Vector3((0, 0, 0), dtype='f4')
        object_pos = Vector3((0, 0, 0), dtype='f4')

        self.offscreen.clear()
        self.offscreen.use()

        depth_projection = Matrix44.orthogonal_projection(-40, 40, -40, 40, -40, 80, dtype='f4')

        depth_view = Matrix44.look_at(self.lightpos, object_pos, (0, 1, 0), dtype='f4')
        depth_mvp_object = depth_projection * depth_view# * Matrix44.from_translation(object_pos, dtype='f4')
        depth_mvp_ground = depth_projection * depth_view# * Matrix44.from_translation(ground_pos, dtype='f4')

        if config.if_shadow_map:
            self.shadowmap_program['vp'].write(depth_mvp_object)
            self.shadowmap_program['model'].write(Matrix44.from_translation(object_pos, dtype='f4'))
            self.sphere.render(self.shadowmap_program)

            self.shadowmap_program['vp'].write(depth_mvp_ground)
            self.shadowmap_program['model'].write(Matrix44.from_translation(ground_pos, dtype='f4'))
            self.floor.render(self.shadowmap_program)


        self.wnd.use()

        if config.if_bias:
            self.basic_light['bias'] = 0.005
        else:
            self.basic_light['bias'] = 0.000

        self.basic_light['ifpoissonDisk'] = False

        if config.ifpoissonDisk:
            self.basic_light['ifpoissonDisk'] = True

        self.basic_light['numberofsamples'] = config.numberofsamples

        self.basic_light['m_proj'].write(self.camera.projection.matrix)
        self.basic_light['m_camera'].write(self.camera.matrix)
        bias_matrix = Matrix44(
            [[0.5, 0.0, 0.0, 0.0],
             [0.0, 0.5, 0.0, 0.0],
             [0.0, 0.0, 0.5, 0.0],
             [0.5, 0.5, 0.5, 1.0]],
            dtype='f4',
        )

        self.basic_light['m_shadow_bias'].write(matrix44.multiply(depth_mvp_ground, bias_matrix))
        self.basic_light['lightDir'].write(self.lightpos)
        self.offscreen_depth.use(location=0)

        self.basic_light['m_model'].write(Matrix44.from_translation(ground_pos, dtype='f4'))
        self.floor.render(self.basic_light)

        self.basic_light['m_shadow_bias'].write(matrix44.multiply(depth_mvp_object, bias_matrix))
        self.basic_light['m_model'].write(Matrix44.from_translation(object_pos, dtype='f4'))
        self.sphere.render(self.basic_light)

        self.sun_prog['m_proj'].write(self.camera.projection.matrix)
        self.sun_prog['m_camera'].write(self.camera.matrix)
        self.sun_prog['m_model'].write(Matrix44.from_translation(self.lightpos, dtype='f4'))
        self.sun.render(self.sun_prog)

        self.render_skybox()

def start(obj,skybox):
    config.object_filename = obj
    config.skybox_filename = skybox
    moderngl_window.run_window_config(ShadowMapping)

if __name__ == "__main__":
    config.object_filename = "objects/cone.obj"
    config.skybox_filename = "images/pngwing.com.png"
    moderngl_window.run_window_config(ShadowMapping)