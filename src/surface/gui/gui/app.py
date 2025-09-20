import atexit
import signal
from pathlib import Path
from threading import Thread

import rclpy.utilities
from ament_index_python import get_package_share_directory
from PyQt6.QtWidgets import QApplication, QWidget
from qt_material import apply_stylesheet, list_themes
from rclpy.executors import MultiThreadedExecutor

from gui.gui_node import GUINode


class App(QWidget):
    """Main app window."""

    app = QApplication([])

    def __init__(self, node_name: str) -> None:
        if not rclpy.utilities.ok():
            rclpy.init()
        super().__init__()
        self.node = GUINode(node_name)

        self.theme_param = self.node.declare_parameter('theme', '')
        self.resize(1850, 720)

        atexit.register(self._clean_shutdown)

    def run_gui(self) -> None:
        # Kills with Control + C
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        extra_blue = {
            'success': '#040444',
            'danger': '#040444',
            'warning': '#040444'
        }
        extra_watermelon = {
            'success': '#341616',
            'danger': '#341616',
            'warning': '#341616'
        }
        # Apply theme
        theme_param = self.theme_param.get_parameter_value().string_value

        base_theme = 'dark_blue.xml' if theme_param == 'dark' else 'light_blue.xml' if theme_param == 'light' else 'watermelon.xml'
        if base_theme == 'watermelon.xml':
            base_theme = Path(get_package_share_directory('gui')) / 'styles' / ('watermelon.xml')
            base_theme = base_theme.as_posix()

        extra = extra_watermelon if theme_param == 'watermelon' else extra_blue
        apply_stylesheet(self, theme=base_theme, extra=extra)

        executor = MultiThreadedExecutor()
        executor.add_node(self.node)
        Thread(target=executor.spin, daemon=True).start()

        self.show()

        # TODO: when the app closes it causes an error. Make not cause error?
        self.app.exec()

    def _clean_shutdown(self) -> None:
        if rclpy.utilities.ok():
            self.node.get_logger().info('Exiting.')
            self.node.destroy_node()
            rclpy.shutdown()
