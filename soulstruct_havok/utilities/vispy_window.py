from __future__ import annotations

__all__ = ["VispyWindow"]

import sys
import numpy as np

try:
    import vispy.color as vp_color
    from vispy import app, scene
except ModuleNotFoundError:
    # No `vispy`. Cannot use `VispyWindow`.
    VipsyWindow = None
else:

    class VispyWindow:

        def __init__(self, bgcolor="black"):
            self.canvas = scene.SceneCanvas(size=(1200, 800), keys="interactive", bgcolor=vp_color.Color(bgcolor))
            self.view = self.canvas.central_widget.add_view()  # type: scene.ViewBox
            self.view.camera = scene.TurntableCamera(up='z', fov=60)  # TODO: Try "y" as up

        @property
        def camera(self) -> scene.TurntableCamera:
            return self.view.camera

        def set_camera_center(self, point):
            self.camera.center = point

        def add_markers(
            self,
            points: np.ndarray,
            edge_width=0,
            edge_color=(0, 0, 0, 1),
            face_color=(1, 1, 1, 1),
            size=5,
            symbol="o",
        ) -> scene.Markers:
            markers = scene.Markers()
            markers.set_data(
                points,
                edge_width=edge_width,
                edge_color=edge_color,
                face_color=face_color,
                size=size,
            )
            markers.symbol = symbol
            self.view.add(markers)
            return markers

        def add_arrow(
            self,
            line_points,
            arrows,
            color="red",
            connect="strip",
        ):
            arrow = scene.Arrow(line_points, arrows=arrows, connect=connect, color=color)
            self.view.add(arrow)
            return arrow

        def add_line(
            self,
            line_points: np.ndarray,
            line_color=(1, 1, 1, 1),
            width=1,
            connect="strip",
            method="gl",
        ) -> scene.Line:
            line = scene.Line(line_points, color=line_color, width=width, connect=connect, method=method)
            self.view.add(line)
            return line

        def add_gridlines(self, grid_color=(1, 1, 1, 0.4)):
            grid = scene.visuals.GridLines(color=grid_color)
            self.view.add(grid)
            return grid

        def add_axes(self):
            xax = scene.Axis(
                pos=[[0, 0], [1, 0]],
                tick_direction=(0, -1),
                axis_color='r',
                tick_color='r',
                text_color='r',
                font_size=16,
                parent=self.view.scene,
            )
            yax = scene.Axis(
                pos=[[0, 0], [0, 1]],
                tick_direction=(-1, 0),
                axis_color='g',
                tick_color='g',
                text_color='g',
                font_size=16,
                parent=self.view.scene,
            )
            zax = scene.Axis(
                pos=[[0, 0], [-1, 0]],
                tick_direction=(0, -1),
                axis_color='b',
                tick_color='b',
                text_color='b',
                font_size=16,
                parent=self.view.scene,
            )

            # TODO: Control?
            zax.transform = scene.transforms.MatrixTransform()  # its acutally an inverted xaxis
            zax.transform.rotate(90, (0, 1, 0))  # rotate cw around yaxis
            zax.transform.rotate(-45, (0, 0, 1))  # tick direction towards (-1,-1)

            return xax, yax, zax

        def show(self):
            self.canvas.show()

        @staticmethod
        def run():
            app.run()


def test():
    window = VispyWindow()
    points = np.array([[1, 2, 3], [4, 5, 6]])
    window.add_markers(points)
    window.add_line(points)
    window.add_axes()
    window.show()
    if sys.flags.interactive == 0:
        window.run()


if __name__ == '__main__':
    test()
